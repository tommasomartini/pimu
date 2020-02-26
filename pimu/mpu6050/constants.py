"""MPU6050 constants.

See:
    https://43zrtwysvxb2gf29r5o0athu-wpengine.netdna-ssl.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
"""

# AFS_SEL selects the full scale range of the accelerometer outputs.
# The unit is +-g, with g Gravity.
AFS_SEL = {
    '2g': 0,
    '4g': 1,
    '8g': 2,
    '16g': 3,
}

# 16 bits are used for one measurement that is 2^16 bits.
# If the range is [-2^k * g, 2^k * g] for k={1, 2, 3, 4}, and g Gravity,
# then each bit accounts for: 2^16 / (2 * 2^k) = 2^(16 - 2k).
# Unit: LSB/g
ACCEL_SENSITIVITY = {
    '2g': 16384,    # 2^14
    '4g': 8192,     # 2^13
    '8g': 4096,     # 2^12
    '16g': 2048,    # 2^11
}

# FS_SEL selects the full scale range of the gyroscope outputs.
# The unit is deg/s.
FS_SEL = {
    '250': 0,
    '500': 1,
    '1000': 2,
    '2000': 3,
}

# 16 bits are used for one measurement that is 2^16 bits.
# If the range is [-250 * 2^k, 250 * 2^k] for k={0, 1, 2, 3}, then each bit
# accounts for: 2^16 / (2 * 250 * 2^k) = 2^(15 - k) / 250.
# Unit: LSB/deg/s
GYRO_SENSITIVITY = {
    '250': 131,     # 2^15 / 250 = 131.072
    '500': 65.5,    # 2^14 / 250 = 65.536
    '1000': 32.8,   # 2^13 / 250 = 32.768
    '2000': 16.4,   # 2^12 / 250 = 16.384
}

# Dimensions of the IMU board.
BOARD_WIDTH_mm = 16.4   # along X axis
BOARD_LENGTH_mm = 21.2  # along Y axis
BOARD_HEIGHT_mm = 3.3   # along Z axis
