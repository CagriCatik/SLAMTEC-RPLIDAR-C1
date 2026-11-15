"""Reproducible README SVG from the actual synthetic scan/mapping pipeline."""
import json
import base64
import struct
import zlib
from pathlib import Path
import tempfile
import numpy as np
from c1_lab.sources import DemoSource
from c1_lab.geometry import points
from c1_lab.processing import inspect_scan
from c1_lab.applications import map_session, load_grid


def main():
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory)/"demo"
        summary = map_session(DemoSource(12), target, 12)
        states, cfg = load_grid(target/"grid.npz")
        landmarks = json.loads((target/"landmarks.json").read_text())["landmarks"]
    scan = next(iter(DemoSource(1))); xy, _ = points(scan)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" viewBox="0 0 1200 520" role="img" aria-labelledby="title">',
        '<title id="title">Ausgeführte synthetische C1-Demo: Scan, lokale Karte und geometrische Landmarken</title>',
        '<rect width="1200" height="520" rx="18" fill="#0f172a"/>',
        '<text x="32" y="44" fill="#7ee4d0" font-family="sans-serif" font-size="24">RPLIDAR C1 LAB</text>',
        '<text x="32" y="72" fill="#cbd5e1" font-family="sans-serif" font-size="15">Synthetische 2D-Demo · Scan → SE2-Pose → Occupancy Grid → geometrische Landmarken</text>',
        '<rect x="24" y="95" width="554" height="362" rx="10" fill="#1e293b"/>',
        '<rect x="598" y="95" width="578" height="362" rx="10" fill="#334155"/>']
    def left(point):
        return 301+point[0]*48, 276-point[1]*48
    for x, y in xy:
        px, py = left((x, y))
        svg.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="1.8" fill="#7dd3fc"/>')
    for line in inspect_scan(scan)["lines"]:
        a, b = [left(p) for p in line["ends_m"]]
        svg.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#f5c66b" stroke-width="2"/>')
    colors = {-1: '#718096', 0: '#f1f5f9', 100: '#142136'}
    # Display subsampling only; estimation still uses the full configured grid.
    display = states[::2, ::2]
    rgb = np.zeros((*display.shape, 3), np.uint8)
    for state, color in colors.items():
        rgb[display == state] = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    def chunk(kind, data):
        return struct.pack('>I', len(data))+kind+data+struct.pack('>I', zlib.crc32(kind+data)&0xffffffff)
    raw = b''.join(b'\x00'+row.tobytes() for row in rgb[::-1])
    png = (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB', len(display[0]), len(display), 8, 2, 0, 0, 0))
           +chunk(b'IDAT', zlib.compress(raw))+chunk(b'IEND', b''))
    encoded = base64.b64encode(png).decode()
    svg.append(f'<image x="737" y="108" width="300" height="300" href="data:image/png;base64,{encoded}" style="image-rendering:pixelated"/>')
    def right(point):
        return 737+(point[0]-cfg.origin_x)/cfg.resolution_m/2*2.5, 108+(len(display)-(point[1]-cfg.origin_y)/cfg.resolution_m/2)*2.5
    for item in landmarks:
        x, y = right(item["xy_world_m"])
        svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="#0f766e" stroke="#5eead4" stroke-width="1"/>')
    route = ' '.join(f'{right(np.array(e["sensor_to_world"])[:2,2])[0]:.2f},{right(np.array(e["sensor_to_world"])[:2,2])[1]:.2f}' for e in summary["trajectory"] if e["sensor_to_world"] is not None)
    svg.extend([f'<polyline points="{route}" fill="none" stroke="#d97706" stroke-width="3"/>',
        '<text x="42" y="437" fill="#cbd5e1" font-family="sans-serif" font-size="14">Native Demopunkte + RANSAC/TLS-Linien</text>',
        f'<text x="620" y="437" fill="#cbd5e1" font-family="sans-serif" font-size="14">{summary["accepted_scans"]} akzeptierte Scans · {len(landmarks)} geometrische Landmarken</text>',
        '<text x="32" y="488" fill="#94a3b8" font-family="sans-serif" font-size="14">Grau: unbekannt · hell: frei · dunkel: belegt · grün: Landmarken · keine echten Hardwaremessungen</text>', '</svg>'])
    path = Path(__file__).resolve().parents[1]/"docs"/"assets"/"demo.svg"
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text('\n'.join(svg)+'\n', encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
