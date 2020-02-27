import logging
import smbus

import pimu.mpu6050.constants as const
import pimu.mpu6050.initialization as init
import pimu.mpu6050.registers as regs
import pimu.mpu6050.interface as interface
import pimu.mpu6050.sensor as sensor
from pimu.imu import Imu

_logger = logging.getLogger(__name__)


class MPU6050(Imu):

    def __init__(self, gyro_sensitivity, acc_sensitivity):
        super().__init__()

        self._gyro_sensitivity = const.GYRO_SENSITIVITY[gyro_sensitivity]
        self._acc_sensitivity = const.ACCEL_SENSITIVITY[acc_sensitivity]

        # The argument is 0 for older versions of the board.
        self._bus = smbus.SMBus(1)
        self._device_address = regs.MPU6050_ADDRESS

        gyro_full_scale_range = const.FS_SEL[gyro_sensitivity]
        acc_full_scale_range = const.AFS_SEL[acc_sensitivity]
        init.initialize(self._bus,
                        self._device_address,
                        gyro_full_scale_range=gyro_full_scale_range,
                        acc_full_scale_range=acc_full_scale_range)

        _logger.info('{} initialized'.format(self.__class__.__name__))

        _logger.debug('Gyroscope sensitivity {} deg/s'.format(gyro_sensitivity))
        _logger.debug('Accelerometer sensitivity: {}'.format(acc_sensitivity))

    def read_next(self):
        accelerometer_data = \
            sensor.read_accelerometer_data(bus=self._bus,
                                           device_address=self._device_address,
                                           sensitivity=self._acc_sensitivity)

        temperature_deg = \
            sensor.read_temperature_data(bus=self._bus,
                                         device_address=self._device_address)

        gyroscope_data = \
            sensor.read_gyroscope_data(bus=self._bus,
                                       device_address=self._device_address,
                                       sensitivity=self._gyro_sensitivity)

        acc_x, acc_y, acc_z = \
            interface.accelerometer_data_to_board_system(*accelerometer_data)
        acc_x -= self._acc_x_bias
        acc_y -= self._acc_y_bias
        acc_z -= (self._acc_z_bias + 1)

        gyro_x, gyro_y, gyro_z = \
            interface.gyroscope_data_to_board_system(*gyroscope_data)
        gyro_x -= self._gyro_x_bias
        gyro_y -= self._gyro_y_bias
        gyro_z -= self._gyro_z_bias

        return acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, temperature_deg
