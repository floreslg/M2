"""
This script was used for plots.

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

colors=["k",'b','r', 'g', 'y', 'm', "c", 'b']*10



def get_S(T1, Tn, N):
    
    BG = (((T1/Tn)-N)/(1-N))[1:]
    BA = (((Tn/T1)*N - 1)/(N-1))[1:]
    N = N[1:]
    
    SpG = N*(1-BG) + BG
    SpA = 1/(BA+(1-BA)/N)

    BGm = np.mean(BG[1:])
    BAm = np.mean(BA[1:])
    
    
    return (BGm, BAm, SpG, SpA)



def predict(BGm, BAm, tot_threads):
    
    N = np.arange(1, tot_threads)
    
    SpG = N*(1-BGm) + BGm
    SpA = 1/(BAm+(1-BAm)/N)
    
    return (N, SpG, SpA)



def plot_errors(data, versions):

    N_vals = data.N_val.unique()
    
    for version in versions:
        errors_mean = []
        errors_std = []
        
        for N_val in N_vals:
             
            df = data[data.N_val==N_val]
            df = df[df.Version==version]
            
            errors_mean.append(np.mean(df.ecart))
            errors_std.append(np.std(df.ecart))
        
        plt.plot(N_vals, errors_mean, label=f'v.{version}',
                 ls='--', c=colors[version])
        plt.errorbar(x=N_vals, y=errors_mean, yerr=errors_std,
                     fmt='o', c=colors[version],
                     elinewidth=2, capthick=3, errorevery=1,
                     alpha=0.3, ms=4, capsize = 5)
    
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("Val_N")
    plt.ylabel("Error")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()


    
def plot_temps(data, versions):
    
    N_vals = data.N_val.unique()
    
    fig, axs = plt.subplots(1, 4, figsize=(7,5))
    i = 0
    for N_val in N_vals:
        for version in versions:
            df = data[data.Version==version]
            df = df[df.N_val==N_val]
            
            N = df.N_threads.to_numpy()
            Tn = df.temps.to_numpy()
            
            axs[i].plot(N, Tn, label=f'v{version}', color=colors[version], marker='o')
            axs[i].set_title(f'Val_N={N_val}')
            axs[i].set_xlabel("Nb. thread")
            axs[i].set_ylabel("Elapsed time (sec.)")
            
        i = i + 1
    
    plt.tight_layout()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()
            
            
    
def plot_perf(data, versions, tot_threads, N_vals=None):
    
    N_vals = N_vals if N_vals is not None else data.N_val.unique()
    
    fig, axs = plt.subplots(1, 3, figsize=(8,4))
    i = 0
    for N_val in N_vals:
        
        for version in versions:
            
            df = data[data.Version==version]
            df = df[df.N_val==N_val]
            
            T1 = float(df[df.N_threads == 1].temps)
            N = df.N_threads.to_numpy()
            Tn = df.temps.to_numpy()
            
            (BGm, BAm, SpG, SpA) = get_S(T1, Tn, N)
            (N2pred, SpG_pred, SpA_pred) = predict(BGm, BAm, tot_threads)
            
            
            axs[0].plot(N, T1/Tn, label=f'v{version}-{N_val}',
                        color=colors[i], marker='o')
            axs[0].set_title(f'Mesured')
            axs[0].set_xlabel("N (Nb. thread)")
            axs[0].set_ylabel("T(1)/T(N)")
            
            
            axs[1].plot(N[1:], SpA, label=f'v{version}-{N_val}',
                        color=colors[i], marker='o')
            axs[1].plot(N2pred, SpA_pred, label=f'v{version} pred. (BAm={BAm:.3} | BGm={BGm:.3})',
                        color=colors[i], ls='--')
            axs[1].set_title(f'Amdahl law')
            axs[1].set_xlabel("N (Nb. thread)")
            axs[1].set_ylabel("Speedup")
            
            
            axs[2].plot(N[1:], SpG, label=f'v{version}-{N_val}',
                        color=colors[i], marker='o')
            axs[2].plot(N2pred, SpG_pred, label=f'v{version} pred. (BAm={BAm:.3} | BGm={BGm:.3})',
                        color=colors[i], ls='--')
            axs[2].set_title(f'Gustafson law')
            axs[2].set_xlabel("N (Nb. thread)")
            axs[2].set_ylabel("Scaled speedup")
            i += 1
    
    plt.tight_layout()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()
        
        

def plot_mat_size(data):
    fig, axs = plt.subplots(1, 3, figsize=(8,4))
    
    for i, diag in enumerate(data.diag.unique()):
        for n in data.taille.unique():

            df = data[data.taille==n]
            df = df[df.diag==diag]

            axs[i].plot(df.iters, df.norme, label=f'n={n}')

        axs[i].set_title(f'diag={diag}')

        axs[i].set_ylim((10e-17,10e4))
        axs[i].set_yscale('log')
        axs[i].set_xscale('log')
        axs[i].set_ylabel('Error')
        axs[i].set_xlabel('Iterations')

    plt.tight_layout()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()
    
    
    
    
# Calcul de Pi:
# -------------

data = pd.read_csv('report.csv')
data.columns = [name.strip() for name in data.columns]


plot_errors(data, versions=[1,2,3])
plot_temps(data, versions=[1,2,3])
plot_perf(data, versions=[1], N_vals=[3000000], tot_threads=200)

plot_errors(data, versions=[1,5,6])
plot_temps(data, versions=[1,5,6])
plot_perf(data, versions=[1,6], N_vals=[3000000], tot_threads=200)

plot_errors(data, versions=[1,4])
plot_temps(data, versions=[1,4])
plot_perf(data, versions=[1,4], N_vals=[3000000], tot_threads=200)




# Methode de Jacbi:
# -----------------

# Convergence:
data = pd.read_csv('hist.csv')
data.columns = [name.strip() for name in data.columns]

plot_mat_size(data)


# Performance:
data = pd.read_csv('report_jacob.csv')
names = [name.strip() for name in data.columns]
names[0] = "N_val"
data.columns = names
data["Version"] = [7]*7

plot_perf(data, versions=[7], tot_threads=80)
