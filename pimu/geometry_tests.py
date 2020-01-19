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


class BuildRotationMatrixTest(unittest.TestCase):

    @staticmethod
    def test_only_yaw():
        yaw_rad = np.deg2rad(30)
        pitch_rad = 0
        roll_rad = 0
        expected_rotation_matrix = np.array([
            [_SQRT3 / 2, -0.5, 0],
            [0.5, _SQRT3 / 2, 0],
            [0, 0, 1],
        ])

        rotation_matrix = \
            geom.build_rotation_matrix(yaw_rad, pitch_rad, roll_rad)
        np.testing.assert_almost_equal(expected_rotation_matrix,
                                       rotation_matrix)

    @staticmethod
    def test_only_pitch():
        yaw_rad = 0
        pitch_rad = np.deg2rad(30)
        roll_rad = 0
        expected_rotation_matrix = np.array([
            [_SQRT3 / 2, 0, 0.5],
            [0, 1, 0],
            [-0.5, 0, _SQRT3 / 2],
        ])

        rotation_matrix = \
            geom.build_rotation_matrix(yaw_rad, pitch_rad, roll_rad)
        np.testing.assert_almost_equal(expected_rotation_matrix,
                                       rotation_matrix)

    @staticmethod
    def test_only_roll():
        yaw_rad = 0
        pitch_rad = 0
        roll_rad = np.deg2rad(30)
        expected_rotation_matrix = np.array([
            [1, 0, 0],
            [0, _SQRT3 / 2, -0.5],
            [0, 0.5, _SQRT3 / 2],
        ])

        rotation_matrix = \
            geom.build_rotation_matrix(yaw_rad, pitch_rad, roll_rad)
        np.testing.assert_almost_equal(expected_rotation_matrix,
                                       rotation_matrix)

    @staticmethod
    def test_yaw_pitch_roll_together():
        yaw_rad = np.deg2rad(30)
        pitch_rad = np.deg2rad(45)
        roll_rad = np.deg2rad(10)
        expected_rotation_matrix = np.array([
            [0.6123725, -0.3860665,  0.6898932],
            [0.3535534,  0.9142624,  0.1977984],
            [-0.7071068,  0.1227878,  0.6963642],
        ])

        rotation_matrix = \
            geom.build_rotation_matrix(yaw_rad, pitch_rad, roll_rad)
        np.testing.assert_almost_equal(expected_rotation_matrix,
                                       rotation_matrix)


class TaitBryanAnglesFromRotationMatrixTest(unittest.TestCase):

    def test_pitch_not_90_deg(self):
        expected_yaw = np.deg2rad(15)
        expected_pitch = np.deg2rad(45)
        expected_roll = np.deg2rad(20)
        rotation_matrix = np.array([
            [0.6830127, -0.0096062,  0.7303433],
            [0.1830127,  0.9702674, -0.1583904],
            [-0.7071068,  0.2418448,  0.6644630],
        ])

        yaw, pitch, roll = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)

    def test_pitch_plus_90_deg(self):
        expected_yaw = 0
        expected_pitch = _PI / 2
        expected_roll = np.deg2rad(30)
        rotation_matrix = np.array([
            [0., 0.5, _SQRT3 / 2],
            [0., _SQRT3 / 2, -0.5],
            [-1., 0., 0.],
        ])

        yaw, pitch, roll = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)

    def test_pitch_minus_90_deg(self):
        expected_yaw = 0
        expected_pitch = - _PI / 2
        expected_roll = np.deg2rad(-30)
        rotation_matrix = np.array([
            [0., 0.5, -_SQRT3 / 2],
            [0., _SQRT3 / 2, 0.5],
            [1., 0., 0.],
        ])

        yaw, pitch, roll = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)

    def test_only_yaw(self):
        expected_yaw = np.deg2rad(30)
        expected_pitch = 0
        expected_roll = 0
        rotation_matrix = np.array([
            [_SQRT3 / 2, -0.5, 0],
            [0.5, _SQRT3 / 2, 0],
            [0, 0, 1],
        ])

        yaw, pitch, roll = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)

    def test_only_pitch(self):
        expected_yaw = 0
        expected_pitch = np.deg2rad(30)
        expected_roll = 0
        rotation_matrix = np.array([
            [_SQRT3 / 2, 0, -0.5],
            [0, 1, 0],
            [-0.5, 0, _SQRT3 / 2],
        ])

        yaw, pitch, roll = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)

    def test_only_roll(self):
        expected_yaw = 0
        expected_pitch = 0
        expected_roll = np.deg2rad(30)
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, _SQRT3 / 2, -0.5],
            [0, 0.5, _SQRT3 / 2],
        ])

        yaw, pitch, roll = \
            geom.tait_bryan_angles_from_rotation_matrix(rotation_matrix)

        self.assertAlmostEqual(yaw, expected_yaw, places=6)
        self.assertAlmostEqual(pitch, expected_pitch, places=6)
        self.assertAlmostEqual(roll, expected_roll, places=6)

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
