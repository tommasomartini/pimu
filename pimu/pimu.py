"""Read Gyro and Accelerometer by Interfacing Raspberry Pi
with MPU6050 using Python.

See: www.electronicwings.com

Registers, addresses and instructions documentation at:
    https://43zrtwysvxb2gf29r5o0athu-wpengine.netdna-ssl.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
"""
import logging
import smbus
from time import sleep

# MPU6050 registers and their address.
MPU6050_ADDRESS = 0x68  # could also be 0x69
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_XOUT_L = 0x3C
ACCEL_YOUT_H = 0x3D
ACCEL_YOUT_L = 0x3E
ACCEL_ZOUT_H = 0x3F
ACCEL_ZOUT_L = 0x40
TEMP_OUT_H = 0x41
TEMP_OUT_L = 0x42
GYRO_XOUT_H = 0x43
GYRO_XOUT_L = 0x44
GYRO_YOUT_H = 0x45
GYRO_YOUT_L = 0x46
GYRO_ZOUT_H = 0x47
GYRO_ZOUT_L = 0x48

# Constants.
ACCEL_LSB_SENSITIVITY_2g = 16384
GYRO_LSB_SENSITIVITY_250deg = 131
GYRO_LSB_SENSITIVITY_2000deg = 16.4

RATE = 10
LOGGING_LEVEL = logging.INFO

logging.basicConfig(level=LOGGING_LEVEL, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def mpu_init(bus, device_address):
    logger.info('Starting IMU setup')

    # Sample Rate Divider.
    # Specifies the divider from the gyroscope output rate used to generate
    # the Sample Rate.
    #   Sample Rate = Gyroscope Output Rate / (1 + SMPLRT_DIV)
    # where Gyroscope Output Rate = 8kHz when the DLPF is disabled
    # (DLPF_CFG = 0 or 7), and 1kHz when the DLPF is enabled (see Register 26).
    bus.write_byte_data(device_address, SMPLRT_DIV, 7)

    # Power Management 1.
    # This register allows the user to configure the power mode
    # and clock source. It also provides a bit for resetting the entire device
    # and a bit for disabling the temperature sensor.
    # There are 3 clock sources:
    # * internal 8MHz oscillator (CLKSEL = 0)
    # * gyroscope based clock (recommended, CLKSEL = 1-3 for x, y, z
    #   gyro reference)
    # * external source (CLKSEL = 4-5)
    # CLKSEL 6 and 7 are other things.
    # Bits 0-2 configure CLKSEL. Bits 3-7 configure other things.
    # Here we take the x gyroscope as clock reference.
    bus.write_byte_data(device_address, PWR_MGMT_1, 1)

    # Configuration.
    # This register configures the external Frame Synchronization (FSYNC)
    # pin sampling (bits 3-5) and the Digital Low Pass Filter (DLPF) setting
    # (bits 0-2) for both the gyroscopes and accelerometers. Bits 6-7 unused.
    # The accelerometer and gyroscope are filtered according to the value
    # of DLPF_CFG.
    # By choosing DLPF_CFG = 0 we are setting the following:
    # * Accelerometer Bandwidth = 160 Hz (max)
    # * Accelerometer Delay = 0 ms (min)
    # * Gyroscope Bandwidth = 256 Hz (max)
    # * Gyroscope Delay = 0.98 ms (min)
    # * Gyroscope Fs = 8 kHz (max)
    # Bandwidth is the vibration the accelerometer can detect. It is filter by
    # a filter with bandwidth set by DLPF_CFG.
    bus.write_byte_data(device_address, CONFIG, 0)

    # Gyroscope Configuration.
    # This register is used to trigger gyroscope self-test and configure
    # the gyroscopes’ full scale range.
    # 24 = 0 0 0 1 1 0 0 0
    # Bits 3-4 set FS_SEL, which selects the full scale range of the gyroscope
    # outputs. The full scale range is the maximum angular velocity that the
    # gyro can read. FS_SEL = 3 sets +-2000 degree/s.
    bus.write_byte_data(device_address, GYRO_CONFIG, 24)

    # Interrupt Enable.
    # This register enables interrupt generation by interrupt sources.
    # Bit 0, which we set to 1, is DATA_RDY_EN.
    # DATA_RDY_EN enables the Data Ready interrupt, which occurs each time
    # a write operation to all of the sensor registers has been completed.
    # To my understanding, when we write data to all sensor registers, we set
    # bit 1 of register INT_STATUS (3A) to 1. Such bit is set back to 0 after
    # a read operation.
    bus.write_byte_data(device_address, INT_ENABLE, 1)

    logger.info('IMU setup complete')


def _read_double_register_data(bus, device_address, address_high, address_low):
    high = bus.read_byte_data(device_address, address_high)
    low = bus.read_byte_data(device_address, address_low)
    value = (high << 8) | low
    signed_value = value - 2**16 if value > 2**15 else value
    return signed_value


def _read_raw_accelerometer_data(bus, device_address):
    raw_data = (
        _read_double_register_data(bus, device_address, ACCEL_XOUT_H, ACCEL_XOUT_L),
        _read_double_register_data(bus, device_address, ACCEL_YOUT_H, ACCEL_YOUT_L),
        _read_double_register_data(bus, device_address, ACCEL_ZOUT_H, ACCEL_ZOUT_L),
    )
    return raw_data


def read_accelerometer_data(bus, device_address):
    return tuple(map(lambda x: x / ACCEL_LSB_SENSITIVITY_2g,
                     _read_raw_accelerometer_data(bus, device_address)))


def _read_raw_temperature_data(bus, device_address):
    raw_data = _read_double_register_data(bus, device_address, TEMP_OUT_H, TEMP_OUT_L)
    return raw_data


def read_temperature_data(bus, device_address):
    raw_temp = _read_raw_temperature_data(bus, device_address)
    temp_deg = raw_temp / 340 + 36.53
    return temp_deg


def _read_raw_gyroscope_data(bus, device_address):
    raw_data = (
        _read_double_register_data(bus, device_address, GYRO_XOUT_H, GYRO_XOUT_L),
        _read_double_register_data(bus, device_address, GYRO_YOUT_H, GYRO_YOUT_L),
        _read_double_register_data(bus, device_address, GYRO_ZOUT_H, GYRO_ZOUT_L),
    )
    return raw_data


def read_gyroscope_data(bus, device_address):
    return tuple(map(lambda x: x / GYRO_LSB_SENSITIVITY_2000deg,
                     _read_raw_gyroscope_data(bus, device_address)))


def main():
    logger.info('Start up')

    # The argument is 0 for older version boards.
    bus = smbus.SMBus(1)

    device_address = MPU6050_ADDRESS
    mpu_init(bus, device_address)

    logger.info('Begin data reading')
    sleep_time = 1. / RATE
    while True:
        acc_x, acc_y, acc_z = read_accelerometer_data(bus, device_address)
        temp_deg = read_temperature_data(bus, device_address)
        gyro_x, gyro_y, gyro_z = read_gyroscope_data(bus, device_address)

        logger.info('Accelerometer: {}'.format((acc_x, acc_y, acc_z)))
        logger.info('Temperature: {}'.format(temp_deg))
        logger.info('Gyroscope: {}'.format((gyro_x, gyro_y, gyro_z)))
        logger.info('')

        sleep(sleep_time)


if __name__ == '__main__':
    main()
