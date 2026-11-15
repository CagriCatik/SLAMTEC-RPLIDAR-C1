from dataclasses import fields
import hashlib
import json
import os
from pathlib import Path
import tempfile
import numpy as np
from .models import Scan

ARRAYS = ("angles", "ranges", "status", "quality", "raw_angle_q14", "raw_distance_q2", "flags")


def metadata(scan):
    return {f.name: getattr(scan, f.name) for f in fields(Scan) if f.name not in ARRAYS}


def fingerprint(scan):
    digest = hashlib.sha256(json.dumps(metadata(scan), sort_keys=True, allow_nan=False).encode())
    for name in ARRAYS:
        array = getattr(scan, name)
        if array is not None:
            digest.update(name.encode()+str(array.dtype).encode()+np.ascontiguousarray(array).tobytes())
    return digest.hexdigest()


def save_scan(path, scan):
    path = Path(path)
    if path.suffix != ".npz":
        raise ValueError("Scan snapshots require .npz")
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {name: getattr(scan, name) for name in ARRAYS if getattr(scan, name) is not None}
    arrays["manifest"] = np.array(json.dumps(dict(schema=1, **metadata(scan)), allow_nan=False))
    fd, temp = tempfile.mkstemp(dir=path.parent, suffix=".npz")
    try:
        with os.fdopen(fd, "wb") as stream:
            np.savez_compressed(stream, **arrays)
        os.link(temp, path)
    finally:
        os.unlink(temp)


def load_scan(path):
    with np.load(path, allow_pickle=False) as data:
        values = json.loads(str(data["manifest"].item()))
        if values.pop("schema") != 1:
            raise ValueError("Unsupported scan schema")
        values.update({name: data[name].copy() for name in ARRAYS if name in data})
        return Scan(**values)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def write_csv(path, rows):
    import csv
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as stream:
        csv.writer(stream).writerows(rows)
