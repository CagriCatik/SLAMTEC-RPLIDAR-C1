from dataclasses import replace
import numpy as np
from .geometry import points, wrap
from .models import HIT, CLEAR, UNKNOWN


def filter_scan(scan, minimum=None, maximum=None, min_quality=None):
    low = scan.range_min if minimum is None else minimum
    high = scan.range_max if maximum is None else maximum
    if not np.isfinite([low, high]).all() or not scan.range_min <= low < high <= scan.range_max:
        raise ValueError("Filter bounds must be inside the scan range")
    status = scan.status.copy()
    reject = (scan.ranges < low) | (scan.ranges > high) | ~np.isfinite(scan.ranges)
    if min_quality is not None:
        if type(min_quality) not in (int, float) or not np.isfinite(min_quality) or not 0 <= min_quality <= 255:
            raise ValueError("Raw quality threshold must be finite and in [0,255]")
        if scan.quality is None:
            raise ValueError("No quality channel available")
        reject |= scan.quality < min_quality
    status[reject] = UNKNOWN
    return replace(scan, status=status, metadata=dict(scan.metadata, filter_bounds_m=[low, high]))


def temporal_median(scans):
    if not scans:
        raise ValueError("Temporal filter needs scans")
    first, last = scans[0], scans[-1]
    if any(s.domain != first.domain or not np.array_equal(s.angles, first.angles) for s in scans):
        raise ValueError("Temporal filter needs identical angular grids and time domains")
    if any(b.time_s <= a.time_s for a, b in zip(scans, scans[1:])):
        raise ValueError("Temporal filter requires increasing timestamps")
    known = np.all([s.status == HIT for s in scans], axis=0)
    ranges = last.ranges.copy()
    ranges[known] = np.median(np.array([s.ranges for s in scans])[:, known], axis=0)
    return replace(last, ranges=ranges, status=np.where(known, HIT, UNKNOWN).astype(np.uint8),
                   metadata=dict(last.metadata, temporal_filter="median_all_frames_hit; no motion compensation"))


def angular_bins(scan, count=360):
    """Explicit derived grid: nearest HIT in each bin, no interpolation or gap filling."""
    if type(count) is not int or count < 4:
        raise ValueError("At least four bins required")
    result = np.full(count, np.nan)
    indices = np.floor((wrap(scan.angles)+np.pi)/(2*np.pi)*count).astype(int) % count
    for index, distance, status in zip(indices, scan.ranges, scan.status):
        if status == HIT and (not np.isfinite(result[index]) or distance < result[index]):
            result[index] = distance
    return {"angles": (-np.pi+(np.arange(count)+.5)*2*np.pi/count).tolist(),
            "ranges": [float(r) if np.isfinite(r) else None for r in result],
            "representation": "derived_nearest_hit_bins; native scan unchanged"}


def clusters(scan, gap_m=.3, max_angle_gap=.06, minimum=3):
    if gap_m <= 0 or max_angle_gap <= 0 or minimum < 1:
        raise ValueError("Invalid cluster parameters")
    order = np.argsort(wrap(scan.angles), kind="stable")
    angle = wrap(scan.angles[order])
    xy = np.column_stack((scan.ranges[order]*np.cos(angle), scan.ranges[order]*np.sin(angle)))
    groups, current = [], []
    for position, index in enumerate(order):
        if scan.status[index] != HIT:
            if current:
                groups.append(current)
            current = []
            continue
        linked = (position > 0 and bool(current) and 1e-8 < angle[position]-angle[position-1] <= max_angle_gap
                  and np.linalg.norm(xy[position]-xy[position-1]) <= gap_m)
        if current and not linked:
            groups.append(current)
            current = []
        current.append(int(index))
    if current:
        groups.append(current)
    if (len(groups) > 1 and scan.metadata.get("full_revolution") is True and len(order)
            and scan.status[order[0]] == HIT and scan.status[order[-1]] == HIT
            and 1e-8 < (angle[0]-angle[-1]) % (2*np.pi) <= max_angle_gap
            and np.linalg.norm(xy[0]-xy[-1]) <= gap_m):
        groups[0] = groups[-1]+groups[0]
        groups.pop()
    return [np.array(group) for group in groups if len(group) >= minimum]


def lines(xy, threshold=.025, minimum=8, max_lines=12, seed=0):
    xy = np.asarray(xy, dtype=float)
    if xy.ndim != 2 or xy.shape[1] != 2 or not np.isfinite(xy).all():
        raise ValueError("Finite Nx2 line points required")
    if threshold <= 0 or minimum < 3 or max_lines < 1:
        raise ValueError("Invalid line parameters")
    remaining = np.arange(len(xy)); result = []
    rng = np.random.default_rng(seed)
    while len(remaining) >= minimum and len(result) < max_lines:
        data = xy[remaining]; best = np.zeros(len(data), bool)
        for _ in range(80):
            a, b = data[rng.choice(len(data), 2, replace=False)]
            tangent = b-a; length = np.linalg.norm(tangent)
            if length < 1e-8:
                continue
            normal = np.array([-tangent[1], tangent[0]])/length
            mask = np.abs((data-a)@normal) <= threshold
            if mask.sum() > best.sum():
                best = mask
        if best.sum() < minimum:
            break
        fitted = data[best]; center = fitted.mean(axis=0)
        _, singular, vt = np.linalg.svd(fitted-center, full_matrices=False)
        if singular[0] < 1e-8:
            break
        tangent, normal = vt[0], vt[-1]
        rho = float(center@normal)
        if rho < 0:
            normal, rho = -normal, -rho
        projection = (fitted-center)@tangent
        ends = np.array([center+projection.min()*tangent, center+projection.max()*tangent])
        result.append({"normal": normal.tolist(), "rho_m": rho, "ends_m": ends.tolist(),
                       "length_m": float(np.ptp(projection)), "point_indices": remaining[best].tolist(),
                       "rmse_m": float(np.sqrt(np.mean((fitted@normal-rho)**2)))})
        remaining = remaining[~best]
    return result


def corners(segments, endpoint_tolerance=.15):
    result = []
    for i, a in enumerate(segments):
        for j, b in enumerate(segments[i+1:], i+1):
            matrix = np.array([a["normal"], b["normal"]])
            if abs(np.linalg.det(matrix)) < np.sin(np.deg2rad(20)):
                continue
            point = np.linalg.solve(matrix, [a["rho_m"], b["rho_m"]])
            if all(min(np.linalg.norm(point-np.array(end)) for end in line["ends_m"]) <= endpoint_tolerance for line in (a, b)):
                if not any(np.linalg.norm(point-np.array(c["xy_m"])) < .05 for c in result):
                    result.append({"xy_m": point.tolist(), "line_indices": [i, j], "hypothesis": "line_intersection_near_endpoints"})
    return result


def sector(scan, center=0., width=np.pi/2):
    if not np.isfinite([center, width]).all() or not 0 < width <= 2*np.pi:
        raise ValueError("Invalid sector")
    selected = np.abs(wrap(scan.angles-center)) <= width/2
    hit = selected & (scan.status == HIT)
    n = int(selected.sum())
    return {"rays": n, "nearest_hit_m": float(scan.ranges[hit].min()) if hit.any() else None,
            "unknown_fraction": float(np.sum(selected & (scan.status == UNKNOWN))/n) if n else None,
            "explicit_clear_fraction": float(np.sum(selected & (scan.status == CLEAR))/n) if n else None}


def inspect_scan(scan):
    xy, original = points(scan)
    segments = lines(xy)
    group_reports = []
    for group in clusters(scan):
        cloud = np.column_stack((scan.ranges[group]*np.cos(scan.angles[group]), scan.ranges[group]*np.sin(scan.angles[group])))
        group_reports.append({"point_indices": group.tolist(), "center_m": cloud.mean(axis=0).tolist(),
                              "visible_extent_m": np.ptp(cloud, axis=0).tolist()})
    return {"inspection_schema": 1, "sequence": scan.sequence, "time_s": scan.time_s, "domain": scan.domain,
            "hit_fraction": float(np.mean(scan.status == HIT)) if len(scan.status) else 0.,
            "clusters": group_reports, "lines": segments, "corners": corners(segments),
            "line_point_to_scan_index": original.tolist(), "front_sector": sector(scan),
            "limits": "Visible 2D contours and geometric hypotheses; no object class or height."}
