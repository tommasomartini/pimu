import unittest

import numpy as np

import pimu.sensorboard as sb

_PI = np.pi


class AccelerometerDataToConventionalSystemTest(unittest.TestCase):

    def test_three_axes_rotation(self):
        acc_x = 0.1
        acc_y = 0.2
        acc_z = 0.3
        expected_output = (0.2, 0.1, -0.3)

        output = sb.accelerometer_data_to_conventional_system(acc_x=acc_x,
                                                              acc_y=acc_y,
                                                              acc_z=acc_z)
        self.assertTupleEqual(expected_output, output)


class AccelerometerDataToTaitbryanTest(unittest.TestCase):

    def test_board_aligned_with_reference_frame(self):
        acc_x = 0
        acc_y = 0
        acc_z = 1
        expected_yaw = 0
        expected_pitch = 0
        expected_roll = 0
        expected_output = (expected_yaw, expected_pitch, expected_roll)

        yaw, pitch, roll = sb.accelerometer_data_to_taitbryan(acc_x=acc_x,
                                                              acc_y=acc_y,
                                                              acc_z=acc_z)
        output = (yaw, pitch, roll)

        self.assertTupleEqual(expected_output, output)

    def test_board_lying_on_right_side(self):
        acc_x = 0
        acc_y = 1
        acc_z = 0
        expected_yaw = 0
        expected_pitch = 0
        expected_roll = _PI / 2
        expected_output = (expected_yaw, expected_pitch, expected_roll)

        yaw, pitch, roll = sb.accelerometer_data_to_taitbryan(acc_x=acc_x,
                                                              acc_y=acc_y,
                                                              acc_z=acc_z)
        output = (yaw, pitch, roll)

        self.assertTupleEqual(expected_output, output)


if __name__ == '__main__':
    unittest.main()
