import numpy as np
from .models import HIT


def wrap(angle):
    return (np.asarray(angle)+np.pi) % (2*np.pi)-np.pi


def native_angles(q14):
    """Same non-inverted convention as upstream ROS: theta = pi - native."""
    return wrap(np.pi-np.asarray(q14, dtype=float)*np.pi/(2*16384))


def points(scan):
    valid = scan.status == HIT
    angle, distance = scan.angles[valid], scan.ranges[valid]
    return np.column_stack((distance*np.cos(angle), distance*np.sin(angle))), np.flatnonzero(valid)


def pose_matrix(pose):
    pose = np.asarray(pose, dtype=float)
    if pose.shape != (3,) or not np.isfinite(pose).all():
        raise ValueError("SE(2) pose requires finite [x,y,yaw]")
    x, y, theta = pose
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, x], [s, c, y], [0., 0., 1.]])


def validate_transform(matrix):
    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (3, 3) or not np.isfinite(matrix).all() or not np.allclose(matrix[2], [0, 0, 1]):
        raise ValueError("Expected a finite SE(2) matrix")
    r = matrix[:2, :2]
    if not np.allclose(r.T@r, np.eye(2), atol=1e-6) or not np.isclose(np.linalg.det(r), 1., atol=1e-6):
        raise ValueError("Transform must be a proper rigid SE(2) transform")
    return matrix


def transform(xy, matrix):
    matrix = validate_transform(matrix)
    return np.asarray(xy)@matrix[:2, :2].T+matrix[:2, 2]
