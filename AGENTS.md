# Development rules

- Target C1M1-R2; distinguish manufacturer revision, configured values and hardware measurements.
- Core models, geometry, processing, odometry, mapping, landmarks and planning import only standard Python and NumPy.
- Device transport is in drivers, GUI in viewer, orchestration in applications/CLI, ROS in ros2/.
- Meters/radians/seconds; x forward, y left, positive rotation counterclockwise. Document native conversion separately.
- Preserve native arrays and time provenance. Never manufacture per-point acquisition times or calibrated reflectivity.
- HIT, explicit CLEAR and UNKNOWN are distinct. Missing returns do not clear occupancy rays.
- Do not merge angular wrap boundaries for partial scans. Preserve invalid gaps and reject duplicate-angle links.
- Rejected poses cannot update occupancy or landmarks. Geometric hypotheses are not object classes.
- Live, demo and replay share algorithms. Keep recording versioned, no pickle, no overwrites.
- SDK bridge must stop scanning/motor and release the connection on failure/signals.
- No firmware or persistent calibration writes. Do not fabricate hardware/ROS/SLAM validation.
- Test numerical invariants and failures. Keep sources, capability matrix and tutorials synchronized.
- All V4 planning is offline. No actuator commands or automatic driving.
- SDK is external/pinned; inspect its license separately from demos. Do not copy vendor demo applications.
