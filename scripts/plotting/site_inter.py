import sys,os
import numpy as np
import pandas as pd
import seaborn as sns
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


    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.065), fancybox=True, shadow=True, ncol=7)
    plt.tight_layout()
    plt.savefig('../../images/' + var + '.png')
    # sys.exit()

def plot_n0_lambda():
    lam_bins = np.arange(-1, 1.05, 0.1)
    n0_bins = np.arange(0, 6.2, 0.1)

    fig, axes = plt.subplots(1, 2, figsize=(18, 10))
    fig.suptitle('n$_0$ Dist. Comparisons')
    for j, site in enumerate(sites):
        lam = np.load('../../data/processed/' + site + '_lam.npy')
        n0 = np.load('../../data/processed/' + site + '_n0.npy')
        # axes[0].hist(lam, bins=lam_bins, density=True, histtype='step', alpha=1, color=colors[j], linewidth=3.0, label=site)
        # axes[1].hist(np.ma.log10(n0), bins=n0_bins, density=True, histtype='step', alpha=1, color=colors[j], linewidth=3.0, label=site)
        sns.kdeplot(lam, ax=axes[0], color=colors[j], linewidth=3.0, label=site)
        sns.kdeplot(np.ma.log10(n0), ax=axes[1], color=colors[j], linewidth=3.0, label=site)

    # axes[0].set_xlim(0.1, 1.1)
    axes[0].set_xlabel("Lambda (λ) ($mm^{-1}$)")
    axes[0].set_ylabel("Normalized Counts")
    axes[0].set_title('Lambda Distribution')
    axes[1].set_xlabel("$Log_{10}(N_0)$")
    axes[1].set_ylabel("Normalized Counts")
    axes[1].set_title('$N_{0}$ Distribution')
    # axes[1].set_xlim(0.1, 5)

    plt.tight_layout()
    plt.savefig('../../images/n0_lambda_comparisons.png')

plot_n0_lambda()
            