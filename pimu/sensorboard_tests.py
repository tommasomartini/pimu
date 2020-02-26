import unittest

import numpy as np

import pimu.sensorboard as sb

_PI = np.pi
_SQRT3 = np.sqrt(3)


class GyroscopeDataToTaitBryanDeltasTest(unittest.TestCase):

    def test_three_axes_rotation(self):
        # Measurements given in degrees/s.
        gyro_x = 1
        gyro_y = 2
        gyro_z = 3
        delta_time_ms = 100
        expected_output = (np.deg2rad(0.3), np.deg2rad(0.2), np.deg2rad(0.1))
        output = \
            sb.gyroscope_data_to_taitbryan_deltas(gyro_x=gyro_x,
                                                  gyro_y=gyro_y,
                                                  gyro_z=gyro_z,
                                                  delta_time_ms=delta_time_ms)
        np.testing.assert_almost_equal(output, expected_output)


class PitchAndRollFromAccelerometerDataTest(unittest.TestCase):

    def test_board_aligned_with_reference_frame(self):
        acc_x = 0
        acc_y = 0
        acc_z = 1
        expected_pitch = 0
        expected_roll = 0
        pitch, roll = \
            sb.pitch_and_roll_from_accelerometer_data(acc_x=acc_x,
                                                      acc_y=acc_y,
                                                      acc_z=acc_z)
        self.assertAlmostEqual(expected_pitch, pitch, places=7)
        self.assertAlmostEqual(expected_roll, roll, places=7)

    def test_only_roll_applied(self):
        acc_x = 0
        acc_y = 0.5
        acc_z = _SQRT3 / 2
        expected_pitch = 0
        expected_roll = np.deg2rad(30)
        pitch, roll = \
            sb.pitch_and_roll_from_accelerometer_data(acc_x=acc_x,
                                                      acc_y=acc_y,
                                                      acc_z=acc_z)
        self.assertAlmostEqual(expected_pitch, pitch, places=7)
        self.assertAlmostEqual(expected_roll, roll, places=7)

    def test_only_pitch_applied(self):
        acc_x = -0.5
        acc_y = 0
        acc_z = _SQRT3 / 2
        expected_pitch = np.deg2rad(30)
        expected_roll = 0
        pitch, roll = \
            sb.pitch_and_roll_from_accelerometer_data(acc_x=acc_x,
                                                      acc_y=acc_y,
                                                      acc_z=acc_z)
        self.assertAlmostEqual(expected_pitch, pitch, places=7)
        self.assertAlmostEqual(expected_roll, roll, places=7)

    def test_board_lying_on_right_side(self):
        acc_x = 0
        acc_y = 1
        acc_z = 0
        expected_pitch = 0
        expected_roll = _PI / 2
        pitch, roll = \
            sb.pitch_and_roll_from_accelerometer_data(acc_x=acc_x,
                                                      acc_y=acc_y,
                                                      acc_z=acc_z)
        self.assertAlmostEqual(expected_pitch, pitch, places=7)
        self.assertAlmostEqual(expected_roll, roll, places=7)

    def test_board_lying_on_bottom_side(self):
        acc_x = -1
        acc_y = 0
        acc_z = 0
        expected_pitch = _PI / 2
        expected_roll = 0
        pitch, roll = \
            sb.pitch_and_roll_from_accelerometer_data(acc_x=acc_x,
                                                      acc_y=acc_y,
                                                      acc_z=acc_z)
        self.assertAlmostEqual(expected_pitch, pitch, places=7)
        self.assertAlmostEqual(expected_roll, roll, places=7)

    def test_no_faces_parallel_to_ground(self):
        acc_x = -0.5
        acc_y = _SQRT3 / 4
        acc_z = (_SQRT3 / 2) ** 2
        expected_pitch = np.deg2rad(30)
        expected_roll = np.deg2rad(30)
        pitch, roll = \
            sb.pitch_and_roll_from_accelerometer_data(acc_x=acc_x,
                                                      acc_y=acc_y,
                                                      acc_z=acc_z)
        self.assertAlmostEqual(expected_pitch, pitch, places=7)
        self.assertAlmostEqual(expected_roll, roll, places=7)


if __name__ == '__main__':
    unittest.main()
