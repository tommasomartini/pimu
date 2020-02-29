import json
import logging
import time

import numpy as np

from pimu.mpu6050.mpu6050 import MPU6050
from pimu.network import UDPServer

_logger = logging.getLogger(__name__)


class MPU6050Server(UDPServer):

    def __init__(self, ip, port, rate_hz, calibrate, **kwargs):
        super().__init__(ip, port)
        self._rate_hz = rate_hz
        self._mpu6050 = MPU6050(**kwargs)
        if calibrate:
            self._mpu6050.calibrate()

    def run(self):
        while True:
            yaw_rad, pitch_rad, roll_rad, temperature_deg = \
                self._mpu6050.read_yaw_pitch_roll()

            _logger.debug('yaw={:> 6.1f}°, '
                          'pitch={:> 6.1f}°, '
                          'roll={:> 6.1f}°, '
                          'temp={:> 5.1f}°C'.format(np.rad2deg(yaw_rad),
                                                    np.rad2deg(pitch_rad),
                                                    np.rad2deg(roll_rad),
                                                    temperature_deg))

            data = json.dumps([yaw_rad, pitch_rad, roll_rad, temperature_deg])
            self.send(data)
            time.sleep(1 / self._rate_hz)
