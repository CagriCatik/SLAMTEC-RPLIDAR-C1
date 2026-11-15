import argparse
import json
from pathlib import Path
import sys
from .applications import benchmark, load_grid, map_session, scene, settings
from .geometry import points
from .processing import angular_bins, filter_scan
from .sources import DemoSource, ReplaySource
from .storage import save_scan, write_json, write_csv


def positive(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError("Positive integer required")
    return value


def source_args(parser, count=30):
    parser.add_argument("--source", choices=("demo", "replay", "hardware"), default="demo")
    parser.add_argument("--input")
    parser.add_argument("--scans", type=positive, default=count)
    parser.add_argument("--moving", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--bridge", default="artifacts/c1_bridge")
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--mode", type=int)


def parser():
    root = argparse.ArgumentParser(prog="c1-lab", description="RPLIDAR C1M1-R2 sensor laboratory")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("capture", "scene", "view", "export", "benchmark", "map", "inspect"):
        p = commands.add_parser(name); source_args(p, 1 if name in ("scene", "export", "inspect") else 30)
        if name == "inspect":
            p.set_defaults(source="hardware")
        if name in ("capture", "export", "map"):
            p.add_argument("--output", required=True)
        elif name != "view":
            p.add_argument("--output")
        if name == "scene":
            p.add_argument("--baseline")
        if name == "view":
            p.add_argument("--polar", action="store_true"); p.add_argument("--save"); p.add_argument("--headless", action="store_true")
        if name == "map":
            p.add_argument("--config"); p.add_argument("--landmarks", action=argparse.BooleanOptionalAction, default=True)
            p.add_argument("--preview", action="store_true")
    filt = commands.add_parser("filter")
    filt.add_argument("--input", required=True); filt.add_argument("--output", required=True)
    filt.add_argument("--minimum", type=float); filt.add_argument("--maximum", type=float); filt.add_argument("--min-quality", type=float)
    bins = commands.add_parser("bins"); bins.add_argument("--input", required=True); bins.add_argument("--count", type=positive, default=360)
    measure = commands.add_parser("measure"); measure.add_argument("--input", required=True)
    measure.add_argument("--indices", type=int, nargs=2, required=True); measure.add_argument("--output")
    query = commands.add_parser("landmarks"); query.add_argument("--input", required=True)
    query.add_argument("--kind", choices=("line", "corner", "cluster")); query.add_argument("--confirmed", action="store_true"); query.add_argument("--output")
    query.add_argument("--near", type=float, nargs=2, help="Filter by world [x,y] in meters")
    query.add_argument("--radius", type=float, default=.5, help="Search radius for --near (meters)")
    plan = commands.add_parser("plan"); plan.add_argument("--input", required=True)
    plan.add_argument("--start", type=float, nargs=2, required=True); plan.add_argument("--goal", type=float, nargs=2, required=True)
    plan.add_argument("--radius", type=float, default=.2); plan.add_argument("--output", required=True)
    return root


def source(args):
    if args.source == "demo":
        if args.input:
            raise ValueError("Demo does not accept --input")
        return DemoSource(args.scans, moving=args.moving if args.moving is not None else args.command == "map")
    if args.source == "replay":
        if not args.input:
            raise ValueError("Replay requires --input")
        return ReplaySource(args.input)
    if args.input:
        raise ValueError("Hardware does not accept --input")
    from .drivers import HardwareSource
    return HardwareSource(args.bridge, args.port, args.scans, args.mode, args.command == "inspect")


def emit(value, path=None):
    if path:
        write_json(path, value)
    print(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False))


def run(args):
    if args.command == "measure":
        import numpy as np
        from .storage import load_scan, fingerprint
        from .models import HIT
        scan = load_scan(args.input)
        a, b = args.indices
        if not all(0 <= i < len(scan.angles) and scan.status[i] == HIT for i in (a, b)):
            raise ValueError("Measurement requires two valid native HIT indices")
        xy = np.array([[scan.ranges[i]*np.cos(scan.angles[i]), scan.ranges[i]*np.sin(scan.angles[i])] for i in (a, b)])
        emit({"indices": [a, b], "points_m": xy.tolist(), "distance_m": float(np.linalg.norm(xy[0]-xy[1])),
              "scan_sha256": fingerprint(scan), "limits": "Same 2D scan; no height or calibrated uncertainty"}, args.output)
        return 0
    if args.command in ("filter", "bins"):
        from .storage import load_scan
        scan = load_scan(args.input)
        if args.command == "filter":
            save_scan(args.output, filter_scan(scan, args.minimum, args.maximum, args.min_quality))
        else:
            emit(angular_bins(scan, args.count))
        return 0
    if args.command == "landmarks":
        import numpy as np
        report = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if report.get("landmark_schema") != 1:
            raise ValueError("Expected landmark_schema=1")
        if not np.isfinite(args.radius) or args.radius <= 0 or (args.near is not None and not np.isfinite(args.near).all()):
            raise ValueError("Finite query center and positive radius required")
        selected = [{k: o[k] for k in ("landmark_id", "kind", "xy_world_m", "observations", "status")}
                    for o in report["landmarks"] if (not args.kind or o["kind"] == args.kind)
                    and (not args.confirmed or o["status"] == "confirmed")
                    and (args.near is None or np.linalg.norm(np.asarray(o["xy_world_m"])-args.near) <= args.radius)]
        emit({"count": len(selected), "landmarks": selected}, args.output); return 0
    if args.command == "plan":
        from .planning import inflate, astar
        import numpy as np
        states, cfg = load_grid(args.input)
        coordinates = np.array([args.start, args.goal])
        if not np.isfinite(coordinates).all():
            raise ValueError("Finite planning coordinates required")
        cells = np.floor((coordinates-[cfg.origin_x, cfg.origin_y])/cfg.resolution_m).astype(int)
        blocked = inflate(states, cfg.resolution_m, args.radius)
        path = astar(blocked, [int(v) for v in cells[0]], [int(v) for v in cells[1]])
        emit({"planning_schema": 1, "status": "path_found" if path else "no_path", "footprint_radius_m": args.radius,
              "path_world_m": [[cfg.origin_x+(x+.5)*cfg.resolution_m, cfg.origin_y+(y+.5)*cfg.resolution_m] for x, y in path],
              "limits": "Offline circular-footprint plan. No actuator commands or navigation validation."}, args.output)
        return 0 if path else 2
    preview = None
    if args.command == "map" and args.preview:
        from .viewer import MapPreview
        preview = MapPreview()
    try:
        with source(args) as scans:
            if args.command == "inspect":
                if args.source != "hardware":
                    raise ValueError("inspect requires hardware source")
                emit(scans.device, args.output); return 0
            if args.command == "view":
                from .viewer import view
                view(scans, args.scans, args.polar, args.save, args.headless); return 0
            if args.command == "benchmark":
                emit(benchmark(scans, args.scans), args.output); return 0
            if args.command == "map":
                matching, grid = settings(args.config)
                report = map_session(scans, args.output, args.scans, matching, grid, args.landmarks, preview)
                emit({k: v for k, v in report.items() if k != "trajectory"})
                return 0 if report["status"] == "completed" else 2
            if args.command == "capture":
                Path(args.output).mkdir(parents=True, exist_ok=False)
            index = -1
            for index, scan in enumerate(scans):
                if args.command == "capture":
                    save_scan(Path(args.output)/f"scan_{index:06d}.npz", scan)
                elif args.command == "scene":
                    report = scene(scan, args.baseline)
                    if args.output:
                        out = Path(args.output); out.mkdir(parents=True, exist_ok=False)
                        save_scan(out/"scan_000000.npz", scan)
                        report["snapshot"] = "scan_000000.npz"
                        write_json(out/"scene.json", report)
                    emit(report); return 0
                elif args.command == "export":
                    xy, _ = points(scan)
                    write_csv(args.output, [["x_m", "y_m"]]+xy.tolist()); emit({"points": len(xy)}); return 0
                if index+1 >= args.scans:
                    emit({"scans": index+1}); return 0
            if args.command == "capture" and index >= 0:
                emit({"scans": index+1}); return 0
            raise ValueError("Source produced no scans")
    finally:
        if preview:
            preview.close()


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return run(args)
    except KeyboardInterrupt:
        print("Interrupted; hardware cleanup requested", file=sys.stderr); return 130
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
        print(f"c1-lab: {exc}", file=sys.stderr); return 2
