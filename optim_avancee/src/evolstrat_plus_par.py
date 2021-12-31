from .evolstrat_plus import Evolstrat_plus
from multiprocessing import Pool
import numpy as np


class Evolstrat_plus_par(Evolstrat_plus):


    def __init__(self, loss_func, x_start, max_iter):
        super().__init__(loss_func, x_start, max_iter)
        self._algoname = 'Ev. strategy plus par. '


    def _evaluation(self, childs, loss_func):
        with Pool() as p:
            childs_evals = p.map(loss_func, childs)
        return np.array(childs_evals)


def rosen(x):#min=(1,1)
    return sum(100.0*(x[1:]-x[:-1]**2.0)**2.0 + (1-x[:-1])**2.0)


if __name__ == "__main__":

    x_start = (0.2, 0.8)
    max_iter = 150

    optim = Evolstrat_plus_par(rosen, x_start, max_iter)
    optim.optimize()
    optim.plot_loss('testNM', outdir='../figures')
