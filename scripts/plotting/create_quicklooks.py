import sys,os,glob
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

    def get_day_of_year(date_string):
        date = datetime.strptime(date_string, '%Y%m%d')
        day_of_year = date.timetuple().tm_yday
        return day_of_year

    def create_precip_plots(site):
        avg_snow = [[] for i in range(365)]
        avg_rain = [[] for i in range(365)]
        avg_ed = [[] for i in range(365)]
        for date in matched_dates:
            print("\nWorking on date", date)
            doy = get_day_of_year(date)
            year = date[:4]
            try:
                file_pattern = pip_path + str(year) + '_' + site + '/netCDF/edensity_lwe_rate/*' + date + '*_P_Minute.nc'
                matching_files = glob.glob(file_pattern)
                ds_lwe = xr.open_dataset(matching_files[0])   
                snow = ds_lwe['nrr'].values  
                rain = ds_lwe['rr'].values
                ed = ds_lwe['ed'].values
                avg_snow[doy-1].append(np.nanmean(snow))
                avg_rain[doy-1].append(np.nanmean(rain))
                avg_ed[doy-1].append(np.nanmean(ed))
                print("Done!")
            except FileNotFoundError:
                print(f"No file found at {pip_path + '/edensity_lwe_rate/*' + date + '*_P_Minute.nc'}")
            except Exception as e:
                print(f"An error occurred: {e}")
            
        std_snow = [np.nanstd(x) for x in avg_snow]
        std_rain = [np.nanstd(x) for x in avg_rain]
        std_ed = [np.nanstd(x) for x in avg_ed]
        avg_snow = [np.nanmean(x) for x in avg_snow]
        avg_rain = [np.nanmean(x) for x in avg_rain]
        avg_ed = [np.nanmean(x) for x in avg_ed]

        fig, axes = plt.subplots(figsize=(12,6))
        axes.set_title(site + " Monthly Average Precip")
        axes.plot(np.arange(365), avg_snow, color='red', linewidth=3, label='snow')
        axes.plot(np.arange(365), avg_rain, color='blue', linewidth=3, label='rain')
        axes.set_ylabel('Precipitation Rate (mm hr$^{-1}$)')
        plt.legend()
        ax2 = axes.twinx()
        ax2.plot(np.arange(365), avg_ed, color='black', linewidth=3)
        ax2.set_ylabel('Effective Density')
        ax2.set_xlabel('Month')
        plt.savefig('../../images/' + site + '_precip.png')
        print("Success!")

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

                        # Calculate 15-minute running average for this minute and all bins
                        running_avg = np.mean(dsd[i:i+15, :], axis=0)

                        # Remove nans from running_avg and corresponding bin_centers
                        valid_indices = ~np.isnan(running_avg)
                        running_avg = running_avg[valid_indices]
                        valid_bin_centers = bin_centers[valid_indices]

                        # If there are no valid data points left after removing NaNs, skip this minute
                        if running_avg.size == 0:
                            N_0_array.append(np.nan)
                            lambda_array.append(np.nan)
                            continue

                        # Perform curve fitting
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
        else:
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
            for date in pip_dates:
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

                        # Calculate 15-minute running average for this minute and all bins
                        running_avg = np.mean(dsd[i:i+15, :], axis=0)

                        # Remove nans from running_avg and corresponding bin_centers
                        valid_indices = ~np.isnan(running_avg)
                        running_avg = running_avg[valid_indices]
                        valid_bin_centers = bin_centers[valid_indices]

                        # If there are no valid data points left after removing NaNs, skip this minute
                        if running_avg.size == 0:
                            N_0_array.append(np.nan)
                            lambda_array.append(np.nan)
                            continue

                        # Perform curve fitting
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

        print("Ze stats", len(ze_list))
        print("DSD stats", len(dsd_list))

        ze_ds = np.concatenate(ze_list)
        dv_ds = np.concatenate(dv_list)
        sw_ds = np.concatenate(sw_list)
        mrr_height_ds = np.concatenate(mrr_height_list)

        dsd_ds = np.concatenate(dsd_list)
        dsd_height_ds = np.concatenate(dsd_height_list)
        vvd_ds = np.concatenate(vvd_list)
        vvd_height_ds = np.concatenate(vvd_height_list)
        rho_ds = np.concatenate(rho_list)
        rho_height_ds = np.concatenate(rho_height_list)

        ze_x = np.asarray(ze_ds).flatten()
        ze_y = np.asarray(mrr_height_ds).flatten()
        ze_x[ze_x<-30] = np.nan
        mask = ~np.isnan(ze_x)
        ze_x = ze_x[mask]
        ze_y = ze_y[mask]
        ze_hist, ze_xedges, ze_yedges = np.histogram2d(ze_y, ze_x, bins=[28, 128])

        dv_x = np.asarray(dv_ds).flatten()
        dv_y = np.asarray(mrr_height_ds).flatten()
        dv_x[dv_x<-30] = np.nan
        dv_x[dv_x>30] = np.nan
        mask = ~np.isnan(dv_x)
        dv_x = dv_x[mask]
        dv_y = dv_y[mask]
        dv_hist, dv_xedges, dv_yedges = np.histogram2d(dv_y, dv_x, bins=[28, 128])

        sw_x = np.asarray(sw_ds).flatten()
        sw_y = np.asarray(mrr_height_ds).flatten()
        sw_x[sw_x<0] = np.nan
        sw_x[sw_x>1] = np.nan
        mask = ~np.isnan(sw_x)
        sw_x = sw_x[mask]
        sw_y = sw_y[mask]
        sw_hist, sw_xedges, sw_yedges = np.histogram2d(sw_y, sw_x, bins=[28, 128])

        fig, axes = plt.subplots(1, 3, figsize=(16,6), sharey=True)
        fig.suptitle(site + ' MRR')
        axes[0].set_title("Reflectivity")
        axes[0].imshow(ze_hist, origin='lower', cmap='Reds', aspect='auto', extent=[ze_yedges[0], ze_yedges[-1], ze_xedges[0], ze_xedges[-1]])
        axes[0].invert_yaxis()
        axes[0].set_xlim((-20, 20))
        formatter = ticker.FuncFormatter(lambda y, pos: f'{y/10:.1f}')
        axes[0].yaxis.set_major_formatter(formatter)
        labels = [item.get_text() for item in axes[0].get_yticklabels()]
        axes[0].set_yticklabels(labels[::-1])
        axes[0].set_xlabel("dBZ")
        axes[0].set_ylabel("Height (km)")
        axes[1].set_title("Doppler Velocity")
        axes[1].imshow(dv_hist, origin='lower', cmap='Blues', aspect='auto', extent=[dv_yedges[0], dv_yedges[-1], dv_xedges[0], dv_xedges[-1]])
        axes[1].invert_yaxis()
        axes[1].set_xlabel("m s$^{-1}$")
        axes[1].set_xlim((-10, 10))
        axes[2].set_title("Spectral Width")
        axes[2].imshow(sw_hist, origin='lower', cmap='Oranges', aspect='auto', extent=[sw_yedges[0], sw_yedges[-1], sw_xedges[0], sw_xedges[-1]])
        axes[2].invert_yaxis()
        axes[2].set_xlabel("m s$^{-1}$")
        axes[2].set_xlim((0, 0.5))
        plt.tight_layout()
        plt.savefig('../../images/' + site + '_mrr.png')

        ########### N0 Lambda Stuff
        bin_N0 = np.arange(0, 6.2, 0.2)
        bin_lambda = np.arange(-1, 1.05, 0.05)
        AR_N0_lambda_hist = np.histogram2d(np.ma.log10(lambda_array), np.ma.log10(N_0_array), (bin_lambda,bin_N0))
        plt.figure(dpi=150)
        plt.pcolormesh(bin_lambda, bin_N0, np.ma.masked_less(AR_N0_lambda_hist[0].T, 10), vmin=0, cmap="viridis")
        plt.xlim(-0.4,1.0)
        plt.ylim(0,6)
        plt.title("PIP AR Snowfall", size=16)
        plt.ylabel("$Log_{10}(N_{0})$", size=14)
        plt.xlabel("$Log_{10}(λ)$", size=14)
        cb = plt.colorbar(label = 'counts', extend="max")
        cb.set_label(label="Counts", size=14)
        cb.ax.tick_params(labelsize=14) 
        plt.grid()
        plt.savefig('../../images/' + site + '_n0_lambda.png')

        plt.figure(dpi=150)
        bin_lambda = np.arange(0, 10, 0.2)
        plt.hist(lambda_array, bins=bin_lambda, density=True, histtype='step', alpha=0.7, color="red", linewidth=3.0, label="AR Snowfall")
        plt.title("PIP Lambda (λ) Histograms", size=20)
        plt.xlim(0.3, 8)
        plt.xlabel("Lambda (λ) [$mm^{-1}$]", size=14)
        plt.ylabel("Normalized Counts", size=14)
        plt.grid()
        plt.legend()
        plt.savefig('../../images/' + site + '_lambda.png')

        plt.figure(dpi=150)
        bin_N0 = np.arange(0.0, 6, 0.2)
        plt.hist(np.ma.log10(N_0_array), bins=bin_N0, density=True, histtype='step', alpha=0.7, color="red", linewidth=3.0, label="AR Snowfall")
        plt.title("PIP $N_0$ Histograms", size=20)
        plt.xlabel("$Log_{10}(N_0)$", size=14)
        plt.ylabel("Normalized Counts", size=14)
        plt.xlim(1, 6)
        plt.grid()
        plt.legend()
        plt.savefig('../../images/' + site + '_n0.png')


        bin_DSD = np.linspace(.001,5,54)
        bin_VVD = np.arange(0.1,5.1,0.1)
        bin_eden = np.arange(0.01,1.01,0.01)    
        bin_D = np.arange(0,26,1)
        
        dsd_x = np.asarray(dsd_ds).flatten()
        dsd_y = np.asarray(dsd_height_ds).flatten()
        dsd_x[dsd_x<=0] = np.nan
        mask = ~np.isnan(dsd_x)
        dsd_x = dsd_x[mask]
        dsd_y = dsd_y[mask]
        dsd_hist, dsd_xedges, dsd_yedges = np.histogram2d(dsd_y, np.ma.log10(dsd_x), (bin_D, bin_DSD))

        vvd_x = np.asarray(vvd_ds).flatten()
        vvd_y = np.asarray(vvd_height_ds).flatten()
        vvd_x[vvd_x<=0] = np.nan
        mask = ~np.isnan(vvd_x)
        vvd_x = vvd_x[mask]
        vvd_y = vvd_y[mask]
        vvd_hist, vvd_xedges, vvd_yedges = np.histogram2d(vvd_y, vvd_x, (bin_D, bin_VVD))
        
        rho_x = np.asarray(rho_ds).flatten()
        rho_y = np.asarray(rho_height_ds).flatten()
        rho_x[rho_x<=0] = np.nan
        mask = ~np.isnan(rho_x)
        rho_x = rho_x[mask]
        rho_y = rho_y[mask]
        rho_hist, rho_xedges, rho_yedges = np.histogram2d(rho_y, rho_x, (bin_D, bin_eden))

        fig, axes = plt.subplots(1, 3, figsize=(16,6), sharey=False)
        fig.suptitle(site + ' PIP')
        axes[0].set_title("Particle Size Distribution")
        axes[0].imshow(dsd_hist.T, origin='lower', cmap='plasma', aspect='auto', extent=[dsd_xedges[0], dsd_xedges[-1], dsd_yedges[0], dsd_yedges[-1]])
        axes[0].set_xlabel("Mean De (mm)")
        bin_centers = ds_pip.bin_centers.values
        ticks_idx = np.linspace(0, 49, 6, dtype=int)
        axes[1].set_title("Velocity Distribution")
        axes[1].imshow(vvd_hist.T, origin='lower', cmap='plasma', aspect='auto', extent=[vvd_xedges[0], vvd_xedges[-1], vvd_yedges[0], vvd_yedges[-1]])
        axes[1].set_ylabel("m s$^{−1}$")
        axes[1].set_xlabel("Mean De (mm)")
        axes[1].set_yscale('linear')
        axes[2].set_title("eDensity Distribution")
        axes[2].imshow(rho_hist.T, origin='lower', cmap='plasma', aspect='auto', extent=[rho_xedges[0], rho_xedges[-1], rho_yedges[0], rho_yedges[-1]])
        axes[2].set_xlabel("g cm$^{-3}$")
        axes[2].set_xlabel("Mean De (mm)")
        axes[2].set_yscale('linear')
        plt.tight_layout()
        plt.savefig('../../images/' + site + '_pip.png')

    create_hists_for_site(site, match_dates)
    create_precip_plots(site, match_dates)

# sanity_check('APX', '/data2/fking/s03/converted/', '/data/APX/MRR/NetCDF')
# sanity_check('MQT', '/data/LakeEffect/PIP/Netcdf_Converted/', '/data/LakeEffect/MRR/NetCDF_DN/')
# sanity_check('HAUK', '/data2/fking/s03/converted/', '/data/HiLaMS/HAUK/MRR/NetCDF/')
# sanity_check('KIS', '/data2/fking/s03/converted/', '/data/HiLaMS/KIR/MRR/NetCDF/')
sanity_check('KO2', '/data2/fking/s03/converted/', '/data2/fking/s03/data/ICE_POP/MRR/KO2/', False)
