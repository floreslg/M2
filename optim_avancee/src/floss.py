import numpy as np



class Floss():


    def __init__(self, sim_class, sim_params):
        self.sim_class = sim_class
        self.sim_params = sim_params
        
        self._k1 = 10
        self._k2 = 100
        self._k3 = 1

        self.simulator = None


    def loss_rec(self, x_start):
        xleft, xright, ydown, yup = x_start

        sim = self.sim_class(**self.sim_params)
        sim.init_fields()
        sim.set_firewall_rectang(xleft, xright, ydown, yup)
        sim.simulate()

        comb_init = 1/(sim.Nx*sim.Ny) * np.sum(sim.C0)
        comb_final = 1/(sim.Nx*sim.Ny) * np.sum(sim.C)

        firewall_area = self._k1 * np.abs((xright - xleft) * (yup - ydown))
        firewall_loc = self._k2 * max(0, 0.2 - ydown)
        burnt_area = self._k3 * (comb_init - comb_final)
        
        loss = burnt_area + firewall_area + firewall_loc
        return loss


    def loss_cer(self, x_start):
        xcent, ycent, r = x_start

        sim = self.sim_class(**self.sim_params)
        sim.init_fields()
        sim.set_firewall_cercle(xcent, ycent, r)
        sim.simulate()

        comb_init = 1/(sim.Nx*sim.Ny) * np.sum(sim.C0)
        comb_final = 1/(sim.Nx*sim.Ny) * np.sum(sim.C)

        firewall_area = self._k1 * np.abs(np.pi * r**2)
        firewall_loc = self._k2 * max(0, 0.2 - ycent)
        burnt_area = self._k3 * (comb_init - comb_final)
        
        loss = burnt_area + firewall_area + firewall_loc
        return loss