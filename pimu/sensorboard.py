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
    """Translates the gyroscope data measurements from the native coordinate
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
    return np.deg2rad(gyro_y), np.deg2rad(gyro_x), -np.deg2rad(gyro_z)


def gyroscope_data_to_taitbryan(gyro_x, gyro_y, gyro_z, delta_time_ms):
    """Returns yaw, pitch and roll from the gyroscope data.

    In this function the system in use is aligned with the sensor board as
    follows:
        X axis: forward
        Y axis: to the right
        Z axis: downward

    The output Tait-Bryan angles describe the rotation of the body from its
    current position that occurred in the last time interval.

    Args:
        gyro_x (float): Angular velocity in deg/s around the board's X axis.
        gyro_y (float): Angular velocity in deg/s around the board's Y axis.
        gyro_z (float): Angular velocity in deg/s around the board's Z axis.
        delta_time_ms (int): Time interval in milliseconds between the previous
            measurement and the current one.

    Returns:
        A tuple (yaw, pitch, roll) in radians, describing the rotation of the
        board from its current position that occurred in the givent
        time interval.
    """
    delta_yaw = gyro_z * delta_time_ms / 1000
    delta_pitch = gyro_y * delta_time_ms / 1000
    delta_roll = gyro_x * delta_time_ms / 1000
    return delta_yaw, delta_pitch, delta_roll


def accelerometer_data_to_taitbryan(acc_x, acc_y, acc_z):
    """Returns yaw, pitch and roll from the accelerometer data.

    In this function the system in use is aligned with the sensor board as
    follows:
        X axis: forward
        Y axis: to the right
        Z axis: downward

    The output Tait-Bryan angles describe the rotation of the body from the
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


def TEMP_pitch_roll_from_accelerometer(acc_x, acc_y, acc_z):
    """

    See: https://www.nxp.com/files-static/sensors/doc/app_note/AN3461.pdf
    """
    acc_vector = np.array([acc_x, acc_y, acc_z])
    gravity = acc_vector / np.linalg.norm(acc_vector)
    x, y, z = gravity

    yaw = 0
    # pitch = np.arctan(-x / np.sqrt(y ** 2 + z ** 2))
    # roll = np.arctan(y / z)

    pitch = np.arctan2(-x, np.sqrt(y ** 2 + z ** 2))
    roll = np.arctan2(y, z)

    return yaw, pitch, roll
