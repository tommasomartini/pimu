import time

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

_LIM_NUM_SAMPLES = 20


def generate_data():
    for i in range(1000):
        time.sleep(0.02)
        yaw, pitch, roll = np.random.randn(3) * np.deg2rad(2)
        yield i, (yaw, pitch, roll)


def main():
    fig = plt.figure()
    ax_yaw = fig.add_subplot(3, 1, 1)
    ax_pitch = fig.add_subplot(3, 1, 2)
    ax_roll = fig.add_subplot(3, 1, 3)

    xs = []
    ys_yaw = []
    ys_pitch = []
    ys_roll = []

    # This function is called periodically from FuncAnimation.
    def animate(values, xs, ys_yaw, ys_pitch, ys_roll):
        idx, (yaw, pitch, roll) = values

        xs.append(idx)
        ys_yaw.append(yaw)
        ys_pitch.append(pitch)
        ys_roll.append(roll)

        xs = xs[-_LIM_NUM_SAMPLES:]
        ys_yaw = ys_yaw[-_LIM_NUM_SAMPLES:]
        ys_pitch = ys_pitch[-_LIM_NUM_SAMPLES:]
        ys_roll = ys_roll[-_LIM_NUM_SAMPLES:]

        ax_yaw.clear()
        yaw_plot = ax_yaw.plot(xs, ys_yaw)

        ax_pitch.clear()
        pitch_plot = ax_pitch.plot(xs, ys_pitch)

        ax_roll.clear()
        roll_plot = ax_roll.plot(xs, ys_roll)

        # Format plot
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.30)
        plt.title('Tait-Bryan angles')
        plt.ylabel('Radians')

        ax_yaw.set_ylim(-np.pi, np.pi)
        ax_pitch.set_ylim(-np.pi, np.pi)
        ax_roll.set_ylim(-np.pi, np.pi)

        return yaw_plot[0], pitch_plot[0], roll_plot[0]

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig=fig,
                                  func=animate,
                                  frames=generate_data,
                                  fargs=(xs, ys_yaw, ys_pitch, ys_roll),
                                  interval=1,
                                  blit=True)
    plt.show()


if __name__ == '__main__':
    main()
