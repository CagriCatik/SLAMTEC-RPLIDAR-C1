from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
import numpy as np

from c1_lab.sources import DemoSource
from c1_lab.models import Scan, HIT, CLEAR, UNKNOWN
from c1_lab.geometry import pose_matrix
from c1_lab.odometry import match_scans, MatchConfig
from c1_lab.mapping import GridConfig, OccupancyGrid, LocalMapper
from c1_lab.landmarks import LandmarkMap
from c1_lab.applications import export_grid, load_grid
from c1_lab.planning import inflate, astar


class OdometryTests(unittest.TestCase):
    def test_relative_transform_direction_and_scale(self):
        frames = list(DemoSource(2))
        estimate, diagnostic = match_scans(*frames)
        self.assertEqual(diagnostic["reason"], "accepted")
        expected = np.linalg.inv(pose_matrix(DemoSource.pose_at(1)))@pose_matrix(DemoSource.pose_at(0))
        np.testing.assert_allclose(estimate, expected, atol=.003)

    def test_unordered_scan_has_same_registration(self):
        a, b = list(DemoSource(2))
        order = np.random.default_rng(1).permutation(len(b.angles))
        shuffled = replace(b, angles=b.angles[order], ranges=b.ranges[order], status=b.status[order], quality=b.quality[order])
        first, _ = match_scans(a, b); second, _ = match_scans(a, shuffled)
        np.testing.assert_allclose(first, second, atol=1e-10)

    def test_single_wall_is_degenerate(self):
        angle = np.linspace(-.6, .6, 200)
        value = Scan(angle, 2/np.cos(angle), np.full(200, HIT), 0, 0.)
        estimate, report = match_scans(value, replace(value, sequence=1, time_s=.1))
        self.assertIsNone(estimate)
        self.assertEqual(report["reason"], "degenerate_geometry")

    def test_motion_gate_and_missing_data(self):
        a, b = list(DemoSource(2))
        estimate, report = match_scans(a, b, MatchConfig(max_translation_m=.001))
        self.assertIsNone(estimate); self.assertEqual(report["reason"], "motion_gate")
        b.status[:] = UNKNOWN
        self.assertEqual(match_scans(a, b)[1]["reason"], "insufficient_points")

    def test_known_multiframe_trajectory(self):
        mapper = LocalMapper()
        for value in DemoSource(12):
            result = mapper.update(value)
            self.assertIsNotNone(result["sensor_to_world"])
            np.testing.assert_allclose(result["sensor_to_world"], pose_matrix(DemoSource.pose_at(value.sequence)), atol=.006)

    def test_clock_failure_latches_and_prevents_map_updates(self):
        frames = list(DemoSource(3)); mapper = LocalMapper()
        mapper.update(frames[0]); before = mapper.grid.log_odds.copy()
        frames[1].time_s = 0
        failed = mapper.update(frames[1]); later = mapper.update(frames[2])
        self.assertIsNone(failed["sensor_to_world"])
        self.assertEqual(later["diagnostic"]["reason"], "tracking_lost_latched")
        np.testing.assert_array_equal(before, mapper.grid.log_odds)

    def test_invalid_pose_is_not_integrated(self):
        matcher = Mock(return_value=(np.zeros((3, 3)), {"reason": "accepted"}))
        mapper = LocalMapper(matcher=matcher)
        a, b = list(DemoSource(2)); mapper.update(a)
        self.assertEqual(mapper.update(b)["diagnostic"]["reason"], "invalid_transform")


class GridTests(unittest.TestCase):
    def setUp(self):
        self.cfg = GridConfig(.1, 60, 60, -3., -3.)

    def test_hit_clears_ray_and_occupies_only_endpoint(self):
        grid = OccupancyGrid(self.cfg)
        value = Scan(np.array([0.]), np.array([1.]), np.array([HIT]), 0, 0.)
        grid.integrate(value, np.eye(3))
        self.assertEqual(grid.states()[30, 40], 100)
        self.assertEqual(grid.states()[30, 35], 0)
        self.assertEqual(grid.states()[30, 45], -1)
        self.assertEqual(grid.states()[30, 30], -1)  # blind zone stays unknown

    def test_unknown_ray_never_clears(self):
        grid = OccupancyGrid(self.cfg)
        grid.integrate(Scan(np.array([0.]), np.array([np.nan]), np.array([UNKNOWN]), 0, 0.), np.eye(3))
        self.assertTrue((grid.states() == -1).all())

    def test_explicit_clear_has_no_obstacle_endpoint(self):
        grid = OccupancyGrid(self.cfg)
        grid.integrate(Scan(np.array([0.]), np.array([1.]), np.array([CLEAR]), 0, 0.), np.eye(3))
        self.assertEqual(grid.states()[30, 40], 0)
        self.assertFalse((grid.states() == 100).any())

    def test_outside_endpoint_does_not_create_boundary_obstacle(self):
        grid = OccupancyGrid(self.cfg)
        grid.integrate(Scan(np.array([0.]), np.array([6.]), np.array([HIT]), 0, 0.), np.eye(3))
        self.assertFalse((grid.states() == 100).any())
        self.assertEqual(grid.states()[30, 59], 0)

    def test_sensor_outside_is_transactional(self):
        grid = OccupancyGrid(self.cfg); before = grid.log_odds.copy()
        with self.assertRaises(ValueError):
            grid.integrate(next(iter(DemoSource(1))), pose_matrix([8, 0, 0]))
        np.testing.assert_array_equal(grid.log_odds, before)

    def test_export_and_reload_preserve_origin_and_flip_pgm_rows(self):
        grid = OccupancyGrid(GridConfig(1., 3, 2, -1., -1.))
        grid.seen[0, 0] = True; grid.log_odds[0, 0] = 2
        with tempfile.TemporaryDirectory() as directory:
            export_grid(directory, grid)
            states, cfg = load_grid(Path(directory)/"grid.npz")
            np.testing.assert_array_equal(states, grid.states()); self.assertEqual(cfg, grid.config)
            data = (Path(directory)/"map.pgm").read_bytes().split(b'\n', 3)[3]
            self.assertEqual(data[3], 0)

    def test_grid_limits_and_config_validation(self):
        for options in ({"width": 0}, {"width": 2000, "height": 2000}, {"free_log_odds": 1}, {"resolution_m": np.nan}):
            with self.assertRaises(ValueError):
                GridConfig(**options)


class LandmarkPlanningTests(unittest.TestCase):
    def test_landmarks_keep_sources_and_confirm(self):
        landmarks = LandmarkMap()
        for value in DemoSource(3, moving=False):
            landmarks.update(value, np.eye(3), f"scan_{value.sequence:06d}.npz")
        report = landmarks.report()
        self.assertTrue(any(o["status"] == "confirmed" for o in report["landmarks"]))
        record = report["landmarks"][0]["recent_observations"][0]
        self.assertEqual(len(record["scan_sha256"]), 64)
        self.assertIn("sensor_to_world", record)

    def test_landmarks_ignore_missing_pose_and_reject_duplicate_scan(self):
        landmarks = LandmarkMap(); value = next(iter(DemoSource(1)))
        self.assertFalse(landmarks.update(value, None, "a.npz")["observations"])
        landmarks.update(value, np.eye(3), "a.npz")
        with self.assertRaises(ValueError):
            landmarks.update(value, np.eye(3), "b.npz")

    def test_unknown_and_occupied_cells_block_offline_planning(self):
        states = np.zeros((20, 20), np.int8); states[:, 10] = -1
        blocked = inflate(states, .1, .1)
        self.assertEqual(astar(blocked, (3, 3), (15, 3)), [])
        states[10, 10] = 0; blocked = inflate(states, .1, 0.)
        path = astar(blocked, (3, 3), (15, 3))
        self.assertTrue(path)
        self.assertTrue(all(not blocked[y, x] for x, y in path))

    def test_footprint_inflates_obstacles_unknown_and_map_boundary(self):
        states = np.zeros((20, 20), np.int8); states[10, 10] = 100; states[5, 5] = -1
        blocked = inflate(states, .1, .2)
        self.assertTrue(blocked[10, 11]); self.assertTrue(blocked[5, 6]); self.assertTrue(blocked[0, 0])
        with self.assertRaises(ValueError):
            astar(blocked, (10, 10), (15, 15))
