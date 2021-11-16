from src.simulator import Simulator


simulator = Simulator(
    # temperature field init:
    Nx=100,
    Ny=100,
    Nt=500,
    xmin=0,
    xmax=1,
    ymin=0,
    ymax=1,
    # temperature field init
    t0=5.,
    x0=0.1,
    y0=0.1,
    r0=0.01,
    # combustion / firewall:
    c0=5.,
    n_spots=10,
    T_ignt=0.05,
    fire_c0=-1,
    # stability related:
    mu=5e-3,
    k=0.25,
    # random:
    seed=444
)

cases = {
    'sim-rectang-outside_normal': (simulator.set_firewall_rectang,
                                        [0.1, 0.6, 0.4, 0.55]),
    'sim-rectang_inside_normal': (simulator.set_firewall_rectang,
                                        [0.2, 0.7, 0.2, 0.35]),
    'sim-rectang-inside-small': (simulator.set_firewall_rectang,
                                        [0.2, 0.7, 0.2, 0.25]),
    'sim-rectang-inside-big': (simulator.set_firewall_rectang,
                                        [0.2, 0.7, 0.2, 0.5]),
    'sim-cercle-inside-normal': (simulator.set_firewall_cercle,
                                        [0.4, 0.2, 0.1]),
}


for name, (set_firewall_fonct, args) in cases.items():

    simulator.init_fields()
    set_firewall_fonct(*args)
    simulator.simulate()
    simulator.plot_simulation(name, outdir='./figures')