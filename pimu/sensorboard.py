import numpy as np


def gyroscope_data_to_taitbryan_deltas(gyro_x, gyro_y, gyro_z, delta_time_ms):
    """Returns a delta for yaw, pitch and roll in radians from the gyroscope
    data, since the last measurement.

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
        board that occurred in the last given time interval.
    """
    delta_yaw_rad = np.deg2rad(gyro_z) * delta_time_ms / 1000
    delta_pitch_rad = np.deg2rad(gyro_y) * delta_time_ms / 1000
    delta_roll_rad = np.deg2rad(gyro_x) * delta_time_ms / 1000
    return delta_yaw_rad, delta_pitch_rad, delta_roll_rad


def pitch_and_roll_from_accelerometer_data(acc_x, acc_y, acc_z):
    """Returns pitch and roll values in radians from 3-axes accelerometer data.

    In this function the system in use is aligned with the sensor board as
    follows:
        X axis: forward
        Y axis: to the right
        Z axis: downward

    The output Tait-Bryan angles describe the rotation of the body from the
    reference frame, where the Z axis is directed along the Gravity direction.
    The rotation occurs as:
    1) pitch: rotation around the Y axis;
    2) roll: rotation around the new X axis.

    Since the only force acting on the sensor is the Gravity, we cannot
    infer the yaw of the board.

    See: https://www.nxp.com/files-static/sensors/doc/app_note/AN3461.pdf

    Args:
        acc_x (float): Acceleration in g units along the board's X axis.
        acc_y (float): Acceleration in g units along the board's Y axis.
        acc_z (float): Acceleration in g units along the board's Z axis.

    Returns:
        A tuple (pitch, roll) in radians, describing the rotation of the
        board from the reference frame.
    """
    acc_vector = np.array([acc_x, acc_y, acc_z])
    gravity = acc_vector / np.linalg.norm(acc_vector)
    gx, gy, gz = gravity
    pitch_rad = np.arctan2(-gx, np.sqrt(gy ** 2 + gz ** 2))
    roll_rad = np.arctan2(gy, gz)
    return pitch_rad, roll_rad
