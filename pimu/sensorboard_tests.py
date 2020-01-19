import unittest

import pimu.sensorboard as sb


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


if __name__ == '__main__':
    unittest.main()
