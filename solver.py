from mesh import *
from matplotlib import animation


class solver:

    def __init__(self, gridpts, dtdx, ic, scheme,
                 bc, timeDomain=1, spaceDomain=1):
        self.grid = mesh(gridpts, dtdx, timeDomain, spaceDomain)
        self.grid.Q[:, :, 0] = ic(self.grid.x)
        self.bc = bc
        left_bc, right_bc = bc(0, self.grid.Q[:, :, 0])
        self.grid.Q[:, 0, 0] = left_bc
        self.grid.Q[:, -1, 0] = right_bc
        self.grid.E[:, :, 0] = self.grid.compute_E(0)
        self.scheme = scheme(self.grid.dtdx, bc)

    def solve(self, t_step, art_viscosity):
        q_step = self.grid.Q[:, :, t_step]
        e_step = self.grid.E[:, :, t_step]
        self.grid.Q[:, :, t_step +
                    1] = self.scheme.step(q_step, e_step, t_step, art_viscosity)
        self.grid.E[:, :, t_step +
                    1] = self.grid.compute_E(t_step + 1)

    def animate(self, timesteps, art_viscosity=[0.01, 0.001], repeat=False):
        interval = self.grid.t[1] - self.grid.t[0]
        fig, axarr = plt.subplots(3, sharex=True)
        qt = self.grid.compute_Qt(0)
        lines = []
        lines.append(axarr[0].plot(self.grid.x, qt[0])[0])
        axarr[0].set_ylabel(r'$\rho$')
        lines.append(axarr[1].plot(self.grid.x, qt[1])[0])
        axarr[1].set_ylabel('u')
        lines.append(axarr[2].plot(self.grid.x, qt[2])[0])
        axarr[2].set_ylabel('P')
        plt.xlabel('x')
        anim = animation.FuncAnimation(fig, self.update_line,
                                       frames=timesteps,
                                       interval=interval,
                                       repeat=False,
                                       fargs=(fig, axarr, lines,
                                              art_viscosity))
        plt.show()

    def update_line(self, i, fig, axarr, lines, art_viscosity):
        self.solve(i, art_viscosity)
        qt = self.grid.compute_Qt(i)
        lines[0].set_data(self.grid.x, qt[0])
        axarr[1].set_ylim([0, 1.5 * np.max(qt[1])])
        lines[1].set_data(self.grid.x, qt[1])
        lines[2].set_data(self.grid.x, qt[2])
        return lines