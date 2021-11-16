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
    'optim-rectang-outside_normal': (f.loss_rec, (0.1, 0.6, 0.4, 0.55)),
    'optim-rectang_inside_normal': (f.loss_rec, (0.2, 0.7, 0.2, 0.35)),
    'optim-rectang-inside-small': (f.loss_rec, (0.2, 0.7, 0.2, 0.25)),
    'optim-rectang-inside-big': (f.loss_rec, (0.2, 0.7, 0.2, 0.5)),
    'optim-cercle-inside-normal': (f.loss_cer, (0.4, 0.2, 0.1)),
}

if __name__ == '__main__':

    iter = 25
    results = list()
    opts = list()
    outdir = './figures/'

    for name, (floss, x_star) in cases.items():

        optimiser = Torczon(floss, x_star, max_iter=iter)
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
    plt.savefig('./figures/optimisation_losses.png', bbox_inches='tight')

    # plot sim
    for x_opt, name in opts:
        sim = Simulator(**sim_params)
        sim.init_fields()

        if name == 'optim-cercle-inside-normal':
            sim.set_firewall_cercle(*x_opt)
        else:
            sim.set_firewall_rectang(*x_opt)

        sim.simulate()

        plt.figure()
        sim.plot_simulation(name, outdir)