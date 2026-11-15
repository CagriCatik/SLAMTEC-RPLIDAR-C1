import numpy as np
from copy import deepcopy
from .geometry import points, transform, validate_transform
from .processing import inspect_scan
from .storage import fingerprint


class LandmarkMap:
    """Geometric hypotheses only; no semantic object labels or cross-session IDs."""
    def __init__(self, gate_m=.3, min_observations=3, capacity=1000):
        if not np.isfinite(gate_m) or gate_m <= 0 or type(min_observations) is not int or min_observations < 1 or type(capacity) is not int or capacity < 1:
            raise ValueError("Invalid landmark configuration")
        self.gate, self.minimum, self.capacity = gate_m, min_observations, capacity
        self.objects, self.next_id = {}, 1
        self.identities = set()

    def update(self, scan, pose, filename):
        if pose is None:
            return {"observations": [], "rejected": [{"reason": "pose_unavailable"}]}
        pose = validate_transform(pose)
        identity = scan.domain, scan.sequence, scan.time_s
        if identity in self.identities:
            raise ValueError("Duplicate landmark scan identity")
        report = inspect_scan(scan)
        self.identities.add(identity)
        features = []
        for line in report["lines"]:
            ends = transform(line["ends_m"], pose)
            direction = ends[1]-ends[0]
            features.append({"kind": "line", "xy_world_m": ends.mean(axis=0).tolist(),
                             "ends_world_m": ends.tolist(), "orientation": float(np.arctan2(direction[1], direction[0]) % np.pi),
                             "scan_point_indices": [report["line_point_to_scan_index"][i] for i in line["point_indices"]]})
        for corner in report["corners"]:
            features.append({"kind": "corner", "xy_world_m": transform([corner["xy_m"]], pose)[0].tolist(),
                             "support_line_indices": corner["line_indices"]})
        for cluster in report["clusters"]:
            # Large connected room contours are not useful object-like clusters.
            if max(cluster["visible_extent_m"]) <= 1.5:
                features.append({"kind": "cluster", "xy_world_m": transform([cluster["center_m"]], pose)[0].tolist(),
                                 "scan_point_indices": cluster["point_indices"]})
        pairs = []
        for index, feature in enumerate(features):
            for object_id, obj in self.objects.items():
                distance = float(np.linalg.norm(np.array(feature["xy_world_m"])-obj["mean"]))
                if feature["kind"] != obj["kind"] or distance > self.gate:
                    continue
                if feature["kind"] == "line":
                    angle = abs((feature["orientation"]-obj["orientation"]+np.pi/2) % np.pi-np.pi/2)
                    if angle > np.deg2rad(10):
                        continue
                pairs.append((distance, object_id, index))
        matched, used = {}, set()
        for _, object_id, index in sorted(pairs):
            if index not in matched and object_id not in used:
                matched[index] = object_id; used.add(object_id)
        observations, rejected = [], []
        for index, feature in enumerate(features):
            object_id = matched.get(index)
            if object_id is None:
                if len(self.objects) >= self.capacity:
                    rejected.append({"reason": "landmark_capacity", "feature_index": index}); continue
                object_id = f"landmark-{self.next_id:06d}"; self.next_id += 1
                self.objects[object_id] = {"kind": feature["kind"], "count": 0, "mean": np.zeros(2),
                    "m2": np.zeros((2, 2)), "orientation": feature.get("orientation"), "recent": []}
            obj = self.objects[object_id]; obj["count"] += 1
            position = np.array(feature["xy_world_m"]); delta = position-obj["mean"]
            obj["mean"] += delta/obj["count"]; obj["m2"] += np.outer(delta, position-obj["mean"])
            evidence = dict(feature, landmark_id=object_id, file=filename, sequence=scan.sequence,
                            time_s=scan.time_s, domain=scan.domain, scan_sha256=fingerprint(scan),
                            sensor_to_world=pose.tolist())
            observations.append(evidence); obj["recent"].append(evidence)
            del obj["recent"][:-50]
        return {"observations": observations, "rejected": rejected}

    def report(self):
        return {"landmark_schema": 1, "coordinate_system": "first sensor frame: x forward, y left; meters",
                "landmarks": [{"landmark_id": key, "kind": obj["kind"], "xy_world_m": obj["mean"].tolist(),
                    "observations": obj["count"], "status": "confirmed" if obj["count"] >= self.minimum else "tentative",
                    "position_scatter_m2": (obj["m2"]/max(1, obj["count"]-1)).tolist(),
                    "recent_observations": deepcopy(obj["recent"])} for key, obj in sorted(self.objects.items())],
                "limits": "Geometric hypotheses. Changing visibility, symmetry and pose drift can change IDs; scatter is not calibrated uncertainty."}
