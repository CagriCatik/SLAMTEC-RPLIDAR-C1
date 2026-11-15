import importlib.util
import os
from pathlib import Path
import tempfile
import unittest


@unittest.skipUnless(importlib.util.find_spec('matplotlib'), 'optional viewer not installed')
class ViewerTests(unittest.TestCase):
    def test_cartesian_and_polar_headless_render_and_cleanup(self):
        os.environ['MPLBACKEND'] = 'Agg'
        from c1_lab.viewer import view, pyplot
        from c1_lab.sources import DemoSource
        with tempfile.TemporaryDirectory() as directory:
            for polar in (False, True):
                path = Path(directory)/f'{polar}.png'
                view(DemoSource(1), 1, polar=polar, save=path, headless=True)
                self.assertGreater(path.stat().st_size, 1000)
            self.assertFalse(pyplot().get_fignums())
