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


