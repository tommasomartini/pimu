"""Read Gyro and Accelerometer by Interfacing Raspberry Pi
with MPU6050 using Python.

See: www.electronicwings.com

Registers, addresses and instructions documentation at:
    https://43zrtwysvxb2gf29r5o0athu-wpengine.netdna-ssl.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
"""
import logging
import smbus
from time import sleep

import numpy as np

import pimu.constants as const
import pimu.init as init
import pimu.registers as regs

RATE = 1
NUMBER_CALIBRATION_SAMPLES = 1000
LOGGING_LEVEL = logging.INFO

_sleep_time = 1. / RATE

logging.basicConfig(level=LOGGING_LEVEL, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def _read_double_register_data(bus, device_address, address_high, address_low):
    high = bus.read_byte_data(device_address, address_high)
    low = bus.read_byte_data(device_address, address_low)
    value = (high << 8) | low
    signed_value = value - 2**16 if value > 2**15 else value
    return signed_value


def _read_raw_accelerometer_data(bus, device_address):
    raw_data = (
        _read_double_register_data(bus, device_address, regs.ACCEL_XOUT_H, regs.ACCEL_XOUT_L),
        _read_double_register_data(bus, device_address, regs.ACCEL_YOUT_H, regs.ACCEL_YOUT_L),
        _read_double_register_data(bus, device_address, regs.ACCEL_ZOUT_H, regs.ACCEL_ZOUT_L),
    )
    return raw_data


def read_accelerometer_data(bus, device_address):
    return tuple(map(lambda x: x / const.ACCEL_LSB_SENSITIVITY_2g,
                     _read_raw_accelerometer_data(bus, device_address)))


def _read_raw_temperature_data(bus, device_address):
    raw_data = _read_double_register_data(bus, device_address, regs.TEMP_OUT_H, regs.TEMP_OUT_L)
    return raw_data


def read_temperature_data(bus, device_address):
    raw_temp = _read_raw_temperature_data(bus, device_address)
    temp_deg = raw_temp / 340 + 36.53
    return temp_deg


def _read_raw_gyroscope_data(bus, device_address):
    raw_data = (
        _read_double_register_data(bus, device_address, regs.GYRO_XOUT_H, regs.GYRO_XOUT_L),
        _read_double_register_data(bus, device_address, regs.GYRO_YOUT_H, regs.GYRO_YOUT_L),
        _read_double_register_data(bus, device_address, regs.GYRO_ZOUT_H, regs.GYRO_ZOUT_L),
    )
    return raw_data


def read_gyroscope_data(bus, device_address):
    return tuple(map(lambda x: x / const.GYRO_LSB_SENSITIVITY_250deg,
                     _read_raw_gyroscope_data(bus, device_address)))


def calibrate(bus, device_address):
    do_calibration = input('Press Y to calibrate ').lower() == 'y'
    if not do_calibration:
        return 0, 0, 0, 0, 0, 0

    input('Place the IMU on a flat surface and press '
          'any key when you are ready. ')

    logger.info('Begin calibration')

    calibration_samples = np.zeros((NUMBER_CALIBRATION_SAMPLES, 6))
    sample_idx = 0
    while sample_idx < NUMBER_CALIBRATION_SAMPLES:
        acc_x, acc_y, acc_z = read_accelerometer_data(bus, device_address)
        gyro_x, gyro_y, gyro_z = read_gyroscope_data(bus, device_address)
        calibration_samples[sample_idx] = \
            np.array([acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z])
        sample_idx += 1

    calibration = np.mean(calibration_samples, axis=0)

    print('Calibration complete')

    return tuple(calibration)


def main():
    logger.info('Start up')

    # The argument is 0 for older version boards.
    bus = smbus.SMBus(1)

    device_address = regs.MPU6050_ADDRESS
    init.mpu_init(bus, device_address)

    calib_correction = calibrate(bus, device_address)
    acc_x_err, acc_y_err, acc_z_err, gyro_x_err, gyro_y_err, gyro_z_err = \
        calib_correction

    input('Enter any key to start ')

    logger.info('Begin data reading')
    while True:
        acc_x, acc_y, acc_z = read_accelerometer_data(bus, device_address)
        temp_deg = read_temperature_data(bus, device_address)
        gyro_x, gyro_y, gyro_z = read_gyroscope_data(bus, device_address)

        logger.info('Accelerometer: '
                    '{: 6.3}, {: 6.3}, {: 6.3}'.format(acc_x - acc_x_err,
                                                       acc_y - acc_y_err,
                                                       acc_z - acc_z_err))
        logger.info('Temperature: {: 6.3}'.format(temp_deg))
        logger.info('Gyroscope: '
                    '{: 6.2}, {: 6.2}, {: 6.2}'.format(gyro_x - gyro_x_err,
                                                       gyro_y - gyro_y_err,
                                                       gyro_z - gyro_z_err))
        logger.info('')

        sleep(_sleep_time)


if __name__ == '__main__':
    main()
