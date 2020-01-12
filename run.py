import json
import logging
import smbus
import socket
from time import sleep

import numpy as np

import pimu.calibration as calib
import pimu.geometry as geom
import pimu.imu as pimu
import pimu.init as init
import pimu.registers as regs

RATE = 2    # Hz
LOGGING_LEVEL = logging.WARNING
FS_SEL = '250'
AFS_SEL = '2g'
CALIBRATE = False
NUM_CALIBRATION_SAMPLES = 5 * RATE  # calibration should take 5s

logging.basicConfig(level=LOGGING_LEVEL, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def _log_accelerometer(x, y, z):
    value_format = '{: 6.3f}'
    values_format = ', '.join([value_format] * 3)
    unformatted_string = 'Accelerometer: ' + values_format
    formatted_string = unformatted_string.format(x, y, z)
    logger.info(formatted_string)


def _log_temperature(val):
    logger.info('Temperature: {: 6.3f}'.format(val))


def _log_gyroscope(x, y, z):
    value_format = '{: 7.3f}'
    values_format = ', '.join([value_format] * 3)
    unformatted_string = 'Gyroscope: ' + values_format
    formatted_string = unformatted_string.format(x, y, z)
    logger.info(formatted_string)


def _accelerometer_data_to_taitbryan(acc_x, acc_y, acc_z):
    gravity_vec = np.array([acc_x, 0, acc_z])

    # The Z axis of the world coordinate system.
    reference_z = - gravity_vec / np.linalg.norm(gravity_vec)

    # Assume the world's Y axis is in the plane of the world's Z axis and the
    # board's Y axis.
    board_x_axis = np.array([1, 0, 0])
    reference_y = np.cross(reference_z, board_x_axis)
    reference_x = np.cross(reference_y, reference_z)

    # This is the matrix rotating the world's axes to overlap the board's axes.
    world2board_matrix = np.array([reference_x, reference_y, reference_z]).T

    # Go from a rotation matrix to the Tait-Bryan angles.
    yaw, roll, pitch = \
        geom.tait_bryan_angles_from_rotation_matrix(world2board_matrix)

    return yaw, roll, pitch


def main():
    logger.info('Start up')

    UDP_IP = '127.0.0.1'
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    ######################################à

    sleep_time = 1. / RATE
    logger.info('Begin data reading')
    while True:
        acc_x, acc_y, acc_z = np.deg2rad(np.random.rand(3) / 10000)
        yaw, roll, pitch = _accelerometer_data_to_taitbryan(acc_x, acc_y, acc_z)
        msg = json.dumps({
            'yaw': float(yaw),
            'roll': float(roll),
            'pitch': float(pitch),
        })
        sock.sendto(bytes(msg, 'utf-8'), (UDP_IP, UDP_PORT))

        sleep(sleep_time)

    return

    #####################################

    # The argument is 0 for older version boards.
    bus = smbus.SMBus(1)

    device_address = regs.MPU6050_ADDRESS

    config = {
        'fs_sel': FS_SEL,
        'afs_sel': AFS_SEL,
    }
    init.mpu_init(bus, device_address, config)

    if CALIBRATE:
        calib_values = calib.calibrate(
            bus=bus,
            device_address=device_address,
            num_calibration_samples=NUM_CALIBRATION_SAMPLES,
            afs_sel=AFS_SEL,
            fs_sel=FS_SEL,
        )
        (err_acc_x, err_acc_y, err_acc_z,
         err_gyro_x, err_gyro_y, err_gyro_z) = calib_values

    sleep_time = 1. / RATE
    logger.info('Begin data reading')
    while True:
        acc_x, acc_y, acc_z = \
            pimu.read_accelerometer_data(bus, device_address, afs_sel=AFS_SEL)
        temp_deg = pimu.read_temperature_data(bus, device_address)
        gyro_x, gyro_y, gyro_z = \
            pimu.read_gyroscope_data(bus, device_address, fs_sel=FS_SEL)

        yaw, roll, pitch = _accelerometer_data_to_taitbryan(acc_x, acc_y, acc_z)
        msg = json.dumps({
            'yaw': yaw,
            'roll': roll,
            'pitch': pitch,
        })
        sock.sendto(bytes(msg, "ascii"), (UDP_IP, UDP_PORT))

        if CALIBRATE:
            acc_x -= err_acc_x
            acc_y -= err_acc_y
            acc_z -= (err_acc_z + 1)

            gyro_x -= err_gyro_x
            gyro_y -= err_gyro_y
            gyro_z -= err_gyro_z

        _log_accelerometer(acc_x, acc_y, acc_z)
        _log_temperature(temp_deg)
        _log_gyroscope(gyro_x, gyro_y, gyro_z)

        logger.info('')

        sleep(sleep_time)


if __name__ == '__main__':
    main()
