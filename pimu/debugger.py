import itertools as it
import json
import socket

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import pimu.constants as const
import pimu.geometry as geom
import pimu.sensorboard as sb


class Board:
    """Represents a board to visualize that is always aligned with the sensor.
    """

    # Dimensions of the board along the board's axes.
    _length = const.BOARD_LENGTH_mm     # along x
    _width = const.BOARD_WIDTH_mm       # along y
    _height = const.BOARD_HEIGHT_mm     # along z

    # How bigger the visualization box is, with respect to the maximum board
    # dimension.
    _box_scale = 1.5

    # How bigger the board axes are displayed, with respect to each board's
    # half dimension.
    _axes_scale = 2.

    def __init__(self):
        # Dimensions along the board's X, Y and Z axes.
        dimensions = np.array([self._length, self._width, self._height])
        half_dimensions = dimensions / 2
        signs = [-1, 1]
        vertices_coords = np.c_[half_dimensions] @ np.c_[signs].T

        # Vertices as column vectors.
        self._init_vertices = np.array(list(it.product(*vertices_coords))).T

        # X, Y and Z axes as column vectors.
        self._init_board_axes = np.diag(self._axes_scale * half_dimensions)

        self._vertices = self._init_vertices
        self._board_axes = self._init_board_axes

        self._yaw = 0
        self._pitch = 0
        self._roll = 0

    def rotate(self, acc_yaw, acc_pitch, acc_roll, gyro_yaw_delta, gyro_pitch_delta, gyro_roll_delta):
        """Rotates the board from its current orientation.

        The rotation follows one of the following two (equivalent) conventions:
        * intrinsic rotations: z - y'- x"
        * extrinsic rotations: x - y - z

        Args:
            yaw_rad (float): Rotation around the Z axis in radians.
            pitch_rad (float): Rotation around the Y axis in radians.
            roll_rad (float): Rotation around the X axis in radians.
        """

        # self._yaw += yaw_rad
        # self._pitch += pitch_rad
        # self._roll += roll_rad

        gyro_yaw = self._yaw + gyro_yaw_delta
        gyro_pitch = self._pitch + gyro_pitch_delta
        gyro_roll = self._roll + gyro_roll_delta

        acc_weight = 0.

        self._yaw = gyro_yaw
        self._pitch = acc_weight * acc_pitch + (1 - acc_weight) * gyro_pitch
        self._roll = acc_weight * acc_roll + (1 - acc_weight) * gyro_roll

        # Build the rotation matrix.
        rotation_matrix = geom.build_rotation_matrix(yaw_rad=self._yaw,
                                                     pitch_rad=self._pitch,
                                                     roll_rad=self._roll)

        self._vertices = rotation_matrix @ self._init_vertices
        self._board_axes = rotation_matrix @ self._init_board_axes

    def _plot_parallelepiped(self, ax):
        # "n" stands for "negative" and "p" for positive.
        nnn, nnp, npn, npp, pnn, pnp, ppn, ppp = self._vertices.T

        front_face = [pnn, pnp, ppp, ppn]   # positive X
        back_face = [nnn, nnp, npp, npn]    # negative X
        right_face = [npn, npp, ppp, ppn]   # positive Y
        left_face = [nnn, nnp, pnp, pnn]    # negative Y
        bottom_face = [nnp, npp, ppp, pnp]  # positive Z
        top_face = [nnn, npn, ppn, pnn]     # negative Z

        facecolors = [
            'w',  # front
            'g',  # back
            'w',  # right
            'r',  # left
            'b',  # bottom
            'w',  # top
        ]

        # Matrix with shape (6, 4, 3) representing 6 sides of the board,
        # each defined by 4 corners given in 3D cartesian coordinates.
        all_sides = np.array([front_face,
                              back_face,
                              right_face,
                              left_face,
                              bottom_face,
                              top_face])

        # Adapt the coordinates for Matplotlib visualization.
        all_sides[:, :, [0, 1]] = all_sides[:, :, [1, 0]]
        all_sides[:, :, -1] *= -1

        poly_collections = Poly3DCollection(all_sides,
                                            facecolors=facecolors,
                                            alpha=0.5)
        ax.add_collection3d(poly_collections)

    def _plot_axes(self, ax):
        colors = ['r', 'g', 'b']
        origin = np.zeros(3)

        # Matrix of shape (3, 2, 3), representing 3 axis, each defined by two
        # points expressed in 3D coordinates.
        lines = np.array([[origin, axis] for axis in self._board_axes.T])

        # Adapt the coordinates for Matplotlib visualization.
        lines[:, :, [0, 1]] = lines[:, :, [1, 0]]
        lines[:, :, -1] *= -1

        line_collection = Line3DCollection(lines, colors=colors, linewidths=2)
        ax.add_collection(line_collection)

    def plot(self, ax):
        self._plot_parallelepiped(ax)
        self._plot_axes(ax)

        lim = self._box_scale * np.max([self._width,
                                        self._length,
                                        self._height])
        ax.set_xlim([-lim, lim])
        ax.set_ylim([-lim, lim])
        ax.set_zlim([-lim, lim])

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

        ax.set_aspect('equal')
        ax.grid(False)


def main():
    board = Board()

    UDP_IP = "192.168.1.33"
    UDP_PORT = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection=Axes3D.name)

    prev_time_ms = None

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        data_dict = json.loads(data.decode('utf-8'))
        acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, timestamp_ms = \
            map(float, [data_dict['acc_x'],
                        data_dict['acc_y'],
                        data_dict['acc_z'],
                        data_dict['gyro_x'],
                        data_dict['gyro_y'],
                        data_dict['gyro_z'],
                        data_dict['timestamp_ms']])

        if prev_time_ms is None:
            prev_time_ms = timestamp_ms
            continue

        acc_x, acc_y, acc_z = \
            sb.accelerometer_data_to_conventional_system(acc_x, acc_y, acc_z)

        gyro_x, gyro_y, gyro_z = \
            sb.gyroscope_data_to_conventional_system(gyro_x, gyro_y, gyro_z)

        acc_yaw, acc_pitch, acc_roll = sb.accelerometer_data_to_taitbryan(acc_x=acc_x,
                                                              acc_y=acc_y,
                                                              acc_z=acc_z)

        delta_time_ms = timestamp_ms - prev_time_ms
        gyro_yaw_delta, gyro_pitch_delta, gyro_roll_delta = \
            sb.gyroscope_data_to_taitbryan(gyro_x=gyro_x,
                                           gyro_y=gyro_y,
                                           gyro_z=gyro_z,
                                           delta_time_ms=delta_time_ms)
        prev_time_ms = timestamp_ms

        ax.clear()
        board.rotate(acc_yaw, acc_pitch, acc_roll, gyro_yaw_delta, gyro_pitch_delta, gyro_roll_delta)
        board.plot(ax)
        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.set_zlabel('Z axis')
        plt.pause(1e-5)

    plt.close()


if __name__ == '__main__':
    main()
