import logging

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

import pimu.geometry as geom

_logger = logging.getLogger()
sns.set()


class VisualDebugger:

    # Show the last n seconds.
    _SHOW_TIME_s = 5

    _XLABEL = 'Time (s)'

    _NUM_SUBPLOTS_ROWS = 4
    _NUM_SUBPLOTS_COLS = 2

    def __init__(self, rate):
        self._num_samples = int(round(rate * self._SHOW_TIME_s))

        # Zero-initialize all the plots.
        self._xs = list(range(self._num_samples))
        self._caches = [[0 for _ in range(self._num_samples)]
                        for _ in range(7)]

        # Create the artist elements that will be updated.
        self._artists = [
            None,   # yaw
            None,   # pitch
            None,   # roll
            None,   # filtered yaw
            None,   # filtered pitch
            None,   # filtered roll
            None,   # temperature
            None,   # X axis
            None,   # Y axis
            None,   # Z axis
        ]

        self._init_board_axes = np.diag(np.ones(3))

        _logger.debug('{} initialized'.format(self.__class__.__name__))

    def _format_axes(self, axes):
        ax_yaw, ax_pitch, ax_roll, ax_temp = axes

        # Yaw axis.
        ax_yaw.set_ylabel('Yaw (°)')
        ax_yaw.set_ylim(-200, 200)
        ax_yaw.yaxis.set_major_locator(plt.MultipleLocator(90))
        ax_yaw.yaxis.set_minor_locator(plt.MultipleLocator(45))
        ax_yaw.grid(which='both', axis='y')

        # Pitch axis.
        ax_pitch.set_ylabel('Pitch (°)')
        ax_pitch.set_ylim(-200, 200)
        ax_pitch.yaxis.set_major_locator(plt.MultipleLocator(90))
        ax_pitch.yaxis.set_minor_locator(plt.MultipleLocator(45))
        ax_pitch.grid(which='both', axis='y')

        # Roll axis.
        ax_roll.set_ylabel('Roll (°)')
        ax_roll.set_ylim(-200, 200)
        ax_roll.yaxis.set_major_locator(plt.MultipleLocator(90))
        ax_roll.yaxis.set_minor_locator(plt.MultipleLocator(45))
        ax_roll.grid(which='both', axis='y')

        # Temperature axis.
        ax_temp.set_ylabel('Temp (°C)')
        ax_temp.set_ylim(-50, 120)
        ax_temp.yaxis.set_major_locator(plt.MultipleLocator(25))
        ax_temp.grid(True)

        # Common axis formatting.
        tick_step = int(round(self._num_samples / self._SHOW_TIME_s))
        ticklabel_step = int(round(self._SHOW_TIME_s // self._SHOW_TIME_s))
        xtickslabels = range(-self._SHOW_TIME_s, 1, ticklabel_step)
        for ax in axes:
            ax.set_xticks(range(-1, self._num_samples, tick_step))
            ax.set_xticklabels(xtickslabels)
            ax.yaxis.set_label_position('right')
            ax.yaxis.tick_right()

        # Set the X axis label only on the last plot.
        axes[-1].set_xlabel(self._XLABEL)

    @staticmethod
    def _format_axes3d(ax_3d):
        ax_3d.set_xlim([-2, 2])
        ax_3d.set_ylim([-2, 2])
        ax_3d.set_zlim([-2, 2])

        ax_3d.set_xticks([])
        ax_3d.set_yticks([])
        ax_3d.set_zticks([])

        ax_3d.set_xlabel('X axis')
        ax_3d.set_ylabel('Y axis')
        ax_3d.set_zlabel('Z axis')

        ax_3d.set_aspect('equal')
        ax_3d.grid(False)

    def _update_cache(self, cache, value):
        cache.append(value)
        cache = cache[-self._num_samples:]
        return cache

    def _animate(self, values):
        (yaw_rad, pitch_rad, roll_rad,
         filtered_yaw_rad, filtered_pitch_rad, filtered_roll_rad,
         temperature_deg) = values

        (yaw_deg, pitch_deg, roll_deg,
         filtered_yaw_deg, filtered_pitch_deg, filtered_roll_deg) = \
            map(np.rad2deg,
                (yaw_rad, pitch_rad, roll_rad,
                 filtered_yaw_rad, filtered_pitch_rad, filtered_roll_rad))

        _logger.debug('yaw={:> 6.1f}°, '
                      'pitch={:> 6.1f}°, '
                      'roll={:> 6.1f}°, '
                      'temp={:> 5.1f}°C'.format(yaw_deg, pitch_deg, roll_deg,
                                                temperature_deg))

        self._caches[0] = self._update_cache(self._caches[0], yaw_deg)
        self._caches[1] = self._update_cache(self._caches[1], pitch_deg)
        self._caches[2] = self._update_cache(self._caches[2], roll_deg)
        self._caches[3] = self._update_cache(self._caches[3],
                                             filtered_yaw_deg)
        self._caches[4] = self._update_cache(self._caches[4],
                                             filtered_pitch_deg)
        self._caches[5] = self._update_cache(self._caches[5],
                                             filtered_roll_deg)
        self._caches[6] = self._update_cache(self._caches[6], temperature_deg)

        self._artists[0].set_ydata(self._caches[0])
        self._artists[1].set_ydata(self._caches[1])
        self._artists[2].set_ydata(self._caches[2])
        self._artists[3].set_ydata(self._caches[3])
        self._artists[4].set_ydata(self._caches[4])
        self._artists[5].set_ydata(self._caches[5])
        self._artists[6].set_ydata(self._caches[6])

        rotation_matrix = geom.build_rotation_matrix(yaw_rad=yaw_rad,
                                                     pitch_rad=pitch_rad,
                                                     roll_rad=roll_rad)
        board_axes = rotation_matrix @ self._init_board_axes

        # Matrix of shape (3, 2, 3), representing 3 axis, each defined by two
        # points expressed in 3D coordinates.
        origin = np.zeros(3)
        lines = np.array([[origin, axis] for axis in board_axes.T])

        # Adapt the coordinates for Matplotlib visualization.
        lines[:, :, [0, 1]] = lines[:, :, [1, 0]]
        lines[:, :, -1] *= -1

        self._artists[7].set_data(lines[0, :, 0], lines[0, :, 1])
        self._artists[7].set_3d_properties(lines[0, :, 2])

        self._artists[8].set_data(lines[1, :, 0], lines[1, :, 1])
        self._artists[8].set_3d_properties(lines[1, :, 2])

        self._artists[9].set_data(lines[2, :, 0], lines[2, :, 1])
        self._artists[9].set_3d_properties(lines[2, :, 2])

        return self._artists

    def run(self, updating_func):
        fig, axes = plt.subplots(nrows=self._NUM_SUBPLOTS_ROWS,
                                 ncols=self._NUM_SUBPLOTS_COLS,
                                 sharex='col',
                                 sharey='none')
        ax_3d = \
            plt.subplot(1, self._NUM_SUBPLOTS_COLS, 1, projection=Axes3D.name)

        self._format_axes(axes[:, -1])
        self._format_axes3d(ax_3d)

        for idx in range(3):
            self._artists[idx] = axes[idx, 1].plot(self._xs,
                                                   self._caches[idx],
                                                   color='k',
                                                   label='raw')[0]

        for idx in range(3):
            self._artists[idx + 3] = axes[idx, 1].plot(self._xs,
                                                       self._caches[idx + 3],
                                                       color='r',
                                                       label='filtered')[0]

        self._artists[6] = \
            axes[3, 1].plot(self._xs, self._caches[6], color='k')[0]

        self._artists[7] = ax_3d.plot([0, 1], [0, 0], [0, 0], color='r')[0]
        self._artists[8] = ax_3d.plot([0, 0], [0, 1], [0, 0], color='g')[0]
        self._artists[9] = ax_3d.plot([0, 0], [0, 0], [0, 1], color='b')[0]

        _logger.debug('{} ready to run'.format(self.__class__.__name__))

        _ = animation.FuncAnimation(fig=fig,
                                    func=self._animate,
                                    frames=updating_func,
                                    interval=1,
                                    blit=True)
        plt.show()
