import sys,os,glob,re
import xarray as xr
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import warnings
from matplotlib.colors import LogNorm
from datetime import datetime, timedelta
from matplotlib.colors import LogNorm
from scipy.optimize import curve_fit
warnings.simplefilter(action='ignore', category=FutureWarning)
plt.rcParams.update({'font.size': 15})

def sanity_check(site, pip_path, mrr_path, match_dates):
    print("\n\n\nPerforming sanity check on", site)

    pip_dates = []
    for year in range(2015, 2023):
        pip_path_temp = os.path.join(pip_path, f"{year}_{site}", "netCDF", "edensity_distributions", "*.nc")
        print(pip_path_temp)
        for file in glob.glob(pip_path_temp):
            pip_dates.append(file[-37:-29])

    matched_dates = []
    files = glob.glob(os.path.join(mrr_path, '*.nc'))
    if not(match_dates):
        matched_dates = files
    else:
        for date in pip_dates:
            if len([f for f in files if date in os.path.basename(f)]) > 0:
                matched_dates.append(date)

    print(matched_dates)
    print("Total Matched:", len(matched_dates))

    def create_hists_for_site(site, match_dates):
        ze_list = []
        dv_list = []
        sw_list = []
        mrr_height_list = []

        dsd_list = []
        dsd_height_list = []
        vvd_list = []
        vvd_height_list = []
        rho_list = []
        rho_height_list = []

        N_0_array = []
        lambda_array = []

        if match_dates:
            for date in matched_dates:
                print("\nWorking on", date)
                year = date[:4]
                month = date[4:6]
                day = date[-2:]
                date = year + month + day

                # MRR
                try:
                    file_pattern = mrr_path + '/*' + date + '*.nc'
                    print(file_pattern)
                    matching_files = glob.glob(file_pattern)
                    print(matching_files)
                    ds_mrr = xr.open_dataset(matching_files[0]) 
                    ze = ds_mrr['Ze'].values
                    dv = ds_mrr['W'].values
                    sw = ds_mrr['spectralWidth'].values
                    mrr_height = np.repeat(np.arange(1, 32), ze.shape[0])

                    ze_list.append(ze.T.flatten())
                    dv_list.append(dv.T.flatten())
                    sw_list.append(sw.T.flatten())
                    mrr_height_list.append(mrr_height)
                    print("MRRs Loaded!")
                except FileNotFoundError:
                    print(f"No file found at {mrr_path + '*' + site + '_' + date + '*.nc'}")
                except Exception as e:
                    print(e)

                # PIP
                try:
                    file_pattern = pip_path + str(year) + '_' + site + '/netCDF/edensity_lwe_rate/*' + date + '*_P_Minute.nc'
                    matching_files = glob.glob(file_pattern)
                    ds_pip = xr.open_dataset(matching_files[0])   
                    ed = ds_pip['ed'].values
                    snow_indices = np.where(ed <= 0.2)[0]
                    print('sponge', ed.shape, np.asarray(snow_indices).shape)

                    file_pattern = pip_path + str(year) + '_' + site + '/netCDF/particle_size_distributions/*' + date + '*_dsd.nc'
                    matching_files = glob.glob(file_pattern)
                    ds_pip = xr.open_dataset(matching_files[0])   
                    dsd = ds_pip['psd'].values
                    bin_centers = ds_pip.bin_centers.values

                    dsd = dsd[snow_indices, :]

                    dsd_height = np.repeat(np.arange(1, 132), dsd.shape[0])
                    dsd_list.append(dsd.T.flatten())
                    dsd_height_list.append(dsd_height)

                    func = lambda t, a, b: a * np.exp(-b*t)

                    # Loop over each minute
                    for i in range(dsd.shape[0] - 14): # Subtract 14 to ensure we can get a 15-min running average for every point
                        running_avg = np.mean(dsd[i:i+15, :], axis=0)
                        valid_indices = ~np.isnan(running_avg)
                        running_avg = running_avg[valid_indices]
                        valid_bin_centers = bin_centers[valid_indices]

                        if running_avg.size == 0:
                            N_0_array.append(np.nan)
                            lambda_array.append(np.nan)
                            continue

                        try:
                            popt, pcov = curve_fit(func, valid_bin_centers, running_avg, p0 = [1e4, 2], maxfev=600)
                            if popt[0] > 0 and popt[0] < 10**7 and popt[1] > 0 and popt[1] < 10:
                                N_0_array.append(popt[0])
                                lambda_array.append(popt[1])
                        except RuntimeError:
                            N_0_array.append(np.nan)
                            lambda_array.append(np.nan)


                    print("PSDs loaded!")
                except FileNotFoundError:
                    print(f"No file found at {pip_path + str(year) + '_' + site + '/netCDF/particle_size_distributions/' + date + '*_dsd.nc'}")
                except Exception as e:
                    print(e)

                try:
                    file_pattern = pip_path + str(year) + '_' + site + '/netCDF/edensity_lwe_rate/*' + date + '*_P_Minute.nc'
                    matching_files = glob.glob(file_pattern)
                    ds_pip = xr.open_dataset(matching_files[0])   
                    ed = ds_pip['ed'].values
                    snow_indices = np.where(ed <= 0.2)[0]

                    file_pattern = pip_path + str(year) + '_' + site + '/netCDF/velocity_distributions/*' + date + '*_vvd_A.nc'
                    matching_files = glob.glob(file_pattern)
                    ds_pip = xr.open_dataset(matching_files[0])   
                    vvd = ds_pip['vvd'].values

                    vvd = vvd[snow_indices, :]

                    vvd_height = np.repeat(np.arange(1, 132), vvd.shape[0])
                    vvd_list.append(vvd.T.flatten())
                    vvd_height_list.append(vvd_height)
                    print("VVDs loaded!")
                except FileNotFoundError:
                    print(f"No file found at {pip_path + str(year) + '_' + site + '/netCDF/velocity_distributions/*' + date + '*_vvd_A.nc'}")
                except Exception as e:
                    print(f"No file found at {pip_path + str(year) + '_' + site + '/netCDF/velocity_distributions/*' + date + '*_vvd_A.nc'}")

                try:
                    file_pattern = pip_path + str(year) + '_' + site + '/netCDF/edensity_lwe_rate/*' + date + '*_P_Minute.nc'
                    matching_files = glob.glob(file_pattern)
                    ds_pip = xr.open_dataset(matching_files[0])   
                    ed = ds_pip['ed'].values
                    snow_indices = np.where(ed <= 0.2)[0]

                    file_pattern =  pip_path + str(year) + '_' + site + '/netCDF/edensity_distributions/*' + date + '*_rho_Plots_D_minute.nc'
                    matching_files = glob.glob(file_pattern)
                    ds_pip = xr.open_dataset(matching_files[0])  
                    rho = ds_pip['rho'].values

                    rho = rho[snow_indices, :]

                    rho_height = np.repeat(np.arange(1, 132), rho.shape[0])
                    rho_list.append(rho.T.flatten())
                    rho_height_list.append(rho_height)
                    print("EDs loaded!")
                except FileNotFoundError:
                    print(f"No file found at {pip_path + str(year) + '_' + site + '/netCDF/edensity_distributions/*' + date + '*_rho_Plots_D_minute.nc'}")
                except Exception as e:
                    print(f"No file found at {pip_path + str(year) + '_' + site + '/netCDF/edensity_distributions/*' + date + '*_rho_Plots_D_minute.nc'}")
        else:
            for date in matched_dates:
                ds_mrr = xr.open_dataset(date) 
                ze = ds_mrr['Ze'].values
                dv = ds_mrr['W'].values
                sw = ds_mrr['spectralWidth'].values
                mrr_height = np.repeat(np.arange(1, 32), ze.shape[0])

                ze_list.append(ze.T.flatten())
                dv_list.append(dv.T.flatten())
                sw_list.append(sw.T.flatten())
                mrr_height_list.append(mrr_height)
                print("MRRs Loaded!")
            for date in pip_dates:
                year = date[:4]
                month = date[4:6]
                day = date[-2:]
                date = year + month + day
                # PIP
                try:
                    file_pattern = pip_path + str(year) + '_' + site + '/netCDF/particle_size_distributions/*' + date + '*_dsd.nc'
                    matching_files = glob.glob(file_pattern)
                    ds_pip = xr.open_dataset(matching_files[0])   
                    dsd = ds_pip['psd'].values
                    bin_centers = ds_pip.bin_centers.values
                    dsd_height = np.repeat(np.arange(1, 132), dsd.shape[0])
                    dsd_list.append(dsd.T.flatten())
                    dsd_height_list.append(dsd_height)

                    func = lambda t, a, b: a * np.exp(-b*t)

                    # Loop over each minute
                    for i in range(dsd.shape[0] - 14): # Subtract 14 to ensure we can get a 15-min running average for every point
                        running_avg = np.mean(dsd[i:i+15, :], axis=0)
                        valid_indices = ~np.isnan(running_avg)
                        running_avg = running_avg[valid_indices]
                        valid_bin_centers = bin_centers[valid_indices]

                        if running_avg.size == 0:
                            N_0_array.append(np.nan)
                            lambda_array.append(np.nan)
                            continue

                        try:
                            popt, pcov = curve_fit(func, valid_bin_centers, running_avg, p0 = [1e4, 2], maxfev=600)
                            if popt[0] > 0 and popt[0] < 10**7 and popt[1] > 0 and popt[1] < 10:
                                N_0_array.append(popt[0])
                                lambda_array.append(popt[1])
                        except RuntimeError:
                            N_0_array.append(np.nan)
                            lambda_array.append(np.nan)

                    print("PSDs loaded!")
                except FileNotFoundError:
                    print(f"No file found at {pip_path + str(year) + '_' + site + '/netCDF/particle_size_distributions/' + date + '*_dsd.nc'}")
                except Exception as e:
                    print(e)

                try:
                    file_pattern = pip_path + str(year) + '_' + site + '/netCDF/velocity_distributions/*' + date + '*_vvd_A.nc'
                    matching_files = glob.glob(file_pattern)
                    ds_pip = xr.open_dataset(matching_files[0])   
                    vvd = ds_pip['vvd'].values
                    vvd_height = np.repeat(np.arange(1, 132), vvd.shape[0])
                    vvd_list.append(vvd.T.flatten())
                    vvd_height_list.append(vvd_height)
                    print("VVDs loaded!")
                except FileNotFoundError:
                    print(f"No file found at {pip_path + str(year) + '_' + site + '/netCDF/velocity_distributions/*' + date + '*_vvd_A.nc'}")
                except Exception as e:
                    print(f"No file found at {pip_path + str(year) + '_' + site + '/netCDF/velocity_distributions/*' + date + '*_vvd_A.nc'}")

                try:
                    file_pattern =  pip_path + str(year) + '_' + site + '/netCDF/edensity_distributions/*' + date + '*_rho_Plots_D_minute.nc'
                    matching_files = glob.glob(file_pattern)
                    ds_pip = xr.open_dataset(matching_files[0])  
                    rho = ds_pip['rho'].values
                    rho_height = np.repeat(np.arange(1, 132), rho.shape[0])
                    rho_list.append(rho.T.flatten())
                    rho_height_list.append(rho_height)
                    print("EDs loaded!")
                except FileNotFoundError:
                    print(f"No file found at {pip_path + str(year) + '_' + site + '/netCDF/edensity_distributions/*' + date + '*_rho_Plots_D_minute.nc'}")
                except Exception as e:
                    print(f"No file found at {pip_path + str(year) + '_' + site + '/netCDF/edensity_distributions/*' + date + '*_rho_Plots_D_minute.nc'}")


        def prepare_data(data_list, height_list, range):
            data_ds = np.concatenate(data_list)
            height_ds = np.concatenate(height_list)
            data_x = np.asarray(data_ds).flatten()
            height_y = np.asarray(height_ds).flatten()

            data_x[data_x < range[0]] = np.nan
            data_x[data_x > range[1]] = np.nan

            mask = ~np.isnan(data_x)
            data_x = data_x[mask]
            height_y = height_y[mask]
            
            return data_x, height_y

        def plot_mrr_histogram(ax, x, y, title, color, xlabel, xlim):
            hist, xedges, yedges = np.histogram2d(y, x, bins=[28, 128])
            ax.set_title(title)
            ax.imshow(hist, origin='lower', cmap=color, aspect='auto', extent=[yedges[0], yedges[-1], xedges[0], xedges[-1]])
            ax.invert_yaxis()
            ax.set_xlim(xlim)
            ax.set_xlabel(xlabel)

        def plot_pip_histogram(ax, x, y, title, color, xlabel, bins):
            hist, xedges, yedges = np.histogram2d(y, x, bins=[np.arange(0,26,1), bins])
            ax.set_title(title)
            ax.imshow(hist.T, origin='lower', cmap=color, aspect='auto', extent=[yedges[0], yedges[-1], xedges[0], xedges[-1]])
            ax.set_xlabel(xlabel)

        def plot_mrr_figures(site, ze_data, dv_data, sw_data):
            fig, axes = plt.subplots(1, 3, figsize=(16,6), sharey=True)
            fig.suptitle(site + ' MRR')
            axes[0].set_ylabel("Height (km)")

            plot_mrr_histogram(axes[0], ze_data[0], ze_data[1], "Reflectivity", 'Reds', "dBZ", (-20, 30))
            plot_mrr_histogram(axes[1], dv_data[0], dv_data[1], "Doppler Velocity", 'Blues', "m s$^{-1}$", (-5, 5))
            plot_mrr_histogram(axes[2], sw_data[0], sw_data[1], "Spectral Width", 'Oranges', "m s$^{-1}$", (0, 0.5))

            plt.tight_layout()
            plt.savefig('../../images/' + site + '_mrr.png')

        def plot_pip_figures(site, dsd_data, vvd_data, rho_data):
            fig, axes = plt.subplots(1, 3, figsize=(16,6))
            fig.suptitle(site + ' PIP')
            axes[0].set_xlabel("Mean D$_e$ (mm)")
            axes[1].set_xlabel("Mean D$_e$ (mm)")
            axes[2].set_xlabel("Mean D$_e$ (mm)")

            plot_pip_histogram(axes[0], np.ma.log10(dsd_data[0]), dsd_data[1], "Particle Size Distribution", 'plasma', "Log$_{10}$ PSD (m$^{-3}$ mm$^{-1}$)", np.linspace(.001,5,54))
            plot_pip_histogram(axes[1], vvd_data[0], vvd_data[1], "Velocity Distribution", 'plasma', "Fall Speed (m s$^{−1}$)", np.arange(0.1,5.1,0.1))
            plot_pip_histogram(axes[2], rho_data[0], rho_data[1], "eDensity Distribution", 'plasma', "Effective Density (g cm$^{-3}$)", np.arange(0.01,1.01,0.01))

            plt.tight_layout()
            plt.savefig('../../images/' + site + '_pip.png')

        def process_mrr_data(site, ze_list, mrr_height_list, dv_list, sw_list):
            ze_data = prepare_data(ze_list, mrr_height_list, [-30, np.inf])
            dv_data = prepare_data(dv_list, mrr_height_list, [-30, 30])
            sw_data = prepare_data(sw_list, mrr_height_list, [0, 1])

            plot_mrr_figures(site, ze_data, dv_data, sw_data)

        def process_pip_data(site, dsd_list, dsd_height_list, vvd_list, vvd_height_list, rho_list, rho_height_list):
            dsd_data = prepare_data(dsd_list, dsd_height_list, [0, np.inf])
            vvd_data = prepare_data(vvd_list, vvd_height_list, [0, np.inf])
            rho_data = prepare_data(rho_list, rho_height_list, [0, np.inf])

            plot_pip_figures(site, dsd_data, vvd_data, rho_data)

        def plot_n0_lambda(site, lam, n0, lam_bins, n0_bins):
            n0_lambda_hist = np.histogram2d(np.ma.log10(lam), np.ma.log10(n0), (lam_bins, n0_bins))
            fig, axes = plt.subplots(1, 3, figsize=(16,6))
            fig.suptitle(site + ' n$_0$ Lambda Summary')

            pcm = axes[0].pcolormesh(lam_bins, n0_bins, np.ma.masked_less(n0_lambda_hist[0].T, 10), vmin=0, cmap="viridis")
            axes[0].set_xlim(-0.4, 1.0)
            axes[0].set_ylim(0, 6)
            axes[0].set_ylabel("$Log_{10}(N_{0})$")
            axes[0].set_xlabel("$Log_{10}(λ)$")

            cb = fig.colorbar(pcm, ax=axes[0], extend="max")
            cb.set_label(label="Counts", size=14)

            axes[1].hist(lam, bins=lam_bins, density=True, histtype='step', alpha=0.7, color="red", linewidth=3.0)
            axes[1].set_xlim(0.3, 8)
            axes[1].set_xlabel("Lambda (λ) [$mm^{-1}$]", size=14)
            axes[1].set_ylabel("Normalized Counts", size=14)

            axes[2].hist(np.ma.log10(n0), bins=n0_bins, density=True, histtype='step', alpha=0.7, color="red", linewidth=3.0)
            axes[2].set_xlabel("$Log_{10}(N_0)$", size=14)
            axes[2].set_ylabel("Normalized Counts", size=14)
            axes[2].set_xlim(1, 6)
            plt.tight_layout()
            plt.savefig('../../images/' + site + '_n0_lambda.png')

        # Call the process_data function with the appropriate data lists
        process_mrr_data(site, ze_list, mrr_height_list, dv_list, sw_list)
        process_pip_data(site, dsd_list, dsd_height_list, vvd_list, vvd_height_list, rho_list, rho_height_list)
        plot_n0_lambda(site, lambda_array, N_0_array, np.arange(-1, 1.05, 0.05), np.arange(0, 6.2, 0.2))

    create_hists_for_site(site, match_dates)

sanity_check('APX', '/data2/fking/s03/converted/', '/data/APX/MRR/NetCDF', True)
# sanity_check('MQT', '/data/LakeEffect/PIP/Netcdf_Converted/', '/data/LakeEffect/MRR/NetCDF_DN/', False)
# sanity_check('HAUK', '/data2/fking/s03/converted/', '/data/HiLaMS/HAUK/MRR/NetCDF/', False)
# sanity_check('KIS', '/data2/fking/s03/converted/', '/data/HiLaMS/KIR/MRR/NetCDF/', False)
# sanity_check('KO2', '/data2/fking/s03/converted/', '/data2/fking/s03/data/ICE_POP/MRR/KO2/', False)
