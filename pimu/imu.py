import logging
import time

import numpy as np
from tqdm import tqdm

import pimu.sensorboard as sb

_logger = logging.getLogger(__name__)


class Imu:

    NUMBER_OF_CALIBRATION_SAMPLES = 1000

    def __init__(self):
        self._yaw = 0
        self._pitch = 0
        self._roll = 0
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

        acc_pitch, acc_roll = \
            sb.pitch_and_roll_from_accelerometer_data(acc_x, acc_y, acc_z)

        gyro_yaw_delta, gyro_pitch_delta, gyro_roll_delta = \
            sb.gyroscope_data_to_taitbryan_deltas(gyro_x, gyro_y, gyro_z,
                                                  delta_time_ms=delta_time_ms)

        self._yaw += gyro_yaw_delta
        self._pitch = 0.5 * acc_pitch + 0.5 * (self._pitch + gyro_pitch_delta)
        self._roll = 0.5 * acc_roll + 0.5 * (self._roll + gyro_roll_delta)

        output = self._yaw, self._pitch, self._roll, *other
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
