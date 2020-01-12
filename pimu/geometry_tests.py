import unittest

import pimu.geometry as geom


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


if __name__ == '__main__':
    unittest.main()
