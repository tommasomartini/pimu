import itertools as it

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import pimu.constants as const


def _fake_data_generator():
    num_samples = 100
    for idx in range(num_samples):
        yield idx


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
        self._init_vertices = np.array(list(it.product(*vertices_coords)))

        # X, Y and Z axes as column vectors.
        self._init_board_axes = np.diag(self._axes_scale * half_dimensions)

        self._yaw_rad = 0
        self._yaw_pitch = 0
        self._yaw_roll = 0

    def rotate(self, yaw_rad, pitch_rad, roll_rad):
        """Rotates the board from its current orientation.

        The rotation follows one of the following two (equivalent) conventions:
        * intrinsic rotations: z - y'- x"
        * extrinsic rotations: x - y - z

        Args:
            yaw_rad (float): Rotation around the Z axis in radians.
            pitch_rad (float): Rotation around the X axis in radians.
            roll_rad (float): Rotation around the Y axis in radians.
        """
        pass

    def _plot_parallelepiped(self, ax):
        # "n" stands for "negative" and "p" for positive.
        nnn, nnp, npn, npp, pnn, pnp, ppn, ppp = self._init_vertices

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
        lines = [[origin, axis] for axis in self._init_board_axes.T]
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
        ax.grid('off')


def main():

    board = Board()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection=Axes3D.name)

    board.plot(ax)

    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')

    plt.show()
    plt.close()


if __name__ == '__main__':
    main()
