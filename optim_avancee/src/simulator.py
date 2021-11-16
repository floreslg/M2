import numpy as np
import matplotlib.pyplot as plt


class Simulator():
    
    
    def __init__(self, 
                 # domain discretisation:
                 Nx, Ny, Nt, xmin, xmax, ymin, ymax,
                 # temperature field init:
                 t0, x0, y0, r0,
                 # combustion / firewall:
                 c0, n_spots, T_ignt, fire_c0,
                 # stability related:
                 mu, k,
                 # random:
                 seed
                 ):

        # domain discretisation
        self.Nx = Nx
        self.Ny = Ny
        self.Nt = Nt
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        
        # temperature field init
        self.t0 = t0
        self.x0 = x0
        self.y0 = y0
        self.r0 = r0
        
        # combustion / firewall
        self.c0 = c0
        self.n_spots = n_spots
        self.T_ignt = T_ignt
        self.fire_c0 = fire_c0

        # stability related
        self.mu = mu
        self.k = k
        self.seed = seed
    

    def _init_domain(self, Nx, Ny, xmin, xmax, ymin, ymax):
        
        xx, yy = np.meshgrid(np.linspace(xmin, xmax, Nx+2),
                             np.linspace(ymin, ymax, Ny+2))
        
        dx = xx[0,1] - xx[0,0]
        dy = yy[1,0] - yy[0,0]
        
        return xx, yy, dx, dy
        
    
    def _init_T(self, xx, yy, t0, x0, y0, r0):
        T0 = np.zeros(xx.shape)
        
        for i in range(T0.shape[0]):
            for j in range(T0.shape[1]):
                x = xx[i,j]
                y = yy[i,j]
                r = ((x0-x)**2 + (y0-y)**2)**(1/2)
                if r < r0:
                    T0[i,j] = t0
                    
        return T0
    
    
    def _init_C(self, xx, yy, c0, xmax, ymax, n_spots):
        C0 = np.full(xx.shape, c0)
        
        for spot in range(n_spots):
            mu1 = np.random.rand(1) * xmax
            mu2 = np.random.rand(1) * ymax
            sigma = np.random.normal(1) * xmax * 0.05
            gauss = np.exp((-(xx-mu1)**2 -(yy-mu2)**2) / sigma**2)
            
            C0 += gauss
        
        return C0


    def _init_W(self, xx, yy):
        U = np.cos(np.pi * yy)
        V = 0.6 * np.sin(np.pi / 2*(xx + 0.2))
        return U, V


    def _init_time(self, dx, dy, U, V, k, mu):
        h = min(dx, dy)
        dtc = h / self._norm(U, V)
        dtd = 0.5 * h**2 / mu
        dt = k * min(dtc, dtd)
        return dt

    
    def _laplacian(self, T, i, j, dx, dy):
        dsec_y = 1/(dx**2) * (T[i+1,j] + T[i-1,j] - 2*T[i,j])
        dsec_x = 1/(dy**2) * (T[i,j+1] + T[i,j-1] - 2*T[i,j])
        return dsec_x + dsec_y
    

    def _Wgrad(self, T, i, j, dx, dy, U, V):
        u = U[i,j]
        v = V[i,j]
        
        if v < 0 :
            dprim_y = (1/dx) * (T[i+1,j] - T[i,j])
        else :
            dprim_y = (1/dx) * (T[i,j] - T[i-1,j])
        
        if u < 0 :
            dprim_x = (1/dy) * (T[i,j+1] - T[i,j])
        else :
            dprim_x = (1/dy) * (T[i,j] - T[i,j-1])
        
        return u*dprim_x + v*dprim_y


    def _reaction_T(self, T, i, j, C, T_ignt):
        t = T[i,j]
        c = C[i,j]
        
        if t > T_ignt and c > 0 :
            return 10
        
        if t > T_ignt and c <= 0 :
            return -5
        
        if t <= T_ignt :
            return 0
        
        
    def _reaction_C(self, T, i, j, T_ignt):
        return (-100 if T[i,j] > T_ignt else 0)


    def _norm(self, U, V):
        n_max = 0
        for i in range(U.shape[0]):
            for j in range(U.shape[1]):
                n = (U[i,j]**2 + V[i,j]**2)**(1/2)
                n_max = n if n > n_max else n_max
        
        return n_max


    def init_fields(self):

        np.random.seed(self.seed)

        (
            self.xx,
            self.yy,
            self.dx,
            self.dy
        ) = self._init_domain(self.Nx, self.Ny,
                                self.xmin, self.xmax,
                                self.ymin, self.ymax)
        
        self.T0 = self._init_T(self.xx, self.yy,
                                self.t0, self.x0, self.y0, self.r0)
        
        self.C0 = self._init_C(self.xx, self.yy,
                                self.c0, self.xmax, self.ymax, self.n_spots)

        self.U, self.V = self._init_W(self.xx, self.yy)

        self.dt = self._init_time(self.dx, self.dy,
                                self.U, self.V, self.k, self.mu)


    def set_firewall_rectang(self, xleft, xright, ydown, yup):
        for i in range(self.Nx+2):
            for j in range(self.Ny+2):
                x = self.xx[i, j]
                y = self.yy[i, j]
                if (xleft < x < xright) and (ydown < y < yup):
                    self.C0[i, j] = self.fire_c0


    def set_firewall_cercle(self, xcent, ycent, r):
        for i in range(self.Nx+2):
            for j in range(self.Ny+2):
                x = self.xx[i, j]
                y = self.yy[i, j]
                d = ((xcent-x)**2 + (ycent-y)**2)**(1/2)
                if d < r:
                    self.C0[i, j] = self.fire_c0


    def simulate(self):

        T = self.T0
        C = self.C0

        for iteration in range(self.Nt):

            phi_T = np.zeros(T.shape)
            phi_C = np.zeros(C.shape)

            for i in range(1, self.Nx+1):
                for j in range(1, self.Ny+1):

                    phi_T[i,j] = (
                        - self._Wgrad(T, i, j, self.dx, self.dy, self.U, self.V)
                        + self.mu * self._laplacian(T, i, j, self.dx, self.dy)
                        + self._reaction_T(T, i, j, C, self.T_ignt) * T[i,j]
                    )

                    phi_C[i,j] = (
                        self._reaction_C(T, i, j, self.T_ignt)
                    )

            T = T + self.dt*phi_T
            C = C + self.dt*phi_C
        
        self.C = C
        self.T = T

    
    def plot_simulation(self, name, outdir):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18,6))
        N = 50

        cb1 = ax1.contourf(self.xx, self.yy, self.C0, N, cmap='viridis', vmin=0)
        cb2 = ax1.contourf(self.xx, self.yy, self.T0, N, cmap='plasma', alpha=0.2)
        ax1.streamplot(self.xx, self.yy, self.U, self.V, color='black')

        cb3 = ax2.contourf(self.xx, self.yy, self.C, N, cmap='viridis', vmin=0)
        cb4 = ax2.contourf(self.xx, self.yy, self.T, N, cmap='plasma', alpha=0.2)
        ax2.streamplot(self.xx, self.yy, self.U, self.V, color='black')

        fig.suptitle(name)
        ax1.set_title(f'(iter 0 - comb. {np.sum(self.C0):.3})')
        ax2.set_title(f'(iter {self.Nt} - comb. {np.sum(self.C):.3})')

        fig.colorbar(cb1, ax=ax1, shrink=0.5, label='Comb.')
        fig.colorbar(cb2, ax=ax1, shrink=0.5, label='Temp.')
        fig.colorbar(cb3, ax=ax2, shrink=0.5, label='Comb.')
        fig.colorbar(cb4, ax=ax2, shrink=0.5, label='Temp.')

        plt.savefig(outdir + f'/{name}.png')



if __name__ == "__main__":

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
        seed=1233
    )

    simulator.init_fields()
    simulator.set_firewall_rectang(0.2, 0.6, 0.2, 0.25)
    simulator.set_firewall_cercle(0.2, 0.2, 0.1)
    simulator.simulate()
    simulator.plot_simulation('test', outdir='../figures')