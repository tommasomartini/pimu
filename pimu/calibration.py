import logging

import numpy as np

import pimu.imu as pimu

logger = logging.getLogger(__name__)


def calibrate(bus, device_address, num_calibration_samples, afs_sel, fs_sel):
    input('Place the IMU on a flat surface and press '
          'any key when you are ready. ')

    logger.info('Start calibration')

    calibration_samples = np.zeros((num_calibration_samples, 6))
    sample_idx = 0
    while sample_idx < num_calibration_samples:
        acc_x, acc_y, acc_z = \
            pimu.read_accelerometer_data(bus, device_address, afs_sel)
        gyro_x, gyro_y, gyro_z = \
            pimu.read_gyroscope_data(bus, device_address, fs_sel)

        calibration_samples[sample_idx] = \
            np.array([acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z])

        sample_idx += 1

    calibration = np.mean(calibration_samples, axis=0)

    logger.info('Calibration complete')

    return tuple(calibration)
