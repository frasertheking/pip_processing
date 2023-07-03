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

    mrr_dates = []
    for filename in files:
        match = re.search(r'\d{8}', filename)
        if match:
            mrr_dates.append(match.group())

    if not(match_dates):
        matched_dates = files
    else:
        for date in pip_dates:
            if len([f for f in files if date in os.path.basename(f)]) > 0:
                matched_dates.append(date)

    print("Total Matched:", len(matched_dates))

    if match_dates:
        m_dates = pd.to_datetime(matched_dates, format='%Y%m%d')
        mrr_dates = pd.to_datetime(mrr_dates, format='%Y%m%d')
        pip_dates = pd.to_datetime(pip_dates, format='%Y%m%d')
        # met_dates = pd.to_datetime(met_dates, format='%Y%m%d')

        m_date_data = np.full(len(matched_dates), 0)
        mrr_date_data = np.full(len(mrr_dates), 1)
        pip_date_data = np.full(len(pip_dates), 2)
        # met_date_data = np.full(len(met_dates), 2)

        fig, ax = plt.subplots(figsize=(15, 3))
        plt.title(site + ' Data Temporal Coverage (matched $n=' + str(len(matched_dates)) + '$ days)')
        plt.scatter(m_dates, m_date_data, marker='|', s=250, color='black')
        plt.scatter(mrr_dates, mrr_date_data, marker='|', s=250, color='red')
        plt.scatter(pip_dates, pip_date_data, marker='|', s=250, color='blue')
        # plt.scatter(met_dates, met_date_data, marker='|', s=250, color='red')
        plt.xlabel('Dates')
        plt.ylabel('Data Availability')
        ax.set_ylim((-1, 3))
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(['All', 'MRR', 'PIP'])
        plt.tight_layout()
        plt.savefig('../../images/' + site + '_matched_data.png')

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

        total_snowing_minutes = 0

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
                    matching_files = glob.glob(file_pattern)
                    ds_mrr = xr.open_dataset(matching_files[0]) 

                    ze = -1
                    dv = -1
                    sw = -1
                    if site == 'NSA':
                        stn = ds_mrr['signal_to_noise_ratio_copol'].values
                        ze = ds_mrr['reflectivity_copol'].values
                        dv = ds_mrr['mean_doppler_velocity_copol'].values
                        sw = ds_mrr['spectral_width_copol'].values

                        mask = np.where(stn > -20, 1, 0)

                        # Apply the mask to the other arrays
                        ze_masked = np.where(mask, ze, np.nan)
                        dv_masked = np.where(mask, dv, np.nan)
                        sw_masked = np.where(mask, sw, np.nan)

                        # Clip the arrays to only look at the bottom 98 rows
                        ze = ze_masked[-98:]
                        dv = dv_masked[-98:]
                        sw = sw_masked[-98:]
                    else:
                        ze = ds_mrr['Ze'].values
                        dv = ds_mrr['W'].values
                        sw = ds_mrr['spectralWidth'].values

                    file_pattern = pip_path + str(year) + '_' + site + '/netCDF/edensity_lwe_rate/*' + date + '*_P_Minute.nc'
                    matching_files = glob.glob(file_pattern)
                    ds_pip = xr.open_dataset(matching_files[0])   
                    ed = ds_pip['ed'].values
                    snow_indices = np.where(ed <= 0.2)[0]
                    total_snowing_minutes += len(snow_indices)
                    
                    ze = ze[snow_indices, :]
                    mrr_height = np.repeat(np.arange(1, 32), ze.shape[0])
                    dv = dv[snow_indices, :]
                    sw = sw[snow_indices, :]

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
            hist, xedges, yedges = np.histogram2d(y, x, bins=[28, 256])
            ax.set_title(title)
            hist = 100 * hist / np.sum(hist)
            im = ax.imshow(hist, origin='lower', cmap=color, aspect='auto', extent=[yedges[0], yedges[-1], xedges[0], xedges[-1]], interpolation='none')
            ax.set_xlim(xlim)
            ax.set_xlabel(xlabel)
            cbar = ax.figure.colorbar(im, ax=ax)
            cbar.ax.set_ylabel('Counts (%)')

        def plot_pip_histogram(ax, x, y, title, color, xlabel, bins, log_scale=False):
            hist, xedges, yedges = np.histogram2d(y, x, bins=[np.arange(0,26,1), bins])
            ax.set_title(title)
            ax.set_facecolor('black')
            hist = 100 * hist / np.sum(hist)
            if log_scale:
                norm = LogNorm()
            else:
                norm = None

            im = ax.imshow(hist.T, origin='lower', cmap=color, aspect='auto', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], norm=norm, interpolation='none')

            ax.set_ylabel(xlabel)
            ax.set_xlabel("Mean D$_e$ (mm)")
            cbar = ax.figure.colorbar(im, ax=ax)
            cbar.ax.set_ylabel('Counts (%)')

        def plot_mrr_figures(site, ze_data, dv_data, sw_data, match_dates):
            fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
            if match_dates:
                fig.suptitle(site + ' MRR (Data Matched to PIP)')
            else:
                fig.suptitle(site + ' MRR all data')
            axes[0].set_ylabel("Bin")

            plot_mrr_histogram(axes[0], ze_data[0], ze_data[1], "Reflectivity", 'Reds', "dBZ", (-20, 30))
            plot_mrr_histogram(axes[1], dv_data[0], dv_data[1], "Doppler Velocity", 'Blues', "m s$^{-1}$", (-5, 5))
            plot_mrr_histogram(axes[2], sw_data[0], sw_data[1], "Spectral Width", 'Oranges', "m s$^{-1}$", (0, 0.5))

            plt.tight_layout()
            plt.savefig('../../images/' + site + '_mrr_' + str(match_dates) + '.png')

        def plot_pip_figures(site, dsd_data, vvd_data, rho_data, total_snowing_minutes, match_dates):
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            if match_dates:
                fig.suptitle(site + ' PIP (Data Matched to MRR) : # Snow Mins. = ' + str(total_snowing_minutes))
            else:
                fig.suptitle(site + ' PIP all data')


            plot_pip_histogram(axes[0], np.ma.log10(dsd_data[0]), dsd_data[1], "Particle Size Distribution", 'magma', "Log$_{10}$ PSD (m$^{-3}$ mm$^{-1}$)", np.linspace(.001, 5, 256), True)
            plot_pip_histogram(axes[1], vvd_data[0], vvd_data[1], "Velocity Distribution", 'magma', "Fall Speed (m s$^{−1}$)", np.arange(0.1, 5.1, 0.005))
            plot_pip_histogram(axes[2], rho_data[0], rho_data[1], "eDensity Distribution", 'magma', "Effective Density (g cm$^{-3}$)", np.arange(0.01, 1.01, 0.005))

            plt.tight_layout()
            plt.savefig('../../images/' + site + '_pip_' + str(match_dates) + '.png')

        def process_mrr_data(site, ze_list, mrr_height_list, dv_list, sw_list, match_dates):
            ze_data = prepare_data(ze_list, mrr_height_list, [-30, np.inf])
            dv_data = prepare_data(dv_list, mrr_height_list, [-30, 30])
            sw_data = prepare_data(sw_list, mrr_height_list, [0, 1])

            plot_mrr_figures(site, ze_data, dv_data, sw_data, match_dates)

        def process_pip_data(site, dsd_list, dsd_height_list, vvd_list, vvd_height_list, rho_list, rho_height_list, total_snowing_minutes, match_dates):
            dsd_data = prepare_data(dsd_list, dsd_height_list, [0, np.inf])
            vvd_data = prepare_data(vvd_list, vvd_height_list, [0, np.inf])
            rho_data = prepare_data(rho_list, rho_height_list, [0, np.inf])

            plot_pip_figures(site, dsd_data, vvd_data, rho_data, total_snowing_minutes, match_dates)

        def plot_n0_lambda(site, lam, n0, lam_bins, n0_bins, match_dates):
            n0_lambda_hist = np.histogram2d(np.ma.log10(lam), np.ma.log10(n0), (lam_bins, n0_bins))
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            fig.suptitle(site + ' n$_0$ Lambda Summary')

            hist = 100 * n0_lambda_hist[0].T / np.sum(n0_lambda_hist[0].T)
            print(hist.min(), hist.max())
            pcm = axes[0].pcolormesh(lam_bins, n0_bins, hist, cmap="magma", norm=LogNorm(vmin=0.01, vmax=hist.max()))
            axes[0].set_facecolor('black')
            axes[0].set_xlim(-0.4, 0.5)
            axes[0].set_ylim(0, 5)
            axes[0].set_ylabel("$Log_{10}(N_{0})$")
            axes[0].set_xlabel("$Log_{10}(λ)$")

            cb = fig.colorbar(pcm, ax=axes[0], extend="max")
            cb.set_label(label="Counts (%)", size=14)

            axes[1].hist(lam, bins=lam_bins, density=True, histtype='step', alpha=1, color="red", linewidth=3.0)
            axes[1].set_xlim(0.1, 5)
            axes[1].set_xlabel("Lambda (λ) ($mm^{-1}$)", size=14)
            axes[1].set_ylabel("Normalized Counts", size=14)

            axes[2].hist(np.ma.log10(n0), bins=n0_bins, density=True, histtype='step', alpha=1, color="blue", linewidth=3.0)
            axes[2].set_xlabel("$Log_{10}(N_0)$", size=14)
            axes[2].set_ylabel("Normalized Counts", size=14)
            axes[2].set_xlim(1, 5)
            plt.tight_layout()
            plt.savefig('../../images/' + site + '_n0_lambda_' + str(match_dates) + '.png')

        # Call the process_data function with the appropriate data lists
        process_mrr_data(site, ze_list, mrr_height_list, dv_list, sw_list, match_dates)
        process_pip_data(site, dsd_list, dsd_height_list, vvd_list, vvd_height_list, rho_list, rho_height_list, total_snowing_minutes, match_dates)
        plot_n0_lambda(site, lambda_array, N_0_array, np.arange(-1, 1.05, 0.005), np.arange(0, 6.2, 0.1), match_dates)

    create_hists_for_site(site, match_dates)

sanity_check('NSA', '/data2/fking/s03/converted/', '/data/jshates/northslope/KAZR/a1/', True)
sanity_check('NSA', '/data2/fking/s03/converted/', '/data/jshates/northslope/KAZR/a1/', False)

# sanity_check('APX', '/data2/fking/s03/converted/', '/data/APX/MRR/NetCDF', True)
# sanity_check('APX', '/data2/fking/s03/converted/', '/data/APX/MRR/NetCDF', False)
# sanity_check('MQT', '/data/LakeEffect/PIP/Netcdf_Converted/', '/data/LakeEffect/MRR/NetCDF_DN/', True)
# sanity_check('MQT', '/data/LakeEffect/PIP/Netcdf_Converted/', '/data/LakeEffect/MRR/NetCDF_DN/', False)
# sanity_check('HAUK', '/data2/fking/s03/converted/', '/data/HiLaMS/HAUK/MRR/NetCDF/', True)
# sanity_check('HAUK', '/data2/fking/s03/converted/', '/data/HiLaMS/HAUK/MRR/NetCDF/', False)
# sanity_check('KIS', '/data2/fking/s03/converted/', '/data/HiLaMS/KIR/MRR/NetCDF/', True)
# sanity_check('KIS', '/data2/fking/s03/converted/', '/data/HiLaMS/KIR/MRR/NetCDF/', False)
# sanity_check('KO2', '/data2/fking/s03/converted/', '/data2/fking/s03/data/ICE_POP/MRR/KO2/', True)
# sanity_check('KO2', '/data2/fking/s03/converted/', '/data2/fking/s03/data/ICE_POP/MRR/KO2/', False)
# sanity_check('KO1', '/data2/fking/s03/converted/', '/data2/fking/s03/data/ICE_POP/MRR/KO1/', True)
# sanity_check('KO1', '/data2/fking/s03/converted/', '/data2/fking/s03/data/ICE_POP/MRR/KO1/', False)
