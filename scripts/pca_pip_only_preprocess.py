import glob, os
import xarray as xr
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import warnings

from collections import defaultdict
from datetime import datetime, timedelta
from scipy.optimize import curve_fit
warnings.filterwarnings("ignore")
warnings.simplefilter(action='ignore', category=FutureWarning)
plt.rcParams.update({'font.size': 15})

def get_cloud_positions(data):
    cloud_bases = []
    cloud_tops = []

    for col in data.T:  # Transpose to loop over columns
        cloud_base = np.nan
        cloud_top = np.nan
        count = 0
        
        for i in range(len(col)):
            if not np.isnan(col[i]):
                if np.isnan(cloud_base):  # Start of the cloud
                    cloud_base = i
                count += 1
            else:
                if not np.isnan(cloud_base) and count >= 4:  # End of the cloud
                    cloud_top = i - 1  # The last non-NaN value
                    break
                else:  # Reset
                    cloud_base = np.nan
                    count = 0

        if not np.isnan(cloud_base) and (cloud_top is None or np.isnan(cloud_top)):
            # In case the cloud goes up to the last bin in the column
            if count >= 4:
                cloud_top = len(col) - 1
            else:
                # Cloud size is less than 4, reset
                cloud_base = np.nan
                
        cloud_bases.append(cloud_base)
        cloud_tops.append(cloud_top)

    return np.array(cloud_bases)[:283], np.array(cloud_tops)[:283], (np.array(cloud_tops) - np.array(cloud_bases))[:283]


def calc_various_pca_inputs(site):
    print("Working on site " + site)

    ### Globals
    pip_path = '/data/LakeEffect/PIP/Netcdf_Converted/'
        
    pip_dates = []
    for file in glob.glob(os.path.join(pip_path, '**', 'edensity_distributions', '*.nc'), recursive=True):
        pip_dates.append(file[-37:-29])

    N_0_array = []
    lambda_array = []
    total_particle_array = []
    avg_ed_array = []
    avg_rho_array = []
    avg_sr_array = []
    avg_vvd_array = []
    mwd_array = []
    times = []

    number_of_files = 0
    for date in pip_dates:
        print("Working on day", date)
        
        year = int(date[:4])
        month = int(date[4:6])
        day = int(date[-2:])

        # Load PIP data
        try:
            ds_edensity_lwe_rate = xr.open_dataset(pip_path + str(year) + '_' + site + '/netCDF/edensity_lwe_rate/006' + date + '2350_01_P_Minute.nc')
            ds_edensity_distributions = xr.open_dataset(pip_path + str(year) + '_' + site + '/netCDF/edensity_distributions/006' + date + '2350_01_rho_Plots_D_minute.nc')
            ds_velocity_distributions = xr.open_dataset(pip_path + str(year) + '_' + site + '/netCDF/velocity_distributions/006' + date + '2350_01_vvd_A.nc')
            ds_particle_size_distributions = xr.open_dataset(pip_path + str(year) + '_' + site + '/netCDF/particle_size_distributions/006' + date + '2350_01_dsd.nc')
        except FileNotFoundError:
            print("Could not open PIP file, likely ended before 2350")
            continue
        
        dsd_values = ds_particle_size_distributions['psd'].values
        edd_values = ds_edensity_distributions['rho'].values
        vvd_values = ds_velocity_distributions['vvd'].values
        sr_values = ds_edensity_lwe_rate['nrr'].values
        ed_values = ds_edensity_lwe_rate['ed'].values
        bin_centers = ds_particle_size_distributions['bin_centers'].values

        if len(ds_particle_size_distributions.time) != 1440:
            print("PIP data record too short for day, skipping!")
            continue

        ########## PIP CALCULATIONS
        func = lambda t, a, b: a * np.exp(-b*t)

        # Initialize the datetime object at the start of the day
        current_time = datetime(year, month, day, 0, 0)

        # Loop over each 5-minute block
        count = 0
        for i in range(0, dsd_values.shape[0], 5):
            if i >= 1435:
                continue

            count += 1
            block_avg = np.mean(dsd_values[i:i+5, :], axis=0)
            valid_indices = ~np.isnan(block_avg)
            block_avg = block_avg[valid_indices]
            valid_bin_centers = bin_centers[valid_indices]

            times.append(current_time.strftime("%Y-%m-%d %H:%M:%S"))
            current_time += timedelta(minutes=5)

            if block_avg.size == 0:
                N_0_array.append(np.nan)
                lambda_array.append(np.nan)
                avg_vvd_array.append(np.nan)
                avg_ed_array.append(np.nan)
                avg_rho_array.append(np.nan)
                avg_sr_array.append(np.nan)
                total_particle_array.append(0)
                mwd_array.append(np.nan)
                continue

            # Calculate average fallspeed over the 5-minute interval
            avg_vvd_array.append(np.nanmean(vvd_values[i:i+5, :], axis=(0, 1)))

            # Calculate the average eDensity of the 5-minute interval
            avg_ed_array.append(np.nanmean(ed_values[i:i+5]))

            # Calculate the average eDensity of the 5-minute interval
            avg_rho_array.append(np.nanmean(edd_values[i:i+5]))

            # Calculate the average snowfall rate over the 5-minute interval
            avg_sr_array.append(np.nanmean(sr_values[i:i+5]))

            # Calculate total number of particles over the 5-minute interval
            total_particle_array.append(np.nansum(dsd_values[i:i+5, :], axis=(0, 1)))

            # Calculate mean mass diameter over the 5-minute interval
            if edd_values[i:i+5, valid_indices].shape == dsd_values[i:i+5, valid_indices].shape:
                mass_dist = edd_values[i:i+5, valid_indices] * dsd_values[i:i+5, valid_indices] * (4/3) * np.pi * (valid_bin_centers/2)**3
                mass_weighted_diameter = np.sum(mass_dist * valid_bin_centers) / np.sum(mass_dist)
                mwd_array.append(mass_weighted_diameter)
            else:
                mwd_array.append(np.nan)

            # Calculate N0 and Lambda
            try:
                popt, pcov = curve_fit(func, valid_bin_centers, block_avg, p0 = [1e4, 2], maxfev=600)
                if popt[0] > 0 and popt[0] < 10**7 and popt[1] > 0 and popt[1] < 10:
                    N_0_array.append(popt[0])
                    lambda_array.append(popt[1])
                else:
                    N_0_array.append(np.nan)
                    lambda_array.append(np.nan)

            except RuntimeError:
                N_0_array.append(np.nan)
                lambda_array.append(np.nan)


        number_of_files += 1


    df = pd.DataFrame(data={'time': times, 'n0': N_0_array,  'D0': mwd_array, 'Nt': total_particle_array, \
                            'Fs': avg_vvd_array, 'Sr': avg_sr_array,  'Ed': avg_ed_array, \
                            'Rho': avg_rho_array, 'lambda': lambda_array})
    
    df = df.dropna()
    df = df[(df['Ed'] >= 0)]
    df['type'] = df['Ed'].apply(lambda x: 'snow' if x < 0.4 else 'rain')
    df.to_csv('/data2/fking/s03/data/processed/pca_inputs/' + site + '_pip.csv')

def plot_corr(df, size=12):
    # Calculate correlations
    corr_df = df.drop(columns=['type'])
    print(corr_df)
    corr = corr_df.corr()
    
    # Calculate the correlation sum
    corr_sum = corr.sum().sort_values(ascending=False)
    
    # Reorder the dataframe according to the correlation sum
    corr = corr.loc[corr_sum.index, corr_sum.index]

    # Create a DataFrame correlation plot
    fig, ax = plt.subplots(figsize=(size, size))
    plt.title("PSD Variable Correlation Matrix")
    h = ax.matshow(corr, cmap='bwr', vmin=-1, vmax=1)
    fig.colorbar(h, ax=ax, label='Correlation')  # Use fig.colorbar() to make the colorbar the same height as the plot
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.tight_layout()
    plt.savefig('/data2/fking/s03/images/corr.png')

    df = df[(df['Log10_n0'] >= 0)]
    df = df[(df['Log10_lambda'] <= 1)]
    df = df[(df['Log10_Rho'] >= -4)]
    df = df[(df['Log10_Ed'] >= -2)]
    df = df[(df['Log10_Ed'] <= 0.5)]
    sns_plot = sns.pairplot(df, kind="hist", diag_kind="kde", hue='type', height=5, palette=['blue', 'red'], corner=True)
    sns_plot.map_lower(sns.kdeplot, levels=4, color=".2")
    sns_plot.savefig('/data2/fking/s03/images/output_kde.png')

def load_and_plot_pca_for_site(site):
    df = pd.read_csv('/data2/fking/s03/data/processed/pca_inputs/' + site + '_pip.csv')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Log10_n0'] = df['n0'].apply(np.log10)
    df['Log10_lambda'] = df['lambda'].apply(np.log10)
    df['Log10_Ed'] = df['Ed'].apply(np.log10)
    df['Log10_Fs'] = df['Fs'].apply(np.log10)
    df['Log10_Rho'] = df['Rho'].apply(np.log10)
    df['Log10_D0'] = df['D0'].apply(np.log10)
    df['Log10_Sr'] = df['Sr'].apply(np.log10)
    df['Log10_Nt'] = df['Nt'].apply(np.log10)
    df.drop(columns=['Nt', 'n0', 'lambda', 'Ed', 'D0', 'Sr', 'Fs', 'Rho'], inplace=True)
    print(df.describe())
    plot_corr(df)
    print(df)

if __name__ == '__main__':
    calc_various_pca_inputs('MQT')
    # load_and_plot_pca_for_site('MQT')

