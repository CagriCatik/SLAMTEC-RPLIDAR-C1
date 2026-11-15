import ast
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET


class DocumentationTests(unittest.TestCase):
    def test_local_links_and_16_tutorials(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(len(list((root/"projects").glob("*/TUTORIAL.md"))), 16)
        paths = [root/"README.md", root/"TUTORIAL_INDEX.md", *list((root/"docs").rglob("*.md")), *list((root/"projects").rglob("*.md")), root/"ros2"/"README.md"]
        for path in paths:
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' not in link and not link.startswith('#'):
                    self.assertTrue((path.parent/link.split('#')[0]).exists(), f'{path}: {link}')

    def test_svg_is_valid_xml(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(ET.parse(root/'docs/assets/demo.svg').getroot().tag, '{http://www.w3.org/2000/svg}svg')

    def test_core_has_no_driver_ros_or_gui_imports(self):
        root = Path(__file__).resolve().parents[1]/'src/c1_lab'
        forbidden = {'drivers', 'viewer', 'cli', 'rclpy', 'matplotlib', 'serial'}
        for name in ('models', 'geometry', 'processing', 'odometry', 'mapping', 'landmarks', 'planning'):
            for node in ast.walk(ast.parse((root/f'{name}.py').read_text())):
                imported = []
                if isinstance(node, ast.Import):
                    imported = [alias.name.split('.')[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    imported = [(node.module or '').split('.')[0]]
                self.assertFalse(set(imported)&forbidden, f'{name}: {imported}')
