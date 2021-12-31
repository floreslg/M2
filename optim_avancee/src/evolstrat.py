import numpy as np
import time
import matplotlib.pyplot as plt
from tqdm.auto import tqdm



class Evolstrat():


    def __init__(self, loss_func, x_start, max_iter):
        self.loss_func = loss_func
        self.max_iter = max_iter
        if isinstance(x_start, np.ndarray):
            self.x_start = x_start
        else:
            self.x_start = np.array(x_start)

        self._lamb = 50#10
        self._mu = 5#5
        self._tau = 1
        self._algoname = None
        self._seed = 2022

        self.hist_loss = list()
        self.x_opt = None
        self.exe_time = None


    def _initialisation(self, x_start):
        init_pop_mean = x_start
        init_pop_std = np.std(x_start)
        survivors = x_start
        survivors_evals = self.loss_func(x_start)
        return (survivors, survivors_evals, init_pop_mean, init_pop_std)


    def _mutation(self, lamb, pop_mean, pop_std):
        dim_x = len(pop_mean)
        childs = np.zeros((lamb, dim_x))
        for i in range(lamb):
            std = pop_std * np.exp(self._tau*np.random.randn(1))
            childs[i] = pop_mean + std*np.random.randn(dim_x)
        return childs


    def _evaluation(self, childs, loss_func):
        childs_evals = np.array([loss_func(x) for x in childs])
        return childs_evals


    def _selection(self, mu, population, evals):
        idx = np.argsort(evals, )[:mu]
        survivors = population[idx, :]
        return survivors, evals[idx]


    def _recombination(self, survivors):
        pop_mean = np.mean(survivors, axis=0)
        pop_std = np.std(survivors)
        return (pop_mean, pop_std)
    

    def _build_population(self):
        pass


    def optimize(self):
        
        np.random.seed(self._seed)
        t = time.perf_counter()

        (survs,
         survs_evals,
         pop_mean,
         pop_std) = self._initialisation(self.x_start)
        
        for iter in tqdm(range(self.max_iter)):
            
            childs = self._mutation(self._lamb, pop_mean, pop_std)
            childs_evals = self._evaluation(childs, self.loss_func)
            
            pop, evals = self._build_population(survs, survs_evals,
                                                childs, childs_evals)
            
            survs, survs_evals = self._selection(self._mu, pop, evals)
            pop_mean, pop_std = self._recombination(survs)

            x_best = survs[0, :]
            self.hist_loss.append(evals[0])

        self.exe_time = time.perf_counter() - t
        self.x_opt = x_best


    def plot_loss(self, name, outdir):

        title = f'{self._algoname}- optim (exe. time {self.exe_time:.3}): '
        for xi in self.x_opt:
            title += f'{xi:.3}, '

        plt.plot(self.hist_loss)
        plt.yscale('log')
        plt.title(title)
        plt.xlabel('Iterations')
        plt.ylabel('Loss')
        plt.savefig(outdir + f'/{name}.png')
