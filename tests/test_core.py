from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
import numpy as np

from c1_lab.models import Scan, HIT, CLEAR, UNKNOWN
from c1_lab.geometry import native_angles, points, pose_matrix, transform, wrap
from c1_lab.storage import save_scan, load_scan, fingerprint
from c1_lab.sources import DemoSource, ReplaySource
from c1_lab.processing import clusters, lines, corners, sector, filter_scan, temporal_median, angular_bins


def scan(angles=(0., np.pi/2), ranges=(1., 2.), statuses=(HIT, HIT), **changes):
    values = dict(angles=np.array(angles), ranges=np.array(ranges, float), status=np.array(statuses, np.uint8),
                  sequence=0, time_s=0., metadata={"full_revolution": True})
    values.update(changes)
    return Scan(**values)


class GeometryTests(unittest.TestCase):
    def test_polar_axes_meters_and_angle_wrap(self):
        xy, indices = points(scan())
        np.testing.assert_allclose(xy, [[1, 0], [0, 2]], atol=1e-12)
        np.testing.assert_array_equal(indices, [0, 1])
        np.testing.assert_allclose(wrap([0, 2*np.pi, 3*np.pi]), [0, 0, -np.pi])

    def test_native_sdk_angle_convention_and_quantization(self):
        np.testing.assert_allclose(native_angles([0, 16384, 32768, 49152]), [-np.pi, np.pi/2, 0, -np.pi/2])

    def test_full_se2_transform_and_inverse(self):
        matrix = pose_matrix([1, 2, np.pi/2])
        np.testing.assert_allclose(transform([[1, 0]], matrix), [[1, 3]], atol=1e-12)
        np.testing.assert_allclose(transform(transform([[1, 0]], matrix), np.linalg.inv(matrix)), [[1, 0]], atol=1e-12)

    def test_invalid_scan_shapes_times_and_known_ranges(self):
        for changes in ({"time_s": np.nan}, {"sequence": -1}, {"ranges": np.array([0., 2.])},
                        {"status": np.array([9, 1])}, {"angles": np.array([0.])}):
            with self.assertRaises(ValueError):
                scan(**changes)

    def test_unknown_and_clear_do_not_become_pointcloud_hits(self):
        xy, _ = points(scan(statuses=(UNKNOWN, CLEAR)))
        self.assertEqual(len(xy), 0)


class StorageTests(unittest.TestCase):
    def test_roundtrip_native_arrays_and_fingerprint(self):
        original = scan(quality=np.array([0, 255], np.uint8), raw_angle_q14=np.array([32768, 16384], np.uint16),
                        raw_distance_q2=np.array([4000, 8000], np.uint32), flags=np.array([1, 0], np.uint8))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"scan_000000.npz"
            save_scan(path, original); loaded = load_scan(path)
            self.assertEqual(fingerprint(original), fingerprint(loaded))
            np.testing.assert_array_equal(loaded.raw_distance_q2, [4000, 8000])
            with self.assertRaises(FileExistsError):
                save_scan(path, original)
            loaded.ranges[0] += .001
            self.assertNotEqual(fingerprint(original), fingerprint(loaded))

    def test_unknown_nan_roundtrip(self):
        original = scan(ranges=(np.nan, 2), statuses=(UNKNOWN, HIT))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"scan_000000.npz"; save_scan(path, original)
            self.assertEqual(fingerprint(original), fingerprint(load_scan(path)))

    def test_empty_replay_and_unsupported_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                ReplaySource(directory)
            path = Path(directory)/"scan_bad.npz"
            np.savez(path, manifest='{"schema":999}')
            with self.assertRaises(ValueError):
                load_scan(path)

    def test_synthetic_source_is_deterministic_and_contains_unknown(self):
        a, b = next(iter(DemoSource(1))), next(iter(DemoSource(1)))
        self.assertEqual(fingerprint(a), fingerprint(b))
        self.assertTrue((a.status == UNKNOWN).any())


class ProcessingTests(unittest.TestCase):
    def test_benchmark_does_not_compare_mixed_time_domains(self):
        from c1_lab.applications import benchmark
        a, b = scan(), scan(sequence=1, time_s=100000., domain="other")
        result = benchmark([a, b], 2)
        self.assertIsNone(result["median_source_interval_s"])
        self.assertIsNone(result["nonpositive_time_steps"])

    def test_wrap_cluster_joins_only_a_full_revolution(self):
        value = scan(angles=(-np.pi+.01, np.pi-.01), ranges=(1, 1))
        self.assertEqual(len(clusters(value, minimum=1)), 1)
        value.metadata["full_revolution"] = False
        self.assertEqual(len(clusters(value, minimum=1)), 2)

    def test_invalid_gap_and_duplicate_angles_do_not_link(self):
        value = scan(angles=(0, .01, .02), ranges=(1, 1, 1), statuses=(HIT, UNKNOWN, HIT))
        self.assertEqual(len(clusters(value, minimum=1)), 2)
        value = scan(angles=(0, 0), ranges=(1, 1))
        self.assertEqual(len(clusters(value, minimum=1)), 2)

    def test_unordered_native_arrays_preserved_by_clustering(self):
        value = scan(angles=(.03, 0, .02, .01), ranges=(1, 1, 1, 1), statuses=(1, 1, 1, 1))
        before = value.angles.copy()
        groups = clusters(value, minimum=1)
        self.assertEqual(len(groups), 1)
        np.testing.assert_array_equal(value.angles, before)

    def test_lines_with_outliers_and_endpoint_corners(self):
        rng = np.random.default_rng(1)
        a = np.c_[np.linspace(0, 2, 100), np.ones(100)]
        b = np.c_[np.full(100, 2.), np.linspace(1, 3, 100)]
        data = np.vstack((a, b))+rng.normal(0, .001, (200, 2))
        segments = lines(np.vstack((data, rng.uniform(-3, 4, (30, 2)))), minimum=30)
        self.assertGreaterEqual(len(segments), 2)
        found = corners(segments)
        self.assertTrue(any(np.linalg.norm(np.array(c["xy_m"])-[2, 1]) < .02 for c in found))

    def test_degenerate_lines_produce_no_fake_geometry(self):
        self.assertEqual(lines(np.ones((30, 2))), [])
        self.assertEqual(corners([]), [])

    def test_sector_unknown_is_not_zero_distance(self):
        result = sector(scan(statuses=(UNKNOWN, UNKNOWN)))
        self.assertIsNone(result["nearest_hit_m"])
        self.assertEqual(result["unknown_fraction"], 1.)

    def test_filters_reject_to_unknown_and_preserve_native_distance(self):
        value = scan(quality=np.array([0, 100], np.uint8))
        filtered = filter_scan(value, min_quality=10)
        np.testing.assert_array_equal(filtered.status, [UNKNOWN, HIT])
        np.testing.assert_array_equal(value.status, [HIT, HIT])
        np.testing.assert_array_equal(filtered.ranges, value.ranges)
        with self.assertRaises(ValueError):
            filter_scan(value, min_quality=np.nan)

    def test_temporal_filter_requires_matching_grid_time_and_all_hits(self):
        a, b = scan(), scan(sequence=1, time_s=.1)
        b.ranges[0] = 1.2; b.status[1] = UNKNOWN
        result = temporal_median([a, b])
        self.assertAlmostEqual(result.ranges[0], 1.1)
        self.assertEqual(result.status[1], UNKNOWN)
        with self.assertRaises(ValueError):
            temporal_median([a, replace(b, time_s=0)])
        with self.assertRaises(ValueError):
            temporal_median([a, replace(b, angles=b.angles+.01)])

    def test_bins_are_derived_and_do_not_fill_gaps(self):
        result = angular_bins(scan(angles=(0, .001), ranges=(2, 1)), 360)
        self.assertEqual(sum(r is not None for r in result["ranges"]), 1)
        self.assertIn(1., result["ranges"])
