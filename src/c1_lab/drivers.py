"""Linux process adapter to our official-SDK bridge; no serial protocol reimplementation."""
import json
import os
from pathlib import Path
import selectors
import subprocess
import time
import numpy as np
from .geometry import native_angles
from .models import Scan, HIT, UNKNOWN


def decode_scan(value, device):
    if value.get("bridge_schema") != 1 or value.get("type") != "scan":
        raise ValueError("Unsupported bridge scan schema")
    raw = {}
    for key, limit, dtype in (("angle_q14", 65535, np.uint16), ("distance_q2", 4294967295, np.uint32),
                              ("quality", 255, np.uint8), ("flags", 255, np.uint8)):
        data = value[key]
        if not isinstance(data, list) or any(type(x) is not int or not 0 <= x <= limit for x in data):
            raise ValueError(f"Invalid native {key}")
        raw[key] = np.array(data, dtype=dtype)
    distance = raw["distance_q2"].astype(float)/4000.
    advertised = float(value["max_distance_m"])
    duration = float(value["host_receive_duration_s"])
    if not np.isfinite([advertised, duration]).all() or advertised <= .05 or duration < 0:
        raise ValueError("Invalid bridge range or acquisition timing")
    maximum = min(12., advertised)
    valid = (distance >= .05) & (distance <= maximum)
    return Scan(native_angles(raw["angle_q14"]), distance, np.where(valid, HIT, UNKNOWN).astype(np.uint8),
                value["sequence"], value["time_s"], "host_monotonic_receive", metadata={
                    "source": "official_sdk_bridge", "device": device, "scan_mode_id": value["scan_mode_id"],
                    "full_revolution": True, "representation": "native_hq",
                    "host_receive_duration_s": value["host_receive_duration_s"],
                    "per_point_time": "unavailable", "quality_semantics": "raw SDK HQ quality byte"},
                range_max=maximum, quality=raw["quality"], raw_angle_q14=raw["angle_q14"],
                raw_distance_q2=raw["distance_q2"], flags=raw["flags"])


class HardwareSource:
    def __init__(self, bridge, port, count=30, mode=None, inspect=False):
        if not Path(bridge).is_file():
            raise ValueError("Bridge missing; run python scripts/build_bridge.py")
        self.command = [str(Path(bridge).resolve()), port, "--scans", str(count)]
        if mode is not None:
            self.command += ["--mode", str(mode)]
        if inspect:
            self.command.append("--inspect")
        self.process = self.selector = None
        self.buffer = b""

    def _read(self):
        deadline = time.monotonic()+8.
        while b"\n" not in self.buffer:
            remaining = deadline-time.monotonic()
            if remaining <= 0 or not self.selector.select(timeout=remaining):
                raise RuntimeError("LiDAR bridge timeout")
            data = os.read(self.process.stdout.fileno(), 65536)
            if not data:
                code = self.process.wait(timeout=3.)
                if code != 0 or self.buffer:
                    raise RuntimeError(f"LiDAR bridge exited {code} or truncated JSON; see stderr")
                return None
            self.buffer += data
            if len(self.buffer) > 4*1024*1024:
                raise ValueError("Bridge message exceeds size limit")
        line, self.buffer = self.buffer.split(b"\n", 1)
        return json.loads(line)

    def __enter__(self):
        try:
            self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, bufsize=0)
            self.selector = selectors.DefaultSelector()
            self.selector.register(self.process.stdout, selectors.EVENT_READ)
            self.device = self._read()
            if not isinstance(self.device, dict) or self.device.get("type") != "info" or self.device.get("bridge_schema") != 1:
                raise ValueError("Missing bridge device info")
            return self
        except BaseException:
            self.__exit__(); raise

    def __exit__(self, *_):
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=4.)
                except subprocess.TimeoutExpired:
                    self.process.kill(); self.process.wait(timeout=2.)
            self.process.stdout.close()
        if self.selector is not None:
            self.selector.close()
        return False

    def __iter__(self):
        while True:
            value = self._read()
            if value is None:
                return
            yield decode_scan(value, self.device)
