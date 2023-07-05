import sys,os
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
plt.rcParams.update({'font.size': 20})

sites = ['APX', 'HAUK', 'KIS', 'KO2', 'MQT', 'NSA']
vars = ['ze', 'dv', 'sw', 'dsd', 'vvd', 'rho']
titles = ['Refl.', 'Dopp. Vel.', 'Spec. Width', 'DSD', 'VVD', 'eD']
units = ['Reflectivity (dBZ)', 'Doppler Velocity (m s$^{-1}$)', 'Spectral Width (m s$^{-1}$)', 'PSD (m$^{-3}$ mm$^{-1}$)', 'Fall Speed (m s$^{-1}$)', 'Effective Density (g cm$^{-3}$)']
refs = ['Vertical Bin', 'Vertical Bin', 'Vertical Bin', 'Mean D$_e$ (mm)', 'Mean D$_e$ (mm)', 'Mean D$_e$ (mm)']

for i,var in enumerate(vars):
    fig, ax = plt.subplots(figsize=(15,15))
    plt.title(titles[i] + " - All Sites Intercomparison")

    if i >= 3:
        plt.ylabel(units[i])
        plt.xlabel(refs[i])
    else:
        plt.xlabel(units[i])
        plt.ylabel(refs[i])
    
    for site in sites:
        print('Loading', 'processed/' + site + '_avg_' + var + '.npy')
        data = np.load('processed/' + site + '_avg_' + var + '.npy')

        if site == 'NSA' and i < 3:
            f = interpolate.interp1d(np.arange(len(data)), data, kind='linear')
            new_indices = np.linspace(0, len(data)-1, 31)
            data = f(new_indices)
            data[:2] = np.nan
            data[30] = np.nan

        if i >= 3:
            plt.plot(np.arange(0.1, 26.2, 0.2), data, linewidth=5, label=site)
            plt.gca().set_xscale('log')
        else:
            plt.plot(data, np.arange(len(data)), linewidth=5, label=site)


    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.065), fancybox=True, shadow=True, ncol=6)
    plt.tight_layout()
    plt.savefig(var + '.png')
    # sys.exit()
        