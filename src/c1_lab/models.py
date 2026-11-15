from dataclasses import dataclass, field
import numpy as np

UNKNOWN, HIT, CLEAR = 0, 1, 2


@dataclass
class Scan:
    angles: np.ndarray
    ranges: np.ndarray
    status: np.ndarray
    sequence: int
    time_s: float
    domain: str = "synthetic"
    frame_id: str = "laser"
    range_min: float = .05
    range_max: float = 12.
    metadata: dict = field(default_factory=dict)
    quality: np.ndarray | None = None
    raw_angle_q14: np.ndarray | None = None
    raw_distance_q2: np.ndarray | None = None
    flags: np.ndarray | None = None

    def __post_init__(self):
        n = len(self.angles)
        if self.angles.shape != (n,) or self.ranges.shape != (n,) or self.status.shape != (n,):
            raise ValueError("Scan arrays must have matching one-dimensional shapes")
        if not np.isfinite(self.angles).all() or not np.isin(self.status, [UNKNOWN, HIT, CLEAR]).all():
            raise ValueError("Invalid angle or return status")
        if not np.isfinite([self.time_s, self.range_min, self.range_max]).all() or not 0 < self.range_min < self.range_max:
            raise ValueError("Invalid timestamp or range limits")
        if type(self.sequence) is not int or self.sequence < 0 or not isinstance(self.domain, str) or not self.domain:
            raise ValueError("Invalid scan identity")
        measured = self.status != UNKNOWN
        if not np.isfinite(self.ranges[measured]).all() or np.any(self.ranges[measured] < self.range_min) or np.any(self.ranges[measured] > self.range_max):
            raise ValueError("Known returns must have finite distances within range limits")
        for array in (self.quality, self.raw_angle_q14, self.raw_distance_q2, self.flags):
            if array is not None and array.shape != (n,):
                raise ValueError("Optional scan array has wrong shape")
        if not isinstance(self.metadata, dict):
            raise ValueError("Scan metadata must be an object")
