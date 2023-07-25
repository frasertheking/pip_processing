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
    mrr_path = '/data/LakeEffect/MRR/NetCDF_DN/'
    met_path = '/data/LakeEffect/MetData/'
    NANO_FACTOR = 1000000000
    MIN_INTERVALS_5 = 283

    ### Get matched dates
    ds_met = xr.open_dataset(met_path + '2013-2020_' + site + '.nc')
    times = np.asarray((ds_met['UTC Time'].values / NANO_FACTOR), dtype=int)
    utc_time = pd.to_datetime(times, unit='s', origin='unix')
    utc_time = utc_time.tz_localize('UTC')
    est_time = utc_time.tz_convert('US/Eastern')
    ds_met = ds_met.assign_coords(time=est_time)
    ds_met['time'] = ds_met['time'].astype('datetime64[ns]')

    mrr_dates = []
    for file in list(glob.glob(mrr_path + '*.nc')):                                       
        mrr_dates.append(file[-16:-8])

        
    pip_dates = []
    for file in glob.glob(os.path.join(pip_path, '**', 'edensity_distributions', '*.nc'), recursive=True):
        pip_dates.append(file[-37:-29])

    # mrr_ds_dates = []
    # count = 0
    # for date in mrr_dates:
    #     count += 1
    #     year = int(date[:4])
    #     month = int(date[4:6])
    #     day = int(date[-2:])
    #     ds = ds_met.sel(time=(ds_met['time'].dt.year==year) & (ds_met['time'].dt.month==month) & (ds_met['time'].dt.day==day))
    #     if len(ds.time.values) > 0:
    #         mrr_ds_dates.append(date)
    # df = pd.DataFrame(data={'mrr_ds_dates': mrr_ds_dates})
    # df.to_csv('/data2/fking/s03/data/processed/pca_inputs/mrr_ds_dates.csv')
    # df = pd.read_csv('/data2/fking/s03/data/processed/pca_inputs/mrr_ds_dates.csv')
    # mrr_ds_dates = df['mrr_ds_dates'].tolist()

    # file_dict = defaultdict(list)
    # for filepath in glob.glob(os.path.join(pip_path, '**', '**', '**', '*.nc'), recursive=True):
    #     if 'particle_tables' in filepath:
    #         continue
    #     filename = os.path.basename(filepath)
    #     date = filename[3:11]
    #     file_dict[date].append(filepath)
    # matched_dates = []
    # for date in mrr_ds_dates:
    #     print(date, list(set(file_dict[str(date)])))
    #     if len(list(set(file_dict[str(date)]))) == 4:
    #         matched_dates.append(date)
    # df = pd.DataFrame(data={'matched': matched_dates})
    # df.to_csv('/data2/fking/s03/data/processed/pca_inputs/matched_dates.csv')

    df = pd.read_csv('/data2/fking/s03/data/processed/pca_inputs/matched_dates.csv', dtype={'matched': str})
    matched_dates = df['matched'].tolist()

    print("Matched:", len(matched_dates))
    print(matched_dates)

    N_0_array = []
    lambda_array = []
    total_particle_array = []
    avg_ed_array = []
    avg_sr_array = []
    avg_vvd_array = []
    mwd_array = []
    temp_array = []
    rh_array = []
    ws_array = []
    press_array = []
    wd_array = []
    base_array = []
    top_array = []
    depth_array = []

    number_of_files = 0
    for matched_date in matched_dates:
        print("Working on day", matched_date)
        year = int(matched_date[:4])
        month = int(matched_date[4:6])
        day = int(matched_date[-2:])

        # Load MET data
        ds_met_day = ds_met.sel(time=(ds_met['time'].dt.year==year) & (ds_met['time'].dt.month==month) & (ds_met['time'].dt.day==day))

        # Load MRR data
        ds_mrr_day = xr.open_dataset(mrr_path + 'MRR_NWS_MQT_' + matched_date + '_snow.nc')

        # Load PIP data
        try:
            ds_edensity_lwe_rate = xr.open_dataset(pip_path + str(year) + '_' + site + '/netCDF/edensity_lwe_rate/006' + matched_date + '2350_01_P_Minute.nc')
            ds_edensity_distributions = xr.open_dataset(pip_path + str(year) + '_' + site + '/netCDF/edensity_distributions/006' + matched_date + '2350_01_rho_Plots_D_minute.nc')
            ds_velocity_distributions = xr.open_dataset(pip_path + str(year) + '_' + site + '/netCDF/velocity_distributions/006' + matched_date + '2350_01_vvd_A.nc')
            ds_particle_size_distributions = xr.open_dataset(pip_path + str(year) + '_' + site + '/netCDF/particle_size_distributions/006' + matched_date + '2350_01_dsd.nc')
        except RuntimeError:
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

        # Print results
        # print("\nMET")
        # print(ds_met_day)

        # print("\nMRR")
        # print(ds_mrr_day)

        # print("\nPIP")
        # print(ds_edensity_lwe_rate)
        # print(ds_edensity_distributions)
        # print(ds_velocity_distributions)
        # print(ds_particle_size_distributions)

        if len(ds_met_day['Temp Out'].values[:MIN_INTERVALS_5]) != 283:
            print("MET data record too short for day, skipping!")
            continue

        ########## MRR CALCULATIONS
        data = ds_mrr_day['Ze'].values.T[:,:1440]
        if data.shape[1] < 1440:
            print("MRR data record too short for day, skipping!")
            continue

        data_reshaped = data.reshape(31, 1440 // 5, 5)
        data = np.nanmean(data_reshaped, axis=-1)
        mask = data < -5
        data[mask] = np.nan
        cloud_bases, cloud_tops, cloud_depths = get_cloud_positions(data)

        # Plot MRR data
        # fig, ax = plt.subplots(figsize=(12,3))
        # plt.imshow(data, cmap = cm.gist_ncar, vmin = -10, vmax = 30, aspect='auto', interpolation='bilinear')
        # plt.axhline(y=2, color='gray', linestyle='--')
        # plt.scatter(np.arange(len(cloud_bases)), cloud_bases, color='blue', marker='x')
        # plt.scatter(np.arange(len(cloud_tops)), cloud_tops, color='red', marker='x')
        # plt.plot(np.arange(len(cloud_depths)), cloud_depths, color='black', linestyle='--')
        # plt.gca().invert_yaxis()
        # plt.show()

        base_array.append(cloud_bases)
        top_array.append(cloud_tops)
        depth_array.append(cloud_depths)

        ########## PIP CALCULATIONS
        func = lambda t, a, b: a * np.exp(-b*t)

        # Loop over each 5-minute block
        count = 0
        for i in range(0, dsd_values.shape[0], 5):
            if i >= 1415:
                continue

            count += 1
            block_avg = np.mean(dsd_values[i:i+5, :], axis=0)
            valid_indices = ~np.isnan(block_avg)
            block_avg = block_avg[valid_indices]
            valid_bin_centers = bin_centers[valid_indices]

            if block_avg.size == 0:
                N_0_array.append(np.nan)
                lambda_array.append(np.nan)
                avg_vvd_array.append(np.nan)
                avg_ed_array.append(np.nan)
                avg_sr_array.append(np.nan)
                total_particle_array.append(0)
                mwd_array.append(np.nan)
                continue

            # Calculate average fallspeed over the 5-minute interval
            avg_vvd_array.append(np.nanmean(vvd_values[i:i+5, :], axis=(0, 1)))

            # Calculate the average eDensity of the 5-minute interval
            avg_ed_array.append(np.nanmean(ed_values[i:i+5]))

            # Calculate the average snowfall rate over the 5-minute interval
            avg_sr_array.append(np.nanmean(sr_values[i:i+5]))

            # Calculate total number of particles over the 5-minute interval
            total_particle_array.append(np.nansum(dsd_values[i:i+5, :], axis=(0, 1)))

            # Calculate mean mass diameter over the 5-minute interval
            if edd_values[i:i+5, valid_indices].shape == dsd_values[i:i+5, valid_indices]:
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


        ########## MET CALCULATIONS
        temp_array.append(ds_met_day['Temp Out'].values[:MIN_INTERVALS_5])
        rh_array.append(ds_met_day['RH Out'].values[:MIN_INTERVALS_5])
        ws_array.append(ds_met_day['Wind Speed'].values[:MIN_INTERVALS_5])
        press_array.append(ds_met_day['Pressure'].values[:MIN_INTERVALS_5])
        wd_array.append(ds_met_day['Wind Dir'].values[:MIN_INTERVALS_5])
        number_of_files += 1

    top_array = [item for sublist in top_array for item in sublist]
    base_array = [item for sublist in base_array for item in sublist]
    depth_array = [item for sublist in depth_array for item in sublist]
    temp_array = [item for sublist in temp_array for item in sublist]
    rh_array = [item for sublist in rh_array for item in sublist]
    ws_array = [item for sublist in ws_array for item in sublist]
    press_array = [item for sublist in press_array for item in sublist]
    wd_array = [item for sublist in wd_array for item in sublist]


    df = pd.DataFrame(data={'n0': N_0_array,  'D0': mwd_array, 'Nt': total_particle_array, \
                            'Fs': avg_vvd_array, 'Sr': avg_sr_array,  'Ed': avg_ed_array, \
                            'lambda': lambda_array, 'Ct': top_array, 'Cb': base_array, \
                            'Cd': depth_array, 't': temp_array, 'q': rh_array, 'Ws': ws_array, \
                            'u': press_array, 'Wd': wd_array})
    df.to_csv('/data2/fking/s03/data/processed/pca_inputs/' + site + '.csv')

calc_various_pca_inputs('MQT')

