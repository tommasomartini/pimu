import unittest

import numpy as np

import pimu.sensorboard as sb

_PI = np.pi
_SQRT3 = np.sqrt(3)


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

        yaw, pitch, roll = sb.accelerometer_data_to_taitbryan(acc_x=acc_x,
                                                              acc_y=acc_y,
                                                              acc_z=acc_z)
        self.assertAlmostEqual(expected_yaw, yaw, places=7)
        self.assertAlmostEqual(expected_pitch, pitch, places=7)
        self.assertAlmostEqual(expected_roll, roll, places=7)

    def test_only_roll_applied(self):
        acc_x = 0
        acc_y = 0.5
        acc_z = _SQRT3 / 2
        expected_yaw = 0
        expected_pitch = 0
        expected_roll = np.deg2rad(30)

        yaw, pitch, roll = sb.accelerometer_data_to_taitbryan(acc_x=acc_x,
                                                              acc_y=acc_y,
                                                              acc_z=acc_z)
        self.assertAlmostEqual(expected_yaw, yaw, places=7)
        self.assertAlmostEqual(expected_pitch, pitch, places=7)
        self.assertAlmostEqual(expected_roll, roll, places=7)

    def test_only_pitch_applied(self):
        acc_x = -0.5
        acc_y = 0
        acc_z = _SQRT3 / 2
        expected_yaw = 0
        expected_pitch = np.deg2rad(30)
        expected_roll = 0

        yaw, pitch, roll = sb.accelerometer_data_to_taitbryan(acc_x=acc_x,
                                                              acc_y=acc_y,
                                                              acc_z=acc_z)
        self.assertAlmostEqual(expected_yaw, yaw, places=7)
        self.assertAlmostEqual(expected_pitch, pitch, places=7)
        self.assertAlmostEqual(expected_roll, roll, places=7)

    def test_board_lying_on_right_side(self):
        acc_x = 0
        acc_y = 1
        acc_z = 0
        expected_yaw = 0
        expected_pitch = 0
        expected_roll = _PI / 2

        yaw, pitch, roll = sb.accelerometer_data_to_taitbryan(acc_x=acc_x,
                                                              acc_y=acc_y,
                                                              acc_z=acc_z)
        self.assertAlmostEqual(expected_yaw, yaw, places=7)
        self.assertAlmostEqual(expected_pitch, pitch, places=7)
        self.assertAlmostEqual(expected_roll, roll, places=7)

    def test_board_lying_on_bottom_side(self):
        acc_x = -1
        acc_y = 0
        acc_z = 0
        expected_yaw = 0
        expected_pitch = _PI / 2
        expected_roll = 0

        yaw, pitch, roll = sb.accelerometer_data_to_taitbryan(acc_x=acc_x,
                                                              acc_y=acc_y,
                                                              acc_z=acc_z)
        self.assertAlmostEqual(expected_yaw, yaw, places=7)
        self.assertAlmostEqual(expected_pitch, pitch, places=7)
        self.assertAlmostEqual(expected_roll, roll, places=7)

    # def test_no_faces_parallel_to_ground(self):
    #     acc_x = -0.5
    #     acc_y = _SQRT3 / 4
    #     acc_z = (_SQRT3 / 2) ** 2
    #     expected_yaw = 0
    #     expected_pitch = np.deg2rad(30)
    #     expected_roll = np.deg2rad(30)
    #
    #     yaw, pitch, roll = sb.accelerometer_data_to_taitbryan(acc_x=acc_x,
    #                                                           acc_y=acc_y,
    #                                                           acc_z=acc_z)
    #     self.assertAlmostEqual(expected_yaw, yaw, places=7)
    #     self.assertAlmostEqual(expected_pitch, pitch, places=7)
    #     self.assertAlmostEqual(expected_roll, roll, places=7)


if __name__ == '__main__':
    unittest.main()
