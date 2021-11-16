import numpy as np
import matplotlib.pyplot as plt
import time
from tqdm.auto import tqdm


class Nelder_mead():


    def __init__(self, loss_func, x_start, max_iter):
        self.loss_func = loss_func
        self.max_iter = max_iter
        if isinstance(x_start, np.ndarray): self.x_start = x_start
        else: self.x_start = np.array(x_start)

        self._step = 0.02
        self._alpha = 1.
        self._beta = 2.
        self._gamma = 0.5
        self._sigma = 0.5

        self.hist_loss = list()
        self.x_opt = None
        self.exe_time = None


    def _init_simplex(self, x_start, loss_func, step):

        dim = len(x_start)
        evals = list()
        evals.append((x_start, loss_func(x_start)))

        for i in range(dim):
            x = np.copy(x_start)
            x[i] = x[i] + step
            evals.append((x, loss_func(x)))
    
        return evals

    
    def _reflect(self, loss_func, x_cent, x_worst):
        x_ref = x_cent + self._alpha*(x_cent - x_worst)
        loss_ref = loss_func(x_ref)
        
        return (x_ref, loss_ref)


    def _expand(self, loss_func, x_cent, x_worst):
        x_exp = x_cent + self._beta*(x_cent - x_worst)
        loss_exp = loss_func(x_exp)
        
        return (x_exp, loss_exp)
    

    def _contract(self, loss_func, x_cent, x_worst):
        x_cont = x_cent + self._gamma*(x_cent - x_worst)
        loss_cont = loss_func(x_cont)
        
        return (x_cont, loss_cont)

    
    def _reduce(self, loss_func, x_best, evals):
        new_evals = list()
        for x, loss in evals:
            x_red = x_best + self._sigma*(x - x_best)
            new_evals.append((x_red, loss_func(x_red)))
        
        return new_evals

    
    def optimize(self):

        t = time.perf_counter()

        evals = self._init_simplex(self.x_start, self.loss_func, self._step)
        x_best = None
        loss_best = None

        for iter in tqdm(range(self.max_iter)):

            # determine best, worst and centroid point
            evals.sort(key=lambda x: x[1])
            x_best, loss_best = evals[0]
            x_worst, loss_worst = evals[-1]
            x_cent = sum([x for x, _ in evals[:-1]]) / len(evals[:-1])

            self.hist_loss.append(loss_best)

            # reflexion
            x_ref, loss_ref = self._reflect(self.loss_func, x_cent, x_worst)

            if loss_ref < loss_best:
                
                # expansion
                x_exp, loss_exp = self._expand(self.loss_func, x_cent, x_worst)
                if loss_exp < loss_ref:
                    evals[-1] = (x_exp, loss_exp)
                else:
                    evals[-1] = (x_ref, loss_ref)
            
            else:

                if loss_ref < loss_worst:
                    evals[-1] = (x_ref, loss_ref)
                
                else:
                    # contraction
                    x_cont, loss_cont = self._contract(self.loss_func,
                                                        x_cent, x_worst)
                    if loss_cont < loss_worst:
                        evals[-1] = (x_cont, loss_cont)
                    else:
                        # reduction
                        evals = self._reduce(self.loss_func, x_best, evals)

        self.exe_time =  time.perf_counter() - t
        self.x_opt = x_best


    def plot_loss(self, name, outdir):

        title = f'Neldermead - optim (exe. time {self.exe_time:.3}): '
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

    optim = Nelder_mead(rosen, x_start, max_iter)
    optim.optimize()
    optim.plot_loss('testNM', outdir='../figures')




                