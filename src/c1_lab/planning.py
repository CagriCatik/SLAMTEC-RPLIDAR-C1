"""V4 offline footprint/inflation and A*; never sends actuator commands."""
import heapq
import numpy as np


def inflate(states, resolution, radius):
    states = np.asarray(states)
    if states.ndim != 2 or not np.isin(states, [-1, 0, 100]).all():
        raise ValueError("Expected trinary occupancy grid")
    if not np.isfinite([resolution, radius]).all() or resolution <= 0 or radius < 0:
        raise ValueError("Invalid circular footprint")
    reach = int(np.ceil(radius/resolution))
    if reach > 200:
        raise ValueError("Inflation radius exceeds computational limit")
    blocked = states != 0  # unknown is conservatively blocked
    h, w = states.shape
    # A footprint cannot extend into unknown cells or outside the grid either.
    unsafe = states != 0
    for dy in range(-reach, reach+1):
        for dx in range(-reach, reach+1):
            if np.hypot(dx, dy)*resolution > radius+resolution/np.sqrt(2):
                continue
            sy, ey = max(0, -dy), min(h, h-dy); sx, ex = max(0, -dx), min(w, w-dx)
            if sy < ey and sx < ex:
                blocked[sy+dy:ey+dy, sx+dx:ex+dx] |= unsafe[sy:ey, sx:ex]
    if reach:
        blocked[:reach] = True; blocked[-reach:] = True
        blocked[:, :reach] = True; blocked[:, -reach:] = True
    return blocked


def astar(blocked, start, goal):
    blocked = np.asarray(blocked, dtype=bool)
    if blocked.ndim != 2:
        raise ValueError("Expected 2D blocked grid")
    h, w = blocked.shape
    start, goal = tuple(start), tuple(goal)
    for x, y in (start, goal):
        if type(x) is not int or type(y) is not int or not (0 <= x < w and 0 <= y < h) or blocked[y, x]:
            raise ValueError("Start/goal must be known footprint-clear cells")
    queue, cost, parent = [(0., start)], {start: 0}, {}
    while queue:
        _, node = heapq.heappop(queue)
        if node == goal:
            path = [node]
            while node in parent:
                node = parent[node]; path.append(node)
            return path[::-1]
        x, y = node
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = x+dx, y+dy
            if not (0 <= nxt[0] < w and 0 <= nxt[1] < h) or blocked[nxt[1], nxt[0]]:
                continue
            new = cost[node]+1
            if new < cost.get(nxt, np.inf):
                cost[nxt], parent[nxt] = new, node
                heapq.heappush(queue, (new+abs(goal[0]-nxt[0])+abs(goal[1]-nxt[1]), nxt))
    return []
