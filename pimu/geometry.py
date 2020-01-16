"""This module gathers utility functions for geometric operations.

Every time we deal with a rotation, we adopt one of the following (equivalent)
conventions:
* intrinsic rotations: x - y'- z" (yaw - pitch - roll)
* extrinsic rotations: z - y - x

The relation between axes and Tait-Bryan angles here used holds if the axes
are so oriented:
* X axis: back to front
* Y axis: left to right
* Z axis: top to bottom.
An advantage of this convention is that after a rotation, the yaw is still
the angle of the rotated object around the "gravity vector" and the pitch
is still the angle of the object with the ground plane.

The adopted convention rotates an object, not a system. That is, given an
initial system U and a point P in U, the operation:
    Q = <rotation_matrix, P>
returns a vector Q in U coordinates obtained by rotating P.

See:
    https://en.wikipedia.org/wiki/Euler_angles#Tait%E2%80%93Bryan_angles
"""
import numpy as np


_PI = np.pi
_EPS = 1e-6


def _almost_equal(v1, v2, tolerance=None):
    """Returns True if the two input values differ by less then a threshold.
    Otherwise returns False.
    """
    tolerance = np.abs(tolerance or _EPS)
    return np.abs(v1 - v2) < tolerance


def build_rotation_matrix(yaw_rad, pitch_rad, roll_rad):
    """Builds and returns a rotation matrix.

    The applied rotation of the object in the reference system is the series
    of intrinsic rotations: x - y'- z".

    Args:
        yaw_rad (float): Rotation around the X axis in radians.
        pitch_rad (float): Rotation around the Y axis in radians.
        roll_rad (float): Rotation around the Z axis in radians.

    Returns:
        A numpy array with shape (3, 3).
    """
    yaw_matrix = np.array([
        [1, 0, 0],
        [0, np.cos(yaw_rad), -np.sin(yaw_rad)],
        [0, np.sin(yaw_rad), np.cos(yaw_rad)],
    ])
    pitch_matrix= np.array([
        [np.cos(pitch_rad), 0, np.sin(pitch_rad)],
        [0, 1, 0],
        [-np.sin(pitch_rad), 0, np.cos(pitch_rad)],
    ])
    roll_matrix = np.array([
        [np.cos(roll_rad), -np.sin(roll_rad), 0],
        [np.sin(roll_rad), np.cos(roll_rad), 0],
        [0, 0, 1],
    ])
    rotation_matrix = yaw_matrix @ pitch_matrix @ roll_matrix
    return rotation_matrix


def tait_bryan_angles_from_rotation_matrix(rotation_matrix):
    """Returns a tuple of Tait-Bryan angles in radians (yaw, roll, pitch)
    that generated the provided rotation matrix.

    See:
        https://www.gregslabaugh.net/publications/euler.pdf

    Note:
        Different Tait-Bryan angles may generate the same rotation matrix.

    Args:
        rotation_matrix (:obj:`numpy.array`): Array with shape (3, 3).

    Returns:
        A tuple of Tait-Bryan angles in radians (yaw, roll, pitch).

    Raises:
        ValueError: Invalid rotation matrix shape.
    """
    if rotation_matrix.shape != (3, 3):
        raise ValueError('Expected shape of the rotation matrix is (3, 3), '
                         'but provided has shape '
                         '{}'.format(rotation_matrix.shape))

    R31 = rotation_matrix[2, 0]

    if _almost_equal(R31, - 1):
        roll = _PI / 2
        yaw = 0

        R12 = rotation_matrix[0, 1]
        R13 = rotation_matrix[0, 2]
        pitch = np.arctan2(R12, R13)

        return yaw, roll, pitch

    if _almost_equal(R31, 1):
        roll = - _PI / 2
        yaw = 0

        R12 = rotation_matrix[0, 1]
        R13 = rotation_matrix[0, 2]
        pitch = np.arctan2(-R12, -R13)

        return yaw, roll, pitch

    R11 = rotation_matrix[0, 0]
    R21 = rotation_matrix[1, 0]
    R31 = rotation_matrix[2, 0]
    R32 = rotation_matrix[2, 1]
    R33 = rotation_matrix[2, 2]

    roll = np.arcsin(-R31)
    pitch = np.arctan2(R32 / np.cos(roll), R33 / np.cos(roll))
    yaw = np.arctan2(R21 / np.cos(roll), R11 / np.cos(roll))

    return yaw, roll, pitch
