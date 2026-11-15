from dataclasses import dataclass
import numpy as np
from .geometry import points, transform, validate_transform
from .models import HIT, CLEAR
from .odometry import MatchConfig, match_scans


@dataclass(frozen=True)
class GridConfig:
    resolution_m: float = .05
    width: int = 240
    height: int = 240
    origin_x: float = -6.
    origin_y: float = -6.
    free_log_odds: float = -.4
    occupied_log_odds: float = .85

    def __post_init__(self):
        if any(type(v) is not int or v < 1 for v in (self.width, self.height)) or self.width*self.height > 1000000:
            raise ValueError("Grid must have 1..1,000,000 cells")
        scalars = (self.resolution_m, self.origin_x, self.origin_y, self.free_log_odds, self.occupied_log_odds)
        if any(type(v) not in (int, float) for v in scalars) or not np.isfinite(scalars).all():
            raise ValueError("Finite grid settings required")
        if self.resolution_m <= 0 or self.free_log_odds >= 0 or self.occupied_log_odds <= 0:
            raise ValueError("Invalid resolution or inverse sensor model")


def ray_cells(start, end):
    x, y = map(int, start); end_x, end_y = map(int, end)
    dx, dy = abs(end_x-x), abs(end_y-y)
    sx, sy = (1 if x < end_x else -1), (1 if y < end_y else -1)
    error = dx-dy
    while True:
        yield x, y
        if (x, y) == (end_x, end_y):
            return
        double = 2*error
        if double > -dy:
            error -= dy; x += sx
        if double < dx:
            error += dx; y += sy


class OccupancyGrid:
    def __init__(self, config=None):
        self.config = config or GridConfig()
        shape = (self.config.height, self.config.width)
        self.log_odds = np.zeros(shape, np.float32)
        self.seen = np.zeros(shape, bool)

    def cell(self, xy):
        cfg = self.config
        return np.floor((np.asarray(xy)-[cfg.origin_x, cfg.origin_y])/cfg.resolution_m).astype(int)

    def inside(self, cell):
        x, y = cell
        return 0 <= x < self.config.width and 0 <= y < self.config.height

    def integrate(self, scan, pose):
        pose = validate_transform(pose)
        start = self.cell(pose[:2, 2])
        if not self.inside(start):
            raise ValueError("sensor_outside_grid")
        free, occupied = set(), set()
        valid = (scan.status == HIT) | (scan.status == CLEAR)
        xy = np.column_stack((scan.ranges[valid]*np.cos(scan.angles[valid]), scan.ranges[valid]*np.sin(scan.angles[valid])))
        ends = self.cell(transform(xy, pose))
        for end, status in zip(ends, scan.status[valid]):
            endpoint = tuple(end)
            for cell in ray_cells(start, end):
                if not self.inside(cell):
                    break
                if cell == endpoint and status == HIT:
                    occupied.add(cell)
                else:
                    free.add(cell)
        free -= occupied
        if free:
            candidates = np.array(list(free))
            center = np.array([self.config.origin_x, self.config.origin_y])+(candidates+.5)*self.config.resolution_m
            known = np.linalg.norm(center-pose[:2, 2], axis=1)-self.config.resolution_m/np.sqrt(2) >= scan.range_min
            free = set(map(tuple, candidates[known]))  # preserve unobserved near-field blind zone
        for cells, delta in ((free, self.config.free_log_odds), (occupied, self.config.occupied_log_odds)):
            if cells:
                x, y = np.array(list(cells)).T
                self.log_odds[y, x] = np.clip(self.log_odds[y, x]+delta, -4., 4.)
                self.seen[y, x] = True

    def states(self):
        """ROS convention -1 unknown, 0 free, 100 occupied; uncertain remains unknown."""
        result = np.full(self.log_odds.shape, -1, np.int8)
        result[self.seen & (self.log_odds <= -.2)] = 0
        result[self.seen & (self.log_odds >= .6)] = 100
        return result


class LocalMapper:
    def __init__(self, grid_config=None, match_config=None, matcher=None):
        self.grid = OccupancyGrid(grid_config)
        self.match_config = match_config or MatchConfig()
        self.matcher = matcher or match_scans
        self.previous, self.pose, self.lost = None, np.eye(3), False

    def update(self, scan):
        entry = {"sequence": scan.sequence, "time_s": scan.time_s, "domain": scan.domain,
                 "sensor_to_world": None, "status": "lost", "diagnostic": {}}
        if self.lost:
            return dict(entry, diagnostic={"reason": "tracking_lost_latched"})
        pose = self.pose.copy()
        if len(points(scan)[0]) < self.match_config.min_points:
            diagnostic = {"reason": "insufficient_points"}
        elif self.previous is None:
            diagnostic = {"reason": "initialized"}
        elif (scan.domain != self.previous.domain or scan.time_s <= self.previous.time_s
              or scan.frame_id != self.previous.frame_id):
            diagnostic = {"reason": "time_or_frame_discontinuity"}
        else:
            relative, diagnostic = self.matcher(self.previous, scan, self.match_config)
            if relative is not None:
                try:
                    pose = self.pose@np.linalg.inv(validate_transform(relative))
                except (ValueError, np.linalg.LinAlgError):
                    diagnostic = {"reason": "invalid_transform"}
            elif diagnostic.get("reason") == "accepted":
                diagnostic = {"reason": "invalid_transform"}
        okay = diagnostic["reason"] in ("initialized", "accepted")
        if okay:
            try:
                self.grid.integrate(scan, pose)
            except ValueError as exc:
                okay, diagnostic = False, {"reason": str(exc)}
        if not okay:
            self.lost = True
            return dict(entry, diagnostic=diagnostic)
        self.previous, self.pose = scan, pose
        return dict(entry, sensor_to_world=pose.tolist(), status="initialized" if diagnostic["reason"] == "initialized" else "tracking", diagnostic=diagnostic)
