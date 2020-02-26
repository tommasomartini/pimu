"""This module contains functions to read data from a GY-521 MPU-6050 IMU.

Coordinate system:
* X axis: along the short side of the board, pointing from the side with
  the pins to the opposite side.
* Y axis: along the long side of the board, pointing from the bottom to the top
  of the board, if the side with the pins is held on the left and the chips
  upwards.
* Z axis: found by cross-product between X and Y axes.

Note:
    What above described is the reference system drawn on the top face
    of the board, but the actual values read from the accelerometer seem
    to follow the opposite convention. That's why we negate all the values
    before returning them.
"""
import pimu.mpu6050.constants as const
import pimu.mpu6050.registers as regs


def _complement2_to_signed(value):
    signed_value = value - 2 ** 16 if value > 2 ** 15 else value
    return signed_value


def _read_double_register_data(bus, device_address, address_high, address_low):
    """Reads two 8 bits registers and combines them into a 16 bits value.

    Note:
        The 16 bits values are 2’s complement values.
    """
    high = bus.read_byte_data(device_address, address_high)
    low = bus.read_byte_data(device_address, address_low)
    value = (high << 8) | low
    signed_value = _complement2_to_signed(value)
    return signed_value


_read = _read_double_register_data


################################################################################
# Accelerometer

def _read_raw_accelerometer_data(bus, device_address):
    raw_data = (
        _read(bus, device_address, regs.ACCEL_XOUT_H, regs.ACCEL_XOUT_L),
        _read(bus, device_address, regs.ACCEL_YOUT_H, regs.ACCEL_YOUT_L),
        _read(bus, device_address, regs.ACCEL_ZOUT_H, regs.ACCEL_ZOUT_L),
    )
    return raw_data


def read_accelerometer_data(bus, device_address, afs_sel):
    """Returns a tuple with the accelerometer readings along the X, Y and Z
    axes, in g units (e.g. a reading of 1 means 9.81 m/s/s along a certain
    axis).
    """
    sensitivity = const.ACCEL_SENSITIVITY[afs_sel]
    data = tuple(map(lambda x: - x / sensitivity,
                     _read_raw_accelerometer_data(bus, device_address)))
    return data


################################################################################
# Temperature

def _read_raw_temperature_data(bus, device_address):
    raw_data = _read(bus, device_address, regs.TEMP_OUT_H, regs.TEMP_OUT_L)
    return raw_data


def read_temperature_data(bus, device_address):
    """The implemented conversion is indicated in the datasheet."""
    raw_temp = _read_raw_temperature_data(bus, device_address)
    temp_deg = raw_temp / 340 + 36.53
    return temp_deg


################################################################################
# Gyroscope

def _read_raw_gyroscope_data(bus, device_address):
    raw_data = (
        _read(bus, device_address, regs.GYRO_XOUT_H, regs.GYRO_XOUT_L),
        _read(bus, device_address, regs.GYRO_YOUT_H, regs.GYRO_YOUT_L),
        _read(bus, device_address, regs.GYRO_ZOUT_H, regs.GYRO_ZOUT_L),
    )
    return raw_data


def read_gyroscope_data(bus, device_address, fs_sel):
    """Returns a tuple with the gyroscope readings around the X, Y and Z
    axes, in degrees / second.
    """
    sensitivity = const.GYRO_SENSITIVITY[fs_sel]
    data = tuple(map(lambda x: x / sensitivity,
                     _read_raw_gyroscope_data(bus, device_address)))
    return data
