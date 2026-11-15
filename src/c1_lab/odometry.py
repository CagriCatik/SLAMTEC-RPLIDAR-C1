from dataclasses import dataclass
import numpy as np
from .geometry import points, pose_matrix, transform, wrap


@dataclass(frozen=True)
class MatchConfig:
    correspondence_m: float = .3
    max_rmse_m: float = .035
    min_overlap: float = .4
    min_points: int = 30
    max_translation_m: float = .2
    max_rotation_rad: float = .15
    max_condition: float = 10000.
    iterations: int = 35

    def __post_init__(self):
        for name in ("correspondence_m", "max_rmse_m", "max_translation_m", "max_rotation_rad", "max_condition"):
            value = getattr(self, name)
            if type(value) not in (int, float) or not np.isfinite(value) or value <= 0:
                raise ValueError(f"Invalid {name}")
        if type(self.min_overlap) not in (int, float) or not 0 < self.min_overlap <= 1:
            raise ValueError("Invalid overlap")
        for name in ("min_points", "iterations"):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(f"Invalid {name}")
        if self.min_points < 6 or self.max_condition <= 1:
            raise ValueError("Insufficient matching constraints")


def _normals(scan):
    order = np.argsort(wrap(scan.angles), kind="stable")
    positions = np.flatnonzero(scan.status[order] == 1)
    indices = order[positions]
    angle = wrap(scan.angles[indices])
    xy = np.column_stack((scan.ranges[indices]*np.cos(angle), scan.ranges[indices]*np.sin(angle)))
    normals = np.zeros_like(xy)
    if len(xy) < 3:
        return xy, normals
    delta = xy[2:]-xy[:-2]
    length = np.linalg.norm(delta, axis=1)
    gaps = np.diff(angle)
    valid = ((length > .001) & (length < .5) & (np.diff(positions)[:-1] == 1) & (np.diff(positions)[1:] == 1)
             & (gaps[:-1] > 1e-8) & (gaps[1:] > 1e-8) & (gaps[:-1] < .06) & (gaps[1:] < .06))
    normals[1:-1] = np.divide(np.column_stack((-delta[:, 1], delta[:, 0])), length[:, None],
                              out=np.zeros_like(delta), where=valid[:, None])
    return xy, normals


def _pairs(source, matrix, target, normals, cfg):
    p = transform(source, matrix)
    # Chunking bounds memory independently of scan density.
    nearest = np.concatenate([np.argmin(np.sum((chunk[:, None, :]-target[None, :, :])**2, axis=2), axis=1)
                              for chunk in np.array_split(p, max(1, int(np.ceil(len(p)/128))))])
    q, n = target[nearest], normals[nearest]
    valid = (np.linalg.norm(p-q, axis=1) <= cfg.correspondence_m) & (np.linalg.norm(n, axis=1) > .5)
    return p[valid], q[valid], n[valid]


def match_scans(previous, current, config=None):
    cfg = config or MatchConfig()
    source, _ = points(previous); target, normals = _normals(current)
    if min(len(source), len(target)) < cfg.min_points:
        return None, {"reason": "insufficient_points"}
    matrix = np.eye(3); converged = False; info = {}
    for iteration in range(cfg.iterations):
        p, q, n = _pairs(source, matrix, target, normals, cfg)
        info = {"correspondences": len(p), "overlap": len(p)/len(source), "iterations": iteration+1}
        if len(p) < cfg.min_points or info["overlap"] < cfg.min_overlap:
            return None, dict(info, reason="insufficient_overlap")
        residual = np.sum((p-q)*n, axis=1)
        jacobian = np.column_stack((n, -p[:, 1]*n[:, 0]+p[:, 0]*n[:, 1]))
        weight = np.minimum(1., .02/np.maximum(np.abs(residual), 1e-12))
        hessian = jacobian.T@(weight[:, None]*jacobian)
        eigen = np.linalg.eigvalsh(hessian)
        if eigen[0] <= 0 or eigen[-1]/eigen[0] > cfg.max_condition:
            return None, dict(info, reason="degenerate_geometry")
        try:
            delta = np.linalg.solve(hessian, -jacobian.T@(weight*residual))
        except np.linalg.LinAlgError:
            return None, dict(info, reason="numerical_failure")
        matrix = pose_matrix(delta)@matrix
        if np.linalg.norm(delta) < 2e-4:
            converged = True
            break
    p, q, n = _pairs(source, matrix, target, normals, cfg)
    if len(p) < cfg.min_points or len(p)/len(source) < cfg.min_overlap:
        return None, dict(info, reason="insufficient_final_overlap")
    rmse = float(np.sqrt(np.mean(np.sum((p-q)*n, axis=1)**2)))
    info.update(rmse_m=rmse, translation_m=float(np.linalg.norm(matrix[:2, 2])),
                rotation_rad=float(abs(np.arctan2(matrix[1, 0], matrix[0, 0]))))
    if not converged:
        return None, dict(info, reason="iteration_limit")
    if rmse > cfg.max_rmse_m:
        return None, dict(info, reason="residual_too_large")
    if info["translation_m"] > cfg.max_translation_m or info["rotation_rad"] > cfg.max_rotation_rad:
        return None, dict(info, reason="motion_gate")
    return matrix, dict(info, reason="accepted")
