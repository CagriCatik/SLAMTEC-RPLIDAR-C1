from pathlib import Path
import numpy as np
from .models import Scan, UNKNOWN, HIT
from .storage import load_scan


class DemoSource:
    """Static ray-cast geometry; independent known SE(2) sensor trajectory."""
    def __init__(self, count=30, rays=500, moving=True):
        if type(count) is not int or count < 1 or type(rays) is not int or rays < 16:
            raise ValueError("Positive count and at least 16 rays required")
        self.count, self.rays, self.moving = count, rays, moving

    @staticmethod
    def pose_at(index):
        return np.array([.015*index, .006*np.sin(index*.3), .004*index])

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def __iter__(self):
        corners = np.array([[-4, -3], [4, -3], [4, 3], [-4, 3]])
        box = np.array([[1, -.6], [1.5, -.6], [1.5, .1], [1, .1]])
        segments = [(a, b) for polygon in (corners, box) for a, b in zip(polygon, np.roll(polygon, -1, axis=0))]
        segments += [(np.array([-2., .8]), np.array([-.8, 1.9]))]
        angle = np.linspace(-np.pi, np.pi, self.rays, endpoint=False)
        for index in range(min(self.count, 61)):
            pose = self.pose_at(index) if self.moving else np.zeros(3)
            direction = np.column_stack((np.cos(angle+pose[2]), np.sin(angle+pose[2])))
            distance = np.full(self.rays, np.inf)
            for a, b in segments:
                edge, delta = b-a, a-pose[:2]
                cross = direction[:, 0]*edge[1]-direction[:, 1]*edge[0]
                safe = np.where(np.abs(cross) > 1e-10, cross, np.nan)
                t = (delta[0]*edge[1]-delta[1]*edge[0])/safe
                u = (delta[0]*direction[:, 1]-delta[1]*direction[:, 0])/safe
                valid = (t > .05) & (u >= 0) & (u <= 1)
                distance = np.minimum(distance, np.where(valid, t, np.inf))
            valid = np.isfinite(distance) & (distance <= 12.)
            measured = np.where(valid, distance+np.random.default_rng(index).normal(0, .001, self.rays), np.nan)
            status = np.where(valid, HIT, UNKNOWN).astype(np.uint8)
            status[::97] = UNKNOWN
            yield Scan(angle.copy(), measured, status, index, index*.1,
                       metadata={"source": "ray_cast_demo", "full_revolution": True,
                                 "representation": "native_uniform_demo", "per_point_time": "unavailable"},
                       quality=np.full(self.rays, 100, np.uint8))


class ReplaySource:
    def __init__(self, path):
        path = Path(path)
        self.paths = sorted(path.glob("scan_*.npz")) if path.is_dir() else [path]
        if not self.paths or any(not p.is_file() for p in self.paths):
            raise ValueError("No scan snapshots found")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def __iter__(self):
        return (load_scan(path) for path in self.paths)
