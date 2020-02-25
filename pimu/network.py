import logging
import socket


_logger = logging.getLogger()


class _UDPSocket:

    _BUFFER_SIZE = 1024
    _ENCODING = 'utf-8'

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def close(self):
        self._socket.close()
        _logger.info('UDP socket closed')


class UDPServer(_UDPSocket):

    def send(self, data):
        encoded_bytes = bytes(data, self._ENCODING)
        num_sent_bytes = \
            self._socket.sendto(encoded_bytes, (self._ip, self._port))
        _logger.debug('Sent {} bytes '
                      'to {}:{}'.format(num_sent_bytes, self._ip, self._port))


class UDPClient(_UDPSocket):

    def __init__(self, ip, port):
        super().__init__(ip, port)
        self._socket.bind((ip, port))
        _logger.info('UDP Client bound to {}:{}'.format(self._ip, self._port))

    def receive(self):
        while True:
            encoded_data, from_address = \
                self._socket.recvfrom(self._BUFFER_SIZE)
            _logger.debug('Received {} bytes '
                          'from {}'.format(len(encoded_data), from_address))
            data = encoded_data.decode(self._ENCODING)
            yield data
