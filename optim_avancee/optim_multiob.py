from src.simulator import Simulator
from src.floss import Floss
from src.torczon2 import Torczon

import matplotlib.pyplot as plt



sim_params = {
    # temperature field init:
    'Nx':100,
    'Ny':100,
    'Nt':500,
    'xmin':0,
    'xmax':1,
    'ymin':0,
    'ymax':1,
    # temperature field init
    't0':5.,
    'x0':0.1,
    'y0':0.1,
    'r0':0.01,
    # combustion / firewall:
    'c0':5.,
    'n_spots':10,
    'T_ignt':0.05,
    'fire_c0':-1,
    # stability related:
    'mu':5e-3,
    'k':0.25,
    # random:
    'seed':444
}

f = Floss(Simulator, sim_params)

cases = {
    'optim-multiob_no-pond': (f, (10, 100, 1)),
    'optim-multiob_pond': (f, (1/3, 1/3, 1/3)),
    'optim-multiob_pond-k213': (f, (0.09, 0.9, 1-0.99)),
    'optim-multiob_pond-k231': (f, (1-0.99, 0.9, 0.09)),
    'optim-multiob_pond-k123': (f, (0.9, 0.09, 1-0.99)),
    'optim-multiob_pond-k132': (f, (0.9, 1-0.99, 0.09)),
    'optim-multiob_pond-k321': (f, (1-0.99, 0.09, 0.9)),
    'optim-multiob_pond-k312': (f, (0.09, 1-0.99, 0.9)),
}

if __name__ == '__main__':

    iter = 25
    results = list()
    opts = list()
    outdir = './figures/'
    x_star = (0.1, 0.6, 0.4, 0.55)

    for name, (floss, wights) in cases.items():

        floss.set_wights(*wights)
        optimiser = Torczon(floss.loss_rec, x_star, max_iter=iter)
        optimiser.optimize()
        
        results.append((optimiser.hist_loss, optimiser.exe_time, name))
        opts.append((optimiser.x_opt, name))


    # plot losses
    plt.figure()
    for loss, exe_time, name in results:
        plt.plot(loss, label=f'{name}, exe time {exe_time:.2}')
    plt.title('Optimisations efficacity by case')
    plt.xlabel('Iterations')
    plt.ylabel('Loss')
    plt.yscale('log')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig('./figures/optmulti_losses.png', bbox_inches='tight')

    # plot sim
    for x_opt, name in opts:
        sim = Simulator(**sim_params)
        sim.init_fields()
        sim.set_firewall_rectang(*x_opt)
        sim.simulate()

        plt.figure()
        sim.plot_simulation(name, outdir)