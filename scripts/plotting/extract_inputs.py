import sys,os
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def calc_various_psd_inputs(date):
    print("Working on " + date)
    psd_path = '../../data/PIP/2019_MQT/netCDF/particle_size_distributions/006' + date + '2350_01_dsd.nc'
    ed_path = '../../data/PIP/2019_MQT/netCDF/edensity_distributions/006' + date + '2350_01_rho_Plots_D_minute.nc'
    vvd_path = '../../data/PIP/2019_MQT/netCDF/velocity_distributions/006' + date + '2350_01_vvd_A.nc'
    sr_path = '../../data/PIP/2019_MQT/netCDF/edensity_lwe_rate/006' + date + '2350_01_P_Minute.nc'

    try:
        ds_psd = xr.open_dataset(psd_path)   
        psd = ds_psd['psd'].values
        bin_centers = ds_psd.bin_centers.values

        ds_ed = xr.open_dataset(ed_path)   
        rho = ds_ed['rho'].values

        ds_sr = xr.open_dataset(sr_path)   
        ed = ds_sr['ed'].values
        sr = ds_sr['nrr'].values

        ds_vvd = xr.open_dataset(vvd_path)   
        vvd = ds_vvd['vvd'].values
    except Exception as e:
        print(e)

    N_0_array = []
    lambda_array = []
    total_particle_array = []
    avg_ed_array = []
    avg_sr_array = []
    avg_vvd_array = []
    mmd_array = []

    func = lambda t, a, b: a * np.exp(-b*t)

    for i in range(psd.shape[0] - 14):
        avg_vvd_array.append(np.nanmean(vvd[i:i+15, :], axis=(0,1)))
        avg_ed_array.append(np.nanmean(ed[i:i+15]))
        avg_sr_array.append(np.nanmean(sr[i:i+15]))

        running_avg = np.nanmean(psd[i:i+15, :], axis=0)
        valid_indices = ~np.isnan(running_avg)

        running_avg = running_avg[valid_indices]
        valid_bin_centers = bin_centers[valid_indices]

        total_particles = np.nansum(psd[i:i+15, :], axis=(0, 1))
        total_particle_array.append(total_particles)

        mass_dist = rho[i:i+15, valid_indices] * psd[i:i+15, valid_indices] * (4/3) * np.pi * (valid_bin_centers/2)**3
        mass_dist_sum = np.nansum(mass_dist, axis=0)
        
        if mass_dist_sum.size != 0:
            cum_mass_dist = np.cumsum(mass_dist_sum)
            mmd = np.interp(0.5 * cum_mass_dist[-1], cum_mass_dist, valid_bin_centers)
        
            if mmd > 25 and (np.all(cum_mass_dist==0)):
                mmd = 0

            mmd_array.append(mmd)
        else:
            mmd_array.append(np.nan)

        try:
            popt, pcov = curve_fit(func, valid_bin_centers, running_avg, p0 = [1e4, 2], maxfev=600)
            if popt[0] > 0 and popt[0] < 10**7 and popt[1] > 0 and popt[1] < 10:
                N_0_array.append(popt[0])
                lambda_array.append(popt[1])
            else:
                N_0_array.append(np.nan)
                lambda_array.append(np.nan)
                
        except Exception as e:
                N_0_array.append(np.nan)
                lambda_array.append(np.nan)

    df = pd.DataFrame(data={'n0': N_0_array,  'D0': mmd_array, 'Nt': total_particle_array, 'VVD': avg_vvd_array, 'Sr': avg_sr_array,  'eD': avg_ed_array, 'lambda': lambda_array})
    df.to_csv('../../data/processed/psd_inputs/' + date + '.csv')
    print("Saved " + date + ' to ' + '../../data/processed/psd_inputs/' + date + '.csv')

calc_various_psd_inputs('20190213')


#### PLOTTING

# def plot_corr(df,size=10):
#     corr = df.corr()
#     fig, ax = plt.subplots(figsize=(size, size))
#     ax.matshow(corr, cmap='bwr')
#     plt.xticks(range(len(corr.columns)), corr.columns)
#     plt.yticks(range(len(corr.columns)), corr.columns)
#     plt.savefig('../images/corr.png')

# plot_corr(df)

# fig, ax = plt.subplots(figsize=(12,12))
# for i, n0 in enumerate(N_0_array):
#     t = np.arange(131)
#     y = func(t, n0, lambda_array[i])
#     plt.plot(t, y)
# ax.set_yscale('log')
# plt.savefig('../images/01_psds.png')

# x_values = range(len(total_particle_array))
# plt.figure(figsize=(15,6)) 
# plt.bar(x_values, total_particle_array, align='center', alpha=0.5)
# plt.xlabel('Time Interval Index')
# plt.ylabel('Total Particle Count')
# plt.title('Total Particle Count for Each 15-Minute Interval')
# plt.savefig('../images/01_totals.png')

# x_values = range(len(ed))
# plt.figure(figsize=(15,6)) 
# plt.bar(x_values, ed, align='center', alpha=0.5)
# plt.xlabel('Time Interval Index')
# plt.ylabel('Average eDensity')
# plt.title('Average ED for Each 15-Minute Interval')
# plt.savefig('../images/01_eds.png')

# x_values = range(len(sr))
# plt.figure(figsize=(15,6)) 
# plt.bar(x_values, sr, align='center', alpha=0.5)
# plt.xlabel('Time Interval Index')
# plt.ylabel('Average Snowfall')
# plt.title('Average Snowfall for Each 15-Minute Interval')
# plt.savefig('../images/01_srs.png')

# x_values = range(len(avg_vvd_array))
# plt.figure(figsize=(15,6)) 
# plt.bar(x_values, avg_vvd_array, align='center', alpha=0.5)
# plt.xlabel('Time Interval Index')
# plt.ylabel('Average Fallspeed (m/s)')
# plt.title('Average VVD for Each 15-Minute Interval')
# plt.savefig('../images/01_vvds.png')

# # Plot MMD for each 15-minute interval
# x_values = range(len(mmd_array))
# plt.figure(figsize=(15,6)) 
# plt.bar(x_values, mmd_array, align='center', alpha=0.5)
# plt.xlabel('Time Interval Index')
# plt.ylabel('Median Mass Diameter')
# plt.title('Median Mass Diameter for Each 15-Minute Interval')
# plt.savefig('../images/01_mmds.png')