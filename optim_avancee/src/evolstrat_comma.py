from .evolstrat import Evolstrat



class Evolstrat_comma(Evolstrat):


    def __init__(self, loss_func, x_start, max_iter):
        super().__init__(loss_func, x_start, max_iter)
        self._algoname = 'Ev. strategy comma '


    def _build_population(self, survs, survs_evals, childs, childs_evals):
        return (childs, childs_evals)


def rosen(x):#min=(1,1)
    return sum(100.0*(x[1:]-x[:-1]**2.0)**2.0 + (1-x[:-1])**2.0)
    
    
if __name__ == "__main__":

    x_start = (0.2, 0.8)
    max_iter = 500

    optim = Evolstrat_comma(rosen, x_start, max_iter)
    optim.optimize()
    optim.plot_loss('testNM', outdir='../figures')
