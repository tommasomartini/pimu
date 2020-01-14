import unittest

import numpy as np

import pimu.geometry as geom

_PI = np.pi
_SQRT3 = np.sqrt(3)


class AlmostEqualTest(unittest.TestCase):

    def test_equal_values_return_true(self):
        self.assertTrue(geom._almost_equal(1.2, 1.2))

    def test_close_values_return_true(self):
        self.assertTrue(geom._almost_equal(1.2000001, 1.2))

    def test_different_values_return_false(self):
        self.assertFalse(geom._almost_equal(2.2, 1.2))

    def test_true_with_custom_tolerance(self):
        self.assertTrue(geom._almost_equal(-0.1, 0.1, 0.21))

    def test_false_with_custom_tolerance(self):
        self.assertFalse(geom._almost_equal(-0.1, 0.1, 0.19))

    def test_negative_tolerance(self):
        self.assertTrue(geom._almost_equal(-0.1, 0.1, -0.21))


class TaitBryanAnglesFromRotationMatrix(unittest.TestCase):

    def test_roll_not_90_deg(self):
        expected_yaw = _PI / 4
        expected_roll = _PI / 4
        expected_pitch = _PI / 4
        rotation_matrix = np.array([
            [0.5, -0.1464, 0.8536],
            [0.5, 0.8536, -0.1464],
            [-0.707107, 0.5, 0.5],
        ])

        yaw, roll, pitch = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)

    def test_roll_plus_90_deg(self):
        expected_yaw = 0
        expected_roll = _PI / 2
        expected_pitch = np.deg2rad(30)
        rotation_matrix = np.array([
            [0., 0.5, _SQRT3 / 2],
            [0., _SQRT3 / 2, -0.5],
            [-1., 0., 0.],
        ])

        yaw, roll, pitch = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)

    def test_roll_minus_90_deg(self):
        expected_yaw = 0
        expected_roll = - _PI / 2
        expected_pitch = np.deg2rad(-30)
        rotation_matrix = np.array([
            [0., 0.5, -_SQRT3 / 2],
            [0., _SQRT3 / 2, 0.5],
            [1., 0., 0.],
        ])

        yaw, roll, pitch = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)

    def test_only_yaw(self):
        expected_yaw = np.deg2rad(30)
        expected_roll = 0
        expected_pitch = 0
        rotation_matrix = np.array([
            [_SQRT3 / 2, -0.5, 0],
            [0.5, _SQRT3 / 2, 0],
            [0, 0, 1],
        ])

        yaw, roll, pitch = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)

    def test_only_roll(self):
        expected_yaw = 0
        expected_roll = np.deg2rad(30)
        expected_pitch = 0
        rotation_matrix = np.array([
            [_SQRT3 / 2, 0, -0.5],
            [0, 1, 0],
            [-0.5, 0, _SQRT3 / 2],
        ])

        yaw, roll, pitch = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)

    def test_only_pitch(self):
        expected_yaw = 0
        expected_roll = 0
        expected_pitch = np.deg2rad(30)
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, _SQRT3 / 2, -0.5],
            [0, 0.5, _SQRT3 / 2],
        ])

        yaw, roll, pitch = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)

    def test_invalid_rotation_matrix_shape(self):
        with self.assertRaisesRegex(ValueError,
                                    r'Expected shape of the rotation matrix'):
            geom.tait_bryan_angles_from_rotation_matrix(np.eye(4))

        with self.assertRaisesRegex(ValueError,
                                    r'Expected shape of the rotation matrix'):
            geom.tait_bryan_angles_from_rotation_matrix(np.zeros((2, 3)))

        with self.assertRaisesRegex(ValueError,
                                    r'Expected shape of the rotation matrix'):
            geom.tait_bryan_angles_from_rotation_matrix(np.zeros(3))


if __name__ == '__main__':
    unittest.main()
