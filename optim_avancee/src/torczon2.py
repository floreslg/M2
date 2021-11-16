import numpy as np
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
import time
from multiprocessing import Pool



class Torczon():

    def __init__(self, loss_func, x_start, max_iter):

        self.loss_func = loss_func
        self.max_iter = max_iter
        if isinstance(x_start, np.ndarray): self.x_start = x_start
        else: self.x_start = np.array(x_start)

        self._alpha = 2.
        self._beta = 0.5
        self._step = 0.02

        self.hist_loss = list()
        self.x_best = None
        self.x_opt = None
        self.exe_time = None


    def _init_simplex(self, x_start, loss_func, step):

        dim = len(x_start)
        points = [x_start]
        for i in range(dim):
            x = np.copy(x_start)
            x[i] = x[i] + step
            points.append(x)

        with Pool() as p:
            losses = p.map(loss_func, points)
    
        return list(zip(points, losses))


    def _reflect(self, x):
        x_ref = (1+self._alpha)*self.x_best - self._alpha*x
        return (x_ref, self.loss_func(x_ref))
    

    def _contract(self, x):
        x_cont = self._beta*x + (1-self._beta)*self.x_best
        return (x_cont, self.loss_func(x_cont))


    def optimize(self):

        t = time.perf_counter()

        evals = self._init_simplex(self.x_start, self.loss_func, self._step)

        for iter in tqdm(range(self.max_iter)):

            # determine best point
            evals.sort(key=lambda x: x[1])
            self.x_best, loss_best = evals[0]

            self.hist_loss.append(loss_best)

            # reflextion
            with Pool() as p:
                ref_evals = p.map(self._reflect, [x for x,_ in evals[1:]])

            new_evals = [(self.x_best, loss_best)]
            if True in [loss_ref < loss_best for _, loss_ref in ref_evals]:
                new_evals += ref_evals
            
            else:
                # contraction
                with Pool() as p:
                    new_evals += p.map(self._contract, [x for x,_ in evals[1:]])

            evals = new_evals
        
        self.exe_time =  time.perf_counter() - t
        self.x_opt = self.x_best



    def plot_loss(self, name, outdir):

        title = f'Torczon - optim (exe. time {self.exe_time:.3}): '
        for xi in self.x_opt:
            title += f'{xi:.3}, '

        plt.plot(self.hist_loss)
        plt.yscale('log')
        plt.title(title)
        plt.xlabel('Iterations')
        plt.ylabel('Loss')
        plt.savefig(outdir + f'/{name}.png')


def rosen(x):
    time.sleep(2)
    return sum(100.0*(x[1:]-x[:-1]**2.0)**2.0 + (1-x[:-1])**2.0)
        

if __name__ == "__main__":

    x_start = (0.2, 0.8)#np.array([0.2, 0.8])
    max_iter = 6

    optim = Torczon(rosen, x_start, max_iter)
    optim.optimize()
    optim.plot_loss('testTo2', outdir='../figures')