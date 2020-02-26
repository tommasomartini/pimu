import unittest

import pimu.mpu6050.interface as interface


class AccelerometerDataToBoardSystemTest(unittest.TestCase):

    def test_three_axes_rotation(self):
        acc_x = 0.1
        acc_y = 0.2
        acc_z = 0.3
        expected_output = (0.2, 0.1, -0.3)
        output = interface.accelerometer_data_to_board_system(acc_x=acc_x,
                                                              acc_y=acc_y,
                                                              acc_z=acc_z)
        self.assertTupleEqual(expected_output, output)


class GyroscopeDataToBoardSystemTest(unittest.TestCase):

    def test_three_axes_rotation(self):
        gyro_x = 0.1
        gyro_y = 0.2
        gyro_z = 0.3
        expected_output = (0.2, 0.1, -0.3)
        output = interface.gyroscope_data_to_board_system(gyro_x=gyro_x,
                                                          gyro_y=gyro_y,
                                                          gyro_z=gyro_z)
        self.assertTupleEqual(expected_output, output)


if __name__ == '__main__':
    unittest.main()
