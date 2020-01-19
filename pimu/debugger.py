import itertools as it
import json
import socket
import time

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

    def rotate(self, yaw_rad, pitch_rad, roll_rad):
        """Rotates the board from its current orientation.

        The rotation follows one of the following two (equivalent) conventions:
        * intrinsic rotations: z - y'- x"
        * extrinsic rotations: x - y - z

        Args:
            yaw_rad (float): Rotation around the Z axis in radians.
            pitch_rad (float): Rotation around the Y axis in radians.
            roll_rad (float): Rotation around the X axis in radians.
        """
        # Build the rotation matrix.
        rotation_matrix = geom.build_rotation_matrix(yaw_rad=yaw_rad,
                                                     pitch_rad=pitch_rad,
                                                     roll_rad=roll_rad)

        # Matplotlib's reference system for drawing a plot has the Z axis
        # pointing upwards. The following concatenation only serves for
        # data visualization.
        plot_adapting_rotation_matrix = np.array([
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, -1],
        ]).T
        rotation_matrix = plot_adapting_rotation_matrix @ rotation_matrix

        self._vertices = rotation_matrix @ self._init_vertices
        self._board_axes = rotation_matrix @ self._init_board_axes

    def _plot_parallelepiped(self, ax):
        # "n" stands for "negative" and "p" for positive.
        nnp, nnn, pnp, pnn, npp, npn, ppp, ppn = self._vertices.T

        top_face = [nnp, npp, ppp, pnp]
        bottom_face = [nnn, npn, ppn, pnn]
        front_face = [npn, npp, ppp, ppn]
        back_face = [nnn, nnp, pnp, pnn]
        left_face = [nnn, nnp, npp, npn]
        right_face = [pnn, pnp, ppp, ppn]

        facecolors = [
            'w',    # top
            'b',    # bottom
            'w',    # front
            'g',    # back
            'r',    # left
            'w',    # right
        ]
        poly_collections = Poly3DCollection([top_face,
                                             bottom_face,
                                             front_face,
                                             back_face,
                                             left_face,
                                             right_face],
                                            facecolors=facecolors,
                                            alpha=0.5)
        ax.add_collection3d(poly_collections)

    def _plot_axes(self, ax):
        colors = ['r', 'g', 'b']
        origin = np.zeros(3)
        lines = [[origin, axis] for axis in self._board_axes.T]
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

    UDP_IP = "192.168.1.128"
    UDP_PORT = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection=Axes3D.name)

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        data_dict = json.loads(data.decode('utf-8'))
        acc_x, acc_y, acc_z = map(float, [data_dict['acc_x'],
                                          data_dict['acc_y'],
                                          data_dict['acc_z']])

        acc_x, acc_y, acc_z = \
            sb.accelerometer_data_to_conventional_system(acc_x, acc_y, acc_z)
        yaw, pitch, roll = sb.accelerometer_data_to_taitbryan(acc_x=acc_x,
                                                              acc_y=acc_y,
                                                              acc_z=acc_z)

        ax.clear()
        board.rotate(yaw_rad=yaw, pitch_rad=pitch, roll_rad=roll)
        board.plot(ax)
        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.set_zlabel('Z axis')
        plt.pause(1e-5)

    plt.close()


if __name__ == '__main__':
    main()
