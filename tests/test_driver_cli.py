import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from c1_lab.drivers import decode_scan, HardwareSource
from c1_lab.cli import main
from c1_lab.sources import DemoSource


def packet():
    return {"type": "scan", "bridge_schema": 1, "sequence": 0, "time_s": 12., "host_receive_duration_s": .1,
            "scan_mode_id": 1, "max_distance_m": 12., "angle_q14": [32768, 16384, 0],
            "distance_q2": [4000, 8000, 0], "quality": [255, 100, 0], "flags": [1, 0, 0]}


class DriverTests(unittest.TestCase):
    def test_keyboard_interrupt_during_startup_closes_child(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"fake_bridge"
            path.write_text("#!"+sys.executable+"\nimport time\ntime.sleep(10)\n"); path.chmod(0o755)
            source = HardwareSource(path, "/dev/fake")
            with patch.object(source, "_read", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    source.__enter__()
            self.assertIsNotNone(source.process.poll())

    def test_native_units_flags_quality_and_unknown_preserved(self):
        value = decode_scan(packet(), {"model": "C1"})
        np.testing.assert_allclose(value.ranges, [1, 2, 0])
        np.testing.assert_allclose(value.angles, [0, np.pi/2, -np.pi])
        np.testing.assert_array_equal(value.status, [1, 1, 0])
        np.testing.assert_array_equal(value.raw_distance_q2, [4000, 8000, 0])
        self.assertEqual(value.domain, "host_monotonic_receive")

    def test_invalid_packet_fields_fail_without_quantization_wrap(self):
        for key, bad in (("angle_q14", [-1, 0, 0]), ("quality", [256, 0, 0]),
                         ("max_distance_m", np.nan), ("distance_q2", [1.5, 0, 0])):
            data = packet(); data[key] = bad
            with self.assertRaises(ValueError):
                decode_scan(data, {})

    def test_binary_buffer_reads_multiple_lines_and_stops_child(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"fake_bridge"
            lines = [dict(type="info", bridge_schema=1, model_name="C1"), packet(), dict(packet(), sequence=1, time_s=12.1)]
            program = "#!"+sys.executable+"\nimport sys,time\nsys.stdout.write("+repr(''.join(json.dumps(row)+'\n' for row in lines))+ ");sys.stdout.flush()\ntime.sleep(10)\n"
            path.write_text(program); path.chmod(0o755)
            with HardwareSource(path, "/dev/fake") as source:
                iterator = iter(source)
                self.assertEqual(next(iterator).sequence, 0)
                self.assertEqual(next(iterator).sequence, 1)
                process = source.process
            self.assertIsNotNone(process.poll())

    def test_malformed_startup_cleans_up_process(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"fake_bridge"
            path.write_text("#!"+sys.executable+"\nimport time\nprint('{}',flush=True)\ntime.sleep(10)\n")
            path.chmod(0o755)
            source = HardwareSource(path, "/dev/fake")
            with self.assertRaises(ValueError):
                source.__enter__()
            self.assertIsNotNone(source.process.poll())


class CLITests(unittest.TestCase):
    def call(self, args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(args)

    def test_capture_scene_baseline_export_measure_and_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(self.call(["capture", "--scans", "3", "--output", str(root/"scans")]), 0)
            self.assertEqual(self.call(["scene", "--source", "replay", "--input", str(root/"scans"), "--output", str(root/"scene")]), 0)
            self.assertEqual(self.call(["scene", "--source", "replay", "--input", str(root/"scans"), "--baseline", str(root/"scene"/"scene.json")]), 0)
            self.assertEqual(self.call(["export", "--source", "replay", "--input", str(root/"scans"), "--output", str(root/"points.csv")]), 0)
            self.assertEqual(self.call(["measure", "--input", str(root/"scans"/"scan_000000.npz"), "--indices", "1", "2"]), 0)
            self.assertEqual(self.call(["capture", "--output", str(root/"scans")]), 2)

    def test_mapping_replay_landmarks_and_offline_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(self.call(["map", "--scans", "5", "--output", str(root/"map")]), 0)
            self.assertEqual(self.call(["map", "--source", "replay", "--input", str(root/"map"), "--scans", "5", "--output", str(root/"replay")]), 0)
            a = json.loads((root/"map"/"trajectory.json").read_text()); b = json.loads((root/"replay"/"trajectory.json").read_text())
            self.assertEqual(a, b)
            self.assertEqual(self.call(["landmarks", "--input", str(root/"map"/"landmarks.json"), "--kind", "line"]), 0)
            self.assertEqual(self.call(["landmarks", "--input", str(root/"map"/"landmarks.json"), "--near", "0", "0", "--radius", "10"]), 0)
            self.assertEqual(self.call(["landmarks", "--input", str(root/"map"/"landmarks.json"), "--near", "0", "0", "--radius", "-1"]), 2)
            self.assertEqual(self.call(["plan", "--input", str(root/"map"/"grid.npz"), "--start", ".5", ".5", "--goal", "2", "2", "--output", str(root/"plan.json")]), 0)

    def test_empty_source_and_missing_inputs(self):
        self.assertEqual(self.call(["scene", "--source", "replay"]), 2)
        with tempfile.TemporaryDirectory() as directory, patch("c1_lab.cli.source", return_value=DemoSource(1)):
            with patch.object(DemoSource, "__iter__", return_value=iter([])):
                self.assertEqual(self.call(["capture", "--output", str(Path(directory)/"empty")]), 2)
