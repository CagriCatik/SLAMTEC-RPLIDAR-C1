from dataclasses import asdict
import json
from pathlib import Path
import time
import numpy as np
from .geometry import points
from .landmarks import LandmarkMap
from .mapping import GridConfig, LocalMapper
from .odometry import MatchConfig
from .processing import inspect_scan
from .storage import fingerprint, load_scan, save_scan, write_json, write_csv


def settings(path=None):
    if path is None:
        return MatchConfig(), GridConfig()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data)-{"matching", "grid"}:
        raise ValueError("Config supports only matching and grid sections")
    try:
        return MatchConfig(**data.get("matching", {})), GridConfig(**data.get("grid", {}))
    except TypeError as exc:
        raise ValueError(f"Unknown config key/invalid section: {exc}") from exc


def export_grid(directory, grid):
    directory = Path(directory); cfg = grid.config
    states = grid.states()
    pixels = np.where(states == -1, 205, np.where(states == 100, 0, 255)).astype(np.uint8)
    with (directory/"map.pgm").open("xb") as stream:
        stream.write(f"P5\n{cfg.width} {cfg.height}\n255\n".encode()+pixels[::-1].tobytes())
    with (directory/"grid.npz").open("xb") as stream:
        np.savez_compressed(stream, states=states, log_odds=grid.log_odds, seen=grid.seen,
                            metadata=np.array(json.dumps({"grid_schema": 1, "config": asdict(cfg)})))
    with (directory/"map.yaml").open("x", encoding="utf-8") as stream:
        stream.write(f"image: map.pgm\nmode: trinary\nresolution: {cfg.resolution_m}\norigin: [{cfg.origin_x}, {cfg.origin_y}, 0.0]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n")


def load_grid(path):
    with np.load(path, allow_pickle=False) as data:
        metadata = json.loads(str(data["metadata"].item()))
        if metadata["grid_schema"] != 1:
            raise ValueError("Unsupported grid schema")
        cfg = GridConfig(**metadata["config"])
        states = data["states"].copy()
        if states.shape != (cfg.height, cfg.width) or not np.isin(states, [-1, 0, 100]).all():
            raise ValueError("Invalid occupancy data")
        return states, cfg


def map_session(source, output, count, matching=None, grid=None, with_landmarks=True, preview=None):
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    mapper, landmarks = LocalMapper(grid, matching), LandmarkMap()
    entries = []
    with (output/"tracking.jsonl").open("x", encoding="utf-8") as journal, \
         (output/"landmark-observations.jsonl").open("x", encoding="utf-8") as evidence:
        for index, scan in enumerate(source):
            filename = f"scan_{index:06d}.npz"; save_scan(output/filename, scan)
            entry = dict(mapper.update(scan), file=filename, scan_sha256=fingerprint(scan))
            if with_landmarks:
                observation = landmarks.update(scan, entry["sensor_to_world"], filename)
                evidence.write(json.dumps(dict(sequence=scan.sequence, **observation), allow_nan=False)+"\n"); evidence.flush()
            entries.append(entry); journal.write(json.dumps(entry, allow_nan=False)+"\n"); journal.flush()
            if preview is not None and not preview(scan, mapper, entry, landmarks.report() if with_landmarks else None):
                break
            if index+1 >= count:
                break
    if not entries:
        raise ValueError("Mapping source produced no scans")
    export_grid(output, mapper.grid)
    report = {"trajectory_schema": 1, "status": "tracking_lost" if mapper.lost else "completed",
              "coordinate_system": "first sensor frame, x forward/y left, radians/meters",
              "matching": asdict(mapper.match_config), "grid": asdict(mapper.grid.config), "trajectory": entries,
              "accepted_scans": sum(e["sensor_to_world"] is not None for e in entries),
              "limits": "Local point-to-line odometry, drift, no loop closure, no deskew or automatic recovery."}
    write_json(output/"trajectory.json", report)
    if with_landmarks:
        landmark_report = dict(landmarks.report(), mapping_status=report["status"])
        write_json(output/"landmarks.json", landmark_report)
        write_csv(output/"landmarks.csv", [["id", "kind", "observations", "status", "x_m", "y_m"]]+[
            [o["landmark_id"], o["kind"], o["observations"], o["status"], *o["xy_world_m"]] for o in landmark_report["landmarks"]])
    return dict(report, scans=len(entries), landmarks=len(landmarks.objects) if with_landmarks else 0)


def scene(scan, baseline=None):
    report = dict(inspect_scan(scan), scan_sha256=fingerprint(scan))
    if baseline:
        reference = json.loads(Path(baseline).read_text(encoding="utf-8"))
        if reference.get("inspection_schema") != 1 or "snapshot" not in reference:
            raise ValueError("Baseline must reference a scan snapshot")
        old = load_scan(Path(baseline).parent/reference["snapshot"])
        if fingerprint(old) != reference["scan_sha256"]:
            raise ValueError("Baseline snapshot changed")
        if old.frame_id != scan.frame_id:
            raise ValueError("Baseline frame differs")
        a, b = points(scan)[0], points(old)[0]
        if not len(a) or not len(b):
            raise ValueError("Baseline comparison requires hit points")
        nearest = np.concatenate([np.min(np.linalg.norm(chunk[:, None, :]-b[None, :, :], axis=2), axis=1)
                                  for chunk in np.array_split(a, max(1, int(np.ceil(len(a)/128))))])
        report["baseline"] = {"median_nearest_distance_m": float(np.median(nearest)),
                              "p95_nearest_distance_m": float(np.percentile(nearest, 95)),
                              "assumption": "Same fixed sensor pose required; no pose compensation or identity proof"}
    return report


def benchmark(source, count):
    times, domains, sequences, hit_fractions = [], [], [], []
    started = time.monotonic()
    for index, scan in enumerate(source):
        times.append(scan.time_s); domains.append(scan.domain); sequences.append(scan.sequence)
        hit_fractions.append(float(np.mean(scan.status == 1)) if len(scan.status) else 0.)
        if index+1 >= count:
            break
    if not times:
        raise ValueError("No scans to benchmark")
    elapsed = time.monotonic()-started
    delta = np.diff(times)
    return {"scans": len(times), "host_elapsed_s": elapsed, "host_scans_per_s": len(times)/max(elapsed, 1e-9),
            "median_source_interval_s": float(np.median(delta[delta > 0])) if np.any(delta > 0) and len(set(domains)) == 1 else None,
            "nonpositive_time_steps": int(np.sum(delta <= 0)) if len(set(domains)) == 1 else None, "domains": sorted(set(domains)),
            "observed_sequence_gaps": sum(max(0, b-a-1) for a, b in zip(sequences, sequences[1:])),
            "mean_hit_fraction": float(np.mean(hit_fractions)),
            "limits": "Host/replay rate is not motor speed. Source host receive times are not per-point acquisition times."}
