import argparse
import json
import logging

import pimu.debug.visual as vizdbg
import pimu.imu_server as imu_server
import pimu.network as net

_DEFAULT_RATE_hz = 10
_LOGGING_LEVEL = logging.WARNING
_CALIBRATE = False
_GYRO_FULL_SCALE_RANGE = '250'
_ACC_FULL_SCALE_RANGE = '2g'

mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
logging.basicConfig(level=_LOGGING_LEVEL,
                    format='[%(levelname)s][%(name)s] %(message)s')
_logger = logging.getLogger(__name__)


def _client_to_visual_debugger(client):
    def func():
        for data in client.receive():
            yaw_rad, pitch_rad, roll_rad, temperature_deg = \
                map(float, json.loads(data))
            yield yaw_rad, pitch_rad, roll_rad, \
                  0, 0, 0, \
                  temperature_deg
    return func


def _run_imu_server(ip,
                    port,
                    rate_hz,
                    calibrate,
                    gyro_fsr,
                    acc_fsr):
    _logger.info('Starting IMU server')

    server = imu_server.MPU6050Server(ip=ip,
                                      port=port,
                                      rate_hz=rate_hz,
                                      calibrate=calibrate,
                                      gyro_sensitivity=gyro_fsr,
                                      acc_sensitivity=acc_fsr)
    server.run()


def _run_imu_client(ip, port, rate_hz):
    _logger.info('Starting IMU client')

    client = net.UDPClient(ip, port)
    debugger = vizdbg.VisualDebugger(rate=rate_hz)
    debugger.run(updating_func=_client_to_visual_debugger(client))


def _main():
    parser = argparse.ArgumentParser(description='IMU testing app.')
    parser.add_argument('--server', '-s',
                        action='store_true',
                        dest='is_server',
                        help='Starts an IMU server.'
                             'Raises if --client is also set.')
    parser.add_argument('--client', '-c',
                        action='store_true',
                        dest='is_client',
                        help='Starts an IMU client.'
                             'Raises if --server is also set.')
    parser.add_argument('--ip',
                        required=True,
                        type=str,
                        help='IP address of the client to send to (if server) '
                             'or IP address of the server to listen to (if'
                             'client).')
    parser.add_argument('--port',
                        required=True,
                        type=int,
                        help='Port of the UDP communication.')
    parser.add_argument('--rate',
                        required=True,
                        type=float,
                        help='IMU reading rate, in Hertz.')

    args = parser.parse_args()

    is_server = args.is_server
    is_client = args.is_client
    if is_server == is_client:
        raise ValueError('Either --server or --client must be set.')

    if is_server:
        _run_imu_server(ip=args.ip,
                        port=args.port,
                        rate_hz=args.rate,
                        calibrate=_CALIBRATE,
                        gyro_fsr=_GYRO_FULL_SCALE_RANGE,
                        acc_fsr=_ACC_FULL_SCALE_RANGE)
    else:
        _run_imu_client(ip=args.ip,
                        port=args.port,
                        rate_hz=args.rate)


if __name__ == '__main__':
    _main()
