import logging
import time

import numpy as np
from tqdm import tqdm

import pimu.sensorboard as sb

_logger = logging.getLogger(__name__)


class Imu:

    NUMBER_OF_CALIBRATION_SAMPLES = 1000

    def __init__(self):
        self._yaw_rad = 0
        self._pitch_rad = 0
        self._roll_rad = 0
        self._prev_time_ms = int(round(time.time() * 1000))

        # Bias that can be removed through calibration.
        self._acc_x_bias = 0
        self._acc_y_bias = 0
        self._acc_z_bias = 0
        self._gyro_x_bias = 0
        self._gyro_y_bias = 0
        self._gyro_z_bias = 0

    def read_next(self):
        raise NotImplementedError('Only derived classes are supposed '
                                  'to implement this function')

    def read_yaw_pitch_roll(self):
        acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, *other = self.read_next()
        curr_time_ms = int(round(time.time() * 1000))
        delta_time_ms = curr_time_ms - self._prev_time_ms
        self._prev_time_ms = curr_time_ms

        acc_pitch_rad, acc_roll_rad = \
            sb.pitch_and_roll_from_accelerometer_data(acc_x, acc_y, acc_z)

        gyro_yaw_delta_rad, gyro_pitch_delta_rad, gyro_roll_delta_rad = \
            sb.gyroscope_data_to_taitbryan_deltas(gyro_x, gyro_y, gyro_z,
                                                  delta_time_ms=delta_time_ms)

        self._yaw_rad += gyro_yaw_delta_rad
        self._pitch_rad = 0.8 * acc_pitch_rad + \
                          0.2 * (self._pitch_rad + gyro_pitch_delta_rad)
        self._roll_rad = 0.8 * acc_roll_rad + \
                         0.2 * (self._roll_rad + gyro_roll_delta_rad)

        output = self._yaw_rad, self._pitch_rad, self._roll_rad, *other
        return output

    def calibrate(self):
        input('Place the IMU on a flat surface and press '
              'any key when you are ready. ')

        _logger.info('Start calibration')

        calibration_samples = np.zeros((self.NUMBER_OF_CALIBRATION_SAMPLES, 6))
        for sample_idx in tqdm(range(self.NUMBER_OF_CALIBRATION_SAMPLES),
                               desc='Calibrating',
                               leave=False):
            acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, _ = self.read_next()
            calibration_samples[sample_idx] = \
                np.array([acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z])

        calibration = np.mean(calibration_samples, axis=0)
        self._acc_x_bias = calibration[0]
        self._acc_y_bias = calibration[1]
        self._acc_z_bias = calibration[2]

        self._gyro_x_bias = calibration[3]
        self._gyro_y_bias = calibration[4]
        self._gyro_z_bias = calibration[5]

        _logger.info('Calibration complete')
