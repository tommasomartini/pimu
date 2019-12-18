import logging
import smbus
from time import sleep

import pimu.init as init
import pimu.pimu as pimu
import pimu.registers as regs

RATE = 1    # Hz
LOGGING_LEVEL = logging.INFO
FS_SEL = '250'
AFS_SEL = '2g'

logging.basicConfig(level=LOGGING_LEVEL, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def _log_accelerometer(x, y, z):
    value_format = '{: 6.3}'
    values_format = ', '.join([value_format] * 3)
    unformatted_string = 'Accelerometer: ' + values_format
    formatted_string = unformatted_string.format(x, y, z)
    logger.info(formatted_string)


def _log_temperature(val):
    logger.info('Temperature: {: 6.3}'.format(val))


def _log_gyroscope(x, y, z):
    value_format = '{: 6.2}'
    values_format = ', '.join([value_format] * 3)
    unformatted_string = 'Gyroscope: ' + values_format
    formatted_string = unformatted_string.format(x, y, z)
    logger.info(formatted_string)


def main():
    logger.info('Start up')
    _log_accelerometer(1., 2., 3.)
    return

    # The argument is 0 for older version boards.
    bus = smbus.SMBus(1)

    device_address = regs.MPU6050_ADDRESS

    config = {
        'fs_sel': FS_SEL,
        'afs_sel': AFS_SEL,
    }
    init.mpu_init(bus, device_address, config)

    sleep_time = 1. / RATE
    logger.info('Begin data reading')
    while True:
        acc_x, acc_y, acc_z = \
            pimu.read_accelerometer_data(bus, device_address, afs_sel=AFS_SEL)
        temp_deg = pimu.read_temperature_data(bus, device_address)
        gyro_x, gyro_y, gyro_z = \
            pimu.read_gyroscope_data(bus, device_address, fs_sel=FS_SEL)

        _log_accelerometer(acc_x, acc_y, acc_z)
        _log_temperature(temp_deg)
        _log_gyroscope(gyro_x, gyro_y, gyro_z)

        logger.info('')

        sleep(sleep_time)


if __name__ == '__main__':
    main()
