"""Optional Matplotlib adapter; Cartesian/polar inspection and occupancy preview."""
import numpy as np
from .geometry import points
from .processing import inspect_scan


def pyplot():
    try:
        import matplotlib.pyplot as plt
        return plt
    except ImportError as exc:
        raise RuntimeError("Install the [viewer] extra") from exc


def view(source, count=30, polar=False, save=None, headless=False):
    plt = pyplot()
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"} if polar else {})
    if not headless:
        plt.ion(); plt.show()
    try:
        seen = 0
        for index, scan in enumerate(source):
            seen += 1; ax.clear()
            xy, valid = points(scan)
            if polar:
                ax.scatter(scan.angles[valid], scan.ranges[valid], s=3)
            else:
                ax.scatter(xy[:, 0], xy[:, 1], s=4)
                for line in inspect_scan(scan)["lines"]:
                    ends = np.array(line["ends_m"])
                    ax.plot(ends[:, 0], ends[:, 1], linewidth=2)
                ax.set_aspect("equal"); ax.set_xlabel("x forward (m)"); ax.set_ylabel("y left (m)")
            ax.set_title(f"C1 Lab | scan {scan.sequence} | {len(xy)} HIT | {scan.domain}")
            if not headless:
                plt.pause(.02)
                if not plt.fignum_exists(fig.number):
                    break
            if index+1 >= count:
                break
        if not seen:
            raise ValueError("Viewer source was empty")
        if save:
            from pathlib import Path
            path = Path(save); path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                raise FileExistsError(path)
            fig.savefig(path, dpi=140)
    finally:
        plt.close(fig)


class MapPreview:
    def __init__(self):
        self.plt = pyplot(); self.plt.ion()
        self.fig, self.ax = self.plt.subplots(); self.path = []
        self.plt.show()

    def __call__(self, scan, mapper, entry, landmarks):
        from matplotlib.colors import ListedColormap
        self.ax.clear(); cfg = mapper.grid.config
        state = mapper.grid.states()
        image = np.where(state == -1, 0, np.where(state == 100, 2, 1))
        self.ax.imshow(image, origin="lower", vmin=0, vmax=2, cmap=ListedColormap(["#718096", "#f1f5f9", "#142136"]),
                       extent=[cfg.origin_x, cfg.origin_x+cfg.width*cfg.resolution_m, cfg.origin_y, cfg.origin_y+cfg.height*cfg.resolution_m])
        if entry["sensor_to_world"] is not None:
            self.path.append(np.array(entry["sensor_to_world"])[:2, 2])
        if self.path:
            path = np.array(self.path); self.ax.plot(path[:, 0], path[:, 1], color="#d97706")
        for landmark in (landmarks or {}).get("landmarks", []):
            x, y = landmark["xy_world_m"]
            self.ax.plot(x, y, "+", color="#0f766e")
        self.ax.set_title(f"{entry['status']}: {entry['diagnostic']['reason']} | geometric landmarks only")
        self.plt.pause(.01)
        return self.plt.fignum_exists(self.fig.number)

    def close(self):
        self.plt.close(self.fig)
