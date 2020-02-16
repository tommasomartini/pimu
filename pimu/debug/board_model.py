import itertools as it

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import pimu.constants as const
import pimu.geometry as geom


class BoardModel:
    """Class to visualize a sensor board model in 3D.

    The coordinate system integral with the sensor board is the following:
    - X axis: towards the front
    - Y axis: towards the right
    - Z axis: downwards
    """

    # Dimensions of the board along the board's axes.
    _LENGTH = const.BOARD_LENGTH_mm     # along x
    _WIDTH = const.BOARD_WIDTH_mm       # along y
    _HEIGHT = const.BOARD_HEIGHT_mm     # along z

    # How bigger the visualization box is, with respect to the maximum board
    # dimension.
    _BOX_SCALE = 1.5

    # How bigger the board axes are displayed, with respect to each board's
    # half dimension.
    _AXES_SCALE = 2.

    def __init__(self):
        # Dimensions along the board's X, Y and Z axes.
        dimensions = np.array([self._LENGTH, self._WIDTH, self._HEIGHT])
        half_dimensions = dimensions / 2
        signs = [-1, 1]
        vertices_coords = np.c_[half_dimensions] @ np.c_[signs].T

        # Vertices as column vectors.
        self._init_vertices = np.array(list(it.product(*vertices_coords))).T

        # X, Y and Z axes as column vectors.
        self._init_board_axes = np.diag(self._AXES_SCALE * half_dimensions)

        self._vertices = self._init_vertices
        self._board_axes = self._init_board_axes

    def rotate(self, yaw_rad, pitch_rad, roll_rad):
        """Rotates the model from its initial orientation.

        The rotation follows one of the following two (equivalent) conventions:
        * intrinsic rotations: z - y'- x"
        * extrinsic rotations: x - y - z

        Args:
            yaw_rad (float): Rotation around the Z axis in radians.
            pitch_rad (float): Rotation around the Y axis in radians.
            roll_rad (float): Rotation around the X axis in radians.
        """
        rotation_matrix = \
            geom.build_rotation_matrix(yaw_rad, pitch_rad, roll_rad)
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
            'r',  # back
            'w',  # right
            'g',  # left
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

        # Adapt the coordinates for Matplotlib visualization, for the plotting
        # reference system is not the same as the system integral with the
        # sensor board.
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

        lim = self._BOX_SCALE * np.max([self._WIDTH,
                                        self._LENGTH,
                                        self._HEIGHT])
        ax.set_xlim([-lim, lim])
        ax.set_ylim([-lim, lim])
        ax.set_zlim([-lim, lim])

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.set_zlabel('Z axis')

        ax.set_aspect('equal')
        ax.grid(False)


def main():
    board_model = BoardModel()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection=Axes3D.name)

    board_model.rotate(yaw_rad=np.deg2rad(0),
                       pitch_rad=np.deg2rad(30),
                       roll_rad=np.deg2rad(10))
    board_model.plot(ax)

    plt.show()
    plt.close()


if __name__ == '__main__':
    main()
