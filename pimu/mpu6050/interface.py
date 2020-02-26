"""This module contains the functions necessary to interface
the GY-521 MPU6050 IMU with other applications.
"""


def accelerometer_data_to_board_system(acc_x, acc_y, acc_z):
    """Translates the accelerometer data measurements from the native coordinate
    system of the sensor to the conventional board system.

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


def gyroscope_data_to_board_system(gyro_x, gyro_y, gyro_z):
    """Translates the gyroscope data measurements from the native coordinate
    system of the sensor to the conventional board system.

    Native system:
        X axis: to the right
        Y axis: forward
        Z axis: upward

    Conventional system:
        X axis: forward
        Y axis: to the right
        Z axis: downward
    """
    return gyro_y, gyro_x, -gyro_z
