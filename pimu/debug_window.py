import time

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

_RATE_hz = 10


def generate_data():
    for i in range(1000):
        time.sleep(1 / _RATE_hz)
        data = 2 * (np.random.rand(VisualDebugger._NUM_SUBPLOTS_ROWS) - 0.5) * 170
        yield data


class _PlotParams:

    def __init__(self, ylabel, ylim):
        self.ylabel = ylabel
        self.ylim = ylim


_plotsParams = [
    _PlotParams('Yaw (°)', (-180, 180)),
    _PlotParams('Pitch (°)', (-180, 180)),
    _PlotParams('Roll (°)', (-180, 180)),
    _PlotParams('Temp (°C)', (-20, 100)),
]


def _format_axis(ax):
    ax.yaxis.set_label_position('right')
    ax.yaxis.tick_right()


class VisualDebugger:

    # Show the last n seconds.
    _SHOW_TIME_s = 5

    _XLABEL = 'Time (s)'

    _NUM_SUBPLOTS_ROWS = len(_plotsParams)
    _NUM_SUBPLOTS_COLS = 2
    _NUM_XTICKS = 5

    def __init__(self, rate):
        self._num_samples = rate * self._SHOW_TIME_s

        if self._num_samples < self._NUM_XTICKS:
            raise ValueError('Less samples than X ticks')

        if self._SHOW_TIME_s < self._NUM_XTICKS:
            raise ValueError('Less seconds of show-time than X ticks')

        # Zero-initialize all the plots.
        self._xs = list(range(self._num_samples))
        self._caches = [
            [0] * self._num_samples
            for _ in range(self._NUM_SUBPLOTS_ROWS)
        ]

        # Create the plot elements that will be updated.
        self._plots = [None for _ in range(self._NUM_SUBPLOTS_ROWS)]

    def _update_cache(self, cache, value):
        cache.append(value)
        cache = cache[-self._num_samples:]
        return cache

    def _animate(self, values):
        for idx, value in enumerate(values):
            self._caches[idx] = self._update_cache(self._caches[idx], value)
            self._plots[idx].set_ydata(self._caches[idx])

        return self._plots

    def run(self, updating_func):
        fig, axes = plt.subplots(nrows=self._NUM_SUBPLOTS_ROWS,
                                 ncols=self._NUM_SUBPLOTS_COLS,
                                 sharex='col',
                                 sharey='none')
        ax_3d = \
            plt.subplot(1, self._NUM_SUBPLOTS_COLS, 1, projection=Axes3D.name)

        for ax in axes[:, -1]:
            _format_axis(ax)

        for idx in range(self._NUM_SUBPLOTS_ROWS):
            ax = axes[idx, -1]
            _format_axis(ax)
            ax.set_ylim(_plotsParams[idx].ylim)
            ax.set_ylabel(_plotsParams[idx].ylabel)

        for idx in range(self._NUM_SUBPLOTS_ROWS):
            self._plots[idx] = axes[idx, 1].plot(self._xs, self._caches[idx])[0]

        tick_step = self._num_samples // self._NUM_XTICKS
        axes[0, 1].set_xticks(list(range(-1, self._num_samples, tick_step)))

        ticklabel_step = self._SHOW_TIME_s // self._NUM_XTICKS
        xtickslabels = list(range(-self._SHOW_TIME_s, 1, ticklabel_step))
        axes[0, 1].set_xticklabels(xtickslabels)

        axes[-1, -1].set_xlabel(self._XLABEL)

        _ = animation.FuncAnimation(fig=fig,
                                    func=self._animate,
                                    frames=updating_func,
                                    interval=1,
                                    blit=True)
        plt.show()


def main():
    VisualDebugger(rate=_RATE_hz).run(updating_func=generate_data)


if __name__ == '__main__':
    main()
