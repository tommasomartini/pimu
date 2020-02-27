import json
import time

from pimu.mpu6050.mpu6050 import MPU6050
from pimu.network import UDPServer


class MPU6050Server(UDPServer):

    def __init__(self, ip, port, rate_hz, **kwargs):
        super().__init__(ip, port)
        self._rate_hz = rate_hz
        self._mpu6050 = MPU6050(**kwargs)

    def send_yaw_pitch_roll(self):
        while True:
            yaw_rad, pitch_rad, roll_rad, temperature_deg = \
                self._mpu6050.read_yaw_pitch_roll()
            data = json.dumps([yaw_rad, pitch_rad, roll_rad, temperature_deg])
            self.send(data)
            time.sleep(1 / self._rate_hz)
