class Imu:

    def __init__(self):
        # Bias that can be removed through calibration.
        self._acc_x_bias = 0
        self._acc_y_bias = 0
        self._acc_z_bias = 0

        self._gyro_x_bias = 0
        self._gyro_y_bias = 0
        self._gyro_z_bias = 0

    def calibrate(self):
        pass
