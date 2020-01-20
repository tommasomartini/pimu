import numpy as np

import pimu.geometry as geom


def accelerometer_data_to_conventional_system(acc_x, acc_y, acc_z):
    """Translates the accelerometer data measurements from the native coordinate
    system of the sensor to the conventional system.

    Native system:
        X axis: to the right
        Y axis: forward
        Z axis: upward

    Conventional system:
        X axis: forward
        Y axis: to the right
        Z axis: downward
    """
    return acc_y, acc_x, -acc_z


def gyroscope_data_to_conventional_system(gyro_x, gyro_y, gyro_z):
    return np.deg2rad(gyro_y), np.deg2rad(gyro_x), -np.deg2rad(gyro_z)


def accelerometer_data_to_taitbryan(acc_x, acc_y, acc_z):
    """Returns yaw, pitch and roll from the accelerometer data.

    In this function the system in use is aligned with the sensor board as
    follows:
        X axis: forward
        Y axis: to the right
        Z axis: downward

    The output Euler angles describe the rotation of the body from the
    reference frame:
        X axis: pointing North
        Y axis: pointing East
        Z axis: pointing to the ground.

    Args:
        acc_x (float): Acceleration in g units along the board's X axis.
        acc_y (float): Acceleration in g units along the board's Y axis.
        acc_z (float): Acceleration in g units along the board's Z axis.

    Returns:
        A tuple (yaw, pitch, roll) in radians, describing the rotation of the
        board from the reference frame.
    """
    gravity_vec = np.array([acc_x, acc_y, acc_z])

    # The Z axis of the reference coordinate system.
    to_ground = gravity_vec / np.linalg.norm(gravity_vec)

    # The only known force acting on the sensor is gravity, hence we cannot
    # know the yaw of the sensor: we assume the yaw is always zero.

    board_y_axis = np.array([0, 1, 0])
    board_x_axis = np.array([1, 0, 0])

    # Try to use the board's X axis to get a "fake" North.
    to_north = np.cross(board_y_axis, to_ground)
    norm_to_north_vector = np.linalg.norm(to_north)
    if norm_to_north_vector < 1e-6:
        # The board is lying on a side: we need to use the board's X axis to get
        # a "fake" East.
        to_east = np.cross(to_ground, board_x_axis)
        to_east /= np.linalg.norm(to_east)  # should not be needed, in theory
        to_north = np.cross(to_east, to_ground)
    else:
        to_north /= norm_to_north_vector
        to_east = np.cross(to_ground, to_north)

    reference_to_body_rotation_matrix = \
        np.array([to_north, to_east, to_ground])

    yaw, pitch, roll = \
        geom.tait_bryan_angles_from_rotation_matrix(reference_to_body_rotation_matrix)

    return yaw, pitch, roll
