import logging

import numpy as np
from tqdm import tqdm

_logger = logging.getLogger(__name__)


class Imu:

    NUMBER_OF_CALIBRATION_SAMPLES = 1000

    def __init__(self):
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
