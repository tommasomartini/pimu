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


def _fake_data_generator():
    rate = 60
    num_samples = 500
    max_deg = 1
    np.random.seed(0)
    for idx in range(num_samples):
        time.sleep(1. / rate)
        yaw_rad, roll_rad, pitch_rad = np.deg2rad(max_deg * np.random.rand(3))
        yield yaw_rad, roll_rad, pitch_rad


class Board:

    # Dimensions of the board.
    _width = const.BOARD_WIDTH_mm       # along x
    _length = const.BOARD_LENGTH_mm     # along y
    _height = const.BOARD_HEIGHT_mm     # along z

    # How bigger the visualization box is, with respect to the maximum board
    # dimension.
    _box_scale = 1.5

    # How bigger the board axes are displayed, with respect to each board's
    # half dimension.
    _axes_scale = 2.

    def __init__(self):
        dimensions = np.array([self._width, self._length, self._height])
        half_dimensions = dimensions / 2
        signs = [-1, 1]
        vertices_coords = np.c_[half_dimensions] @ np.c_[signs].T

        # Vertices as column vectors.
        self._init_vertices = np.array(list(it.product(*vertices_coords))).T

        # X, Y and Z axes as column vectors.
        self._init_board_axes = np.diag(self._axes_scale * half_dimensions)

        self._yaw_rad = 0
        self._roll_rad = 0
        self._pitch_rad = 0

        self._vertices = self._init_vertices
        self._board_axes = self._init_board_axes

    def rotate(self, yaw_rad, roll_rad, pitch_rad):
        """Rotates the board from its current orientation.

        The rotation follows one of the following two (equivalent) conventions:
        * intrinsic rotations: z - y'- x"
        * extrinsic rotations: x - y - z

        Args:
            yaw_rad (float): Rotation around the Z axis in radians.
            roll_rad (float): Rotation around the Y axis in radians.
            pitch_rad (float): Rotation around the X axis in radians.
        """

        # Update the current orientation.
        self._yaw_rad += yaw_rad
        self._roll_rad += roll_rad
        self._pitch_rad += pitch_rad

        # Build the rotation matrix.
        rotation_matrix = geom.build_rotation_matrix(yaw_rad=self._yaw_rad,
                                                     roll_rad=self._roll_rad,
                                                     pitch_rad=self._pitch_rad)

        self._vertices = rotation_matrix @ self._init_vertices
        self._board_axes = rotation_matrix @ self._init_board_axes

    def _plot_parallelepiped(self, ax):
        # "n" stands for "negative" and "p" for positive.
        nnn, nnp, npn, npp, pnn, pnp, ppn, ppp = self._vertices.T

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

    fig = plt.figure()
    ax = fig.add_subplot(111, projection=Axes3D.name)
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')

    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes

        data_dict = json.loads(data.decode('utf-8'))
        yaw, roll, pitch = map(float, [data_dict['yaw'],
                                       data_dict['roll'],
                                       data_dict['pitch']])

        ax.clear()
        board.rotate(yaw_rad=yaw, roll_rad=roll, pitch_rad=pitch)
        board.plot(ax)
        plt.pause(1e-5)

    plt.close()


if __name__ == '__main__':
    main()
