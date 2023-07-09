import sys,os
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
plt.rcParams.update({'font.size': 20})

sites = ['APX', 'HAUK', 'KIS', 'KO2', 'MQT', 'NSA', 'FIN']
vars = ['ze', 'dv', 'sw', 'dsd', 'vvd', 'rho']
colors = ['r', 'orange', 'c', 'm', 'black', 'b', 'g']
titles = ['Refl.', 'Dopp. Vel.', 'Spec. Width', 'PSD', 'VVD', 'eD']
units = ['Avg. Reflectivity (dBZ)', 'Avg. Doppler Velocity (m s$^{-1}$)', 'Avg. Spectral Width (m s$^{-1}$)', 'Avg. Log PSD (m$^{-3}$ mm$^{-1}$)', 'Avg. Fall Speed (m s$^{-1}$)', 'Avg. Effective Density (g cm$^{-3}$)']
refs = ['Vertical Bin', 'Vertical Bin', 'Vertical Bin', 'D$_e$ (mm)', 'Log D$_e$ (mm)', 'Log D$_e$ (mm)']

for i,var in enumerate(vars):
    fig, ax = plt.subplots(figsize=(15,15))
    plt.title(titles[i] + " - All Sites Intercomparison")

    if i >= 3:
        plt.ylabel(units[i])
        plt.xlabel(refs[i])
    else:
        plt.xlabel(units[i])
        plt.ylabel(refs[i])
    
    for j, site in enumerate(sites):
        print('Loading', 'processed/' + site + '_avg_' + var + '.npy')
        data = np.load('../../data/processed/' + site + '_avg_' + var + '.npy')

        if (site == 'NSA' or site == 'FIN') and i < 3:
            f = interpolate.interp1d(np.arange(len(data)), data, kind='linear')
            new_indices = np.linspace(0, len(data)-1, 31)
            data = f(new_indices)
            data[:2] = np.nan
            data[30] = np.nan

        if i >= 3:
            plt.plot(np.arange(0.1, 26.2, 0.2), data, color=colors[j], linewidth=8, label=site)
            plt.gca().set_xscale('log')
            if i == 3:
                plt.gca().set_yscale('log')
                plt.xlim((0.5, 26.2))
        else:
            plt.plot(data, np.arange(len(data)), color=colors[j], linewidth=8, label=site)


    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.065), fancybox=True, shadow=True, ncol=6)
    plt.tight_layout()
    plt.savefig('../../images/' + var + '.png')
    # sys.exit()
        