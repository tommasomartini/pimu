"""This module contains the functions necessary to set up the MPU6050 IMU.
"""
import logging

import pimu.constants as const
import pimu.registers as regs

logger = logging.getLogger(__name__)


def mpu_init(bus, device_address, config):
    logger.info('Starting IMU setup')

    # Extracts the parameters from the config dict.
    fs_sel = const.FS_SEL[config['fs_sel']]
    afs_sel = const.AFS_SEL[config['afs_sel']]

    # Sample Rate Divider.
    # Specifies the divider from the gyroscope output rate used to generate
    # the Sample Rate.
    #   Sample Rate = Gyroscope Output Rate / (1 + SMPLRT_DIV)
    # where Gyroscope Output Rate = 8kHz when the DLPF is disabled
    # (DLPF_CFG = 0 or 7), and 1kHz when the DLPF is enabled (see Register 26).
    bus.write_byte_data(device_address, regs.SMPLRT_DIV, 7)

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
    bus.write_byte_data(device_address, regs.PWR_MGMT_1, 1)

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
    bus.write_byte_data(device_address, regs.CONFIG, 0)

    # Gyroscope Configuration.
    # This register is used to trigger gyroscope self-test and configure
    # the gyroscopes’ full scale range.
    # 24 = 0 0 0 1 1 0 0 0
    # Bits 3-4 set FS_SEL, which selects the full scale range of the gyroscope
    # outputs. The full scale range is the maximum angular velocity that the
    # gyro can read. FS_SEL = 3 sets +-2000 degree/s.
    bus.write_byte_data(device_address, regs.GYRO_CONFIG, fs_sel)

    # Accelerometer Configuration.
    # This register is used to trigger accelerometer self test and configure
    # the accelerometer full scale range. This register also configures
    # the Digital High Pass Filter (DHPF)
    # Bits 3-4 set AFS_SEL, which selects the full scale range of
    # the accelerometer outputs. AFS_SEL = 0 sets +-2g.
    bus.write_byte_data(device_address, regs.ACCEL_CONFIG, afs_sel)

    # Interrupt Enable.
    # This register enables interrupt generation by interrupt sources.
    # Bit 0, which we set to 1, is DATA_RDY_EN.
    # DATA_RDY_EN enables the Data Ready interrupt, which occurs each time
    # a write operation to all of the sensor registers has been completed.
    # To my understanding, when we write data to all sensor registers, we set
    # bit 1 of register INT_STATUS (3A) to 1. Such bit is set back to 0 after
    # a read operation.
    bus.write_byte_data(device_address, regs.INT_ENABLE, 1)

    logger.info('IMU setup complete')
