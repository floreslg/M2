from src.simulator import Simulator
from src.floss import Floss
from src.torczon2 import Torczon
from src.evolstrat_plus_par import Evolstrat_plus_par

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
    'opcomp_ES-inside': (Evolstrat_plus_par, f.loss_rec, (0.1, 0.6, 0.4, 0.55)),
    'opcomp_ES-outside': (Evolstrat_plus_par, f.loss_rec, (0.1, 0.2, 0.4, 0.55)),
    'opcomp_Torc-inside': (Torczon, f.loss_rec, (0.1, 0.6, 0.4, 0.55)),
    'opcomp_Torc-outside': (Torczon, f.loss_rec, (0.1, 0.2, 0.4, 0.55)),
}

if __name__ == '__main__':

    iter = 25
    results = list()
    opts = list()
    outdir = './figures/'

    for name, (Algo, floss, x_star) in cases.items():

        optimiser = Algo(floss, x_star, max_iter=iter)
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
    plt.savefig('./figures/opcomp_losses.png', bbox_inches='tight')

    # plot sim
    for x_opt, name in opts:
        sim = Simulator(**sim_params)
        sim.init_fields()

        sim.set_firewall_rectang(*x_opt)

        sim.simulate()

        plt.figure()
        sim.plot_simulation(name, outdir)