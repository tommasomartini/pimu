"""Read Gyro and Accelerometer by Interfacing Raspberry Pi
with MPU6050 using Python.

See: www.electronicwings.com

Registers, addresses and instructions documentation at:
    https://43zrtwysvxb2gf29r5o0athu-wpengine.netdna-ssl.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
"""
import smbus
from time import sleep

# MPU6050 registers and their address.
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47


def MPU_Init():
    # Sample Rate Divider.
    # Specifies the divider from the gyroscope output rate used to generate
    # the Sample Rate.
    #   Sample Rate = Gyroscope Output Rate / (1 + SMPLRT_DIV)
    # where Gyroscope Output Rate = 8kHz when the DLPF is disabled
    # (DLPF_CFG = 0 or 7), and 1kHz when the DLPF is enabled (see Register 26).
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

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
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

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
    bus.write_byte_data(Device_Address, CONFIG, 0)

    # Gyroscope Configuration.
    # This register is used to trigger gyroscope self-test and configure
    # the gyroscopes’ full scale range.
    # 24 = 0 0 0 1 1 0 0 0
    # Bits 3-4 set FS_SEL, which selects the full scale range of the gyroscope
    # outputs. The full scale range is the maximum angular velocity that the
    # gyro can read. FS_SEL = 3 sets +-2000 degree/s.
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

    # Interrupt Enable.
    # This register enables interrupt generation by interrupt sources.
    # Bit 0, which we set to 1, is DATA_RDY_EN.
    # DATA_RDY_EN enables the Data Ready interrupt, which occurs each time
    # a write operation to all of the sensor registers has been completed.
    # To my understanding, when we write data to all sensor registers, we set
    # bit 1 of register INT_STATUS (3A) to 1. Such bit is set back to 0 after
    # a read operation.
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)


def read_raw_data(addr):
    # Accelero and Gyro value are 16-bit
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)

    # concatenate higher and lower value
    value = ((high << 8) | low)

    # to get signed value from mpu6050
    if (value > 32768):
        value = value - 65536
    return value


bus = smbus.SMBus(1)  # or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68  # MPU6050 device address

MPU_Init()

print(" Reading Data of Gyroscope and Accelerometer")

while True:
    # Read Accelerometer raw value
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)

    # Read Gyroscope raw value
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)
    gyro_z = read_raw_data(GYRO_ZOUT_H)

    # Full scale range +/- 250 degree/C as per sensitivity scale factor
    Ax = acc_x / 16384.0
    Ay = acc_y / 16384.0
    Az = acc_z / 16384.0

    Gx = gyro_x / 131.0
    Gy = gyro_y / 131.0
    Gz = gyro_z / 131.0

    print("Gx=%.2f" % Gx, u'\u00b0' + "/s", "\tGy=%.2f" % Gy, u'\u00b0' + "/s",
          "\tGz=%.2f" % Gz, u'\u00b0' + "/s", "\tAx=%.2f g" % Ax,
          "\tAy=%.2f g" % Ay, "\tAz=%.2f g" % Az)
    sleep(1)