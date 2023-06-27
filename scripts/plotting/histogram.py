"""
histogram.py --> collection of functions to assist analysis of PIP/MRR data
Jack Richter

Last updated: 05/08/2023 (added detailed comments, file header)
"""

import netCDF4 as nc
import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import matplotlib.cm as cm
import sys
import glob
sys.path.insert(1, '/home/jrichter/python/mqt/py_files') 
from pip_tools_original_JackCopy import *

# -------------------------------------------------------------------------------------------------------------------------------
"""
    This function takes an input string and converts it to its float equivalent.
"""
# from https://stackoverflow.com/questions/575925/how-to-convert-rational-and-decimal-number-strings-to-floats-in-python
def convert(s):
    try:
        return float(s)
    except ValueError:
        num, denom = s.split('/')
        return float(num) / float(denom)
    
# -------------------------------------------------------------------------------------------------------------------------------
"""
    This function takes a filename as input (specific format needed) and creates the composite 2-d PSD histogram of the data.
    
    Input: filename --> path to file that contains list of snowfall events coinciding with PIP PSD measurements.
    Return: datd[0], norm_hist_d --> 2-d and normalized 2-d histogram of the composited PIP PSD measurements. 
"""
def make_PSD_histogram(filename):
    
    file_events = open(filename, "r")

    counter = 0
    for event in file_events: # going through the file, event by event
        args = event.strip().split(",")
        length_range = int(int(args[1]) - int(args[0])) + 1 # amount of days the current event took place over
        # args[2] and args[3] correspond to "cuts". I.e., if the event started at 12 UTC, cut the first 12 hours.
        if (args[2].strip() != "None"):
            cut_1 = convert(args[2])
        else:
            cut_1 = None
        if (args[3].strip() != "None"):
            cut_2 = convert(args[3])
        else:
            cut_2 = None
        # data retrieval and formatting PIP
        PIP_datadir = '/data/LakeEffect/PIP/' + str(args[0])[:4] + '_MQT/PIP_3/f_1_4_DSD_Tables_ascii/'
        PIP_dict = {}
        if (length_range == 2):
            for i in range(length_range):
                PIP_dict["PIP_filename_{}".format(i)] = '006' + str(int(args[0]) + int(i))
                PIP_dict["PIP_fullfiledir_{}".format(i)] = glob.glob(PIP_datadir + PIP_dict["PIP_filename_{}".format(i)] + '*')
                if (len(PIP_dict["PIP_fullfiledir_{}".format(i)]) == 0):
                    print("No File:", str(int(args[0]) + int(i)))
                    continue
                else:
                    PIP_dict["PIP_fullfiledir_{}".format(i)] = PIP_dict["PIP_fullfiledir_{}".format(i)][0]
                if (str(args[0] + str(i))[4] != '0' and str(args[0] + str(i))[6] != '0'): 
                    [PIP_dict["DSD_avg_{}".format(i)], PIP_dict["dsdperminute_{}".format(i)], PIP_dict["bin_cen_{}".format(i)], PIP_dict["bin_edge_{}".format(i)], PIP_dict["timevar_PIP_{}".format(i)], PIP_dict["instrument_time_{}".format(i)]] = open_dist_data(PIP_dict["PIP_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[4:6], str(int(args[0]) + i)[6:], 'mqt')
                elif (str(args[0] + str(i))[4] == '0' and str(args[0] + str(i))[6] != '0'): 
                    [PIP_dict["DSD_avg_{}".format(i)], PIP_dict["dsdperminute_{}".format(i)], PIP_dict["bin_cen_{}".format(i)], PIP_dict["bin_edge_{}".format(i)], PIP_dict["timevar_PIP_{}".format(i)], PIP_dict["instrument_time_{}".format(i)]] = open_dist_data(PIP_dict["PIP_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[5:6], str(int(args[0]) + i)[6:], 'mqt')
                elif (str(args[0] + str(i))[4] != '0' and str(args[0] + str(i))[6] == '0'): 
                    [PIP_dict["DSD_avg_{}".format(i)], PIP_dict["dsdperminute_{}".format(i)], PIP_dict["bin_cen_{}".format(i)], PIP_dict["bin_edge_{}".format(i)], PIP_dict["timevar_PIP_{}".format(i)], PIP_dict["instrument_time_{}".format(i)]] = open_dist_data(PIP_dict["PIP_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[4:6], str(int(args[0]) + i)[6:], 'mqt')
                elif (str(args[0] + str(i))[4] == '0' and str(args[0] + str(i))[6] == '0'): 
                    [PIP_dict["DSD_avg_{}".format(i)], PIP_dict["dsdperminute_{}".format(i)], PIP_dict["bin_cen_{}".format(i)], PIP_dict["bin_edge_{}".format(i)], PIP_dict["timevar_PIP_{}".format(i)], PIP_dict["instrument_time_{}".format(i)]] = open_dist_data(PIP_dict["PIP_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[5:6], str(int(args[0]) + i)[6:], 'mqt')
                PIP_dict["bins_{}".format(i)] = np.array(PIP_dict["bin_edge_{}".format(i)])
                PIP_dict["dsdperminute_{}".format(i)] = np.ma.masked_less(PIP_dict["dsdperminute_{}".format(i)], 0)
            try:
                dsdperminute = np.ma.concatenate((PIP_dict["dsdperminute_{}".format(0)], PIP_dict["dsdperminute_{}".format(1)]))
            except:
                print("Concatenation problem:", str(int(args[0]) + int(i)))
                continue
        else:
            PIP_dict["PIP_filename_{}".format(0)] = '006' + str(int(args[0]))
            PIP_dict["PIP_fullfiledir_{}".format(0)] = glob.glob(PIP_datadir + PIP_dict["PIP_filename_{}".format(0)] + '*')
            if (len(PIP_dict["PIP_fullfiledir_{}".format(0)]) == 0):
                print("No File", str(int(args[0])))
                continue
            else:
                PIP_dict["PIP_fullfiledir_{}".format(0)] = PIP_dict["PIP_fullfiledir_{}".format(0)][0]
            if (str(args[0])[4] != '0' and str(args[0])[6] != '0'): 
                try:
                    [PIP_dict["DSD_avg_{}".format(0)], PIP_dict["dsdperminute_{}".format(0)], PIP_dict["bin_cen_{}".format(0)], PIP_dict["bin_edge_{}".format(0)], PIP_dict["timevar_PIP_{}".format(0)], PIP_dict["instrument_time_{}".format(0)]] = open_dist_data(PIP_dict["PIP_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[4:6], str(int(args[0]))[6:], 'mqt')
                except PermissionError:
                    print("Permission Error", str(int(args[0])))
                    continue
            elif (str(args[0])[4] == '0' and str(args[0])[6] != '0'): 
                [PIP_dict["DSD_avg_{}".format(0)], PIP_dict["dsdperminute_{}".format(0)], PIP_dict["bin_cen_{}".format(0)], PIP_dict["bin_edge_{}".format(0)], PIP_dict["timevar_PIP_{}".format(0)], PIP_dict["instrument_time_{}".format(0)]] = open_dist_data(PIP_dict["PIP_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[5:6], str(int(args[0]))[6:], 'mqt')
            elif (str(args[0])[4] != '0' and str(args[0])[6] == '0'): 
                [PIP_dict["DSD_avg_{}".format(0)], PIP_dict["dsdperminute_{}".format(0)], PIP_dict["bin_cen_{}".format(0)], PIP_dict["bin_edge_{}".format(0)], PIP_dict["timevar_PIP_{}".format(0)], PIP_dict["instrument_time_{}".format(0)]] = open_dist_data(PIP_dict["PIP_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[4:6], str(int(args[0]))[7:], 'mqt')
            elif (str(args[0])[4] == '0' and str(args[0])[6] == '0'): 
                [PIP_dict["DSD_avg_{}".format(0)], PIP_dict["dsdperminute_{}".format(0)], PIP_dict["bin_cen_{}".format(0)], PIP_dict["bin_edge_{}".format(0)], PIP_dict["timevar_PIP_{}".format(0)], PIP_dict["instrument_time_{}".format(0)]] = open_dist_data(PIP_dict["PIP_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[5:6], str(int(args[0]))[6:], 'mqt')
            PIP_dict["bins_{}".format(0)] = np.array(PIP_dict["bin_edge_{}".format(0)])
            PIP_dict["dsdperminute_{}".format(0)] = np.ma.masked_less(PIP_dict["dsdperminute_{}".format(0)], 0)
            dsdperminute = PIP_dict["dsdperminute_{}".format(0)]
    
        if (cut_2 != None):
            dsdperminute = dsdperminute[:int((1440*length_range)-(1440*cut_2))]
    
        if (cut_1 != None):
            dsdperminute = dsdperminute[int(1440*cut_1):]
    
        if (counter == 0):
            total_dsdperminute = dsdperminute
            bin_cen = PIP_dict["bin_cen_0"]
            #print(np.shape(total_dsdperminute))
        else:
            total_dsdperminute = np.ma.concatenate([total_dsdperminute, dsdperminute])
            #print(np.shape(total_dsdperminute))
    
        counter += 1
        
        continue
    
    file_events.close()
    
    bin_DSD = np.linspace(.001,5,54) 
    bin_D = np.arange(0.4,26.2,0.2)
    bin_edge_4bins = np.ones((np.shape(total_dsdperminute)))*bin_cen
    datd = np.histogram2d(np.ma.log10(total_dsdperminute).flatten(), bin_edge_4bins.flatten(), (bin_DSD,bin_D),normed=False) 
    norm_hist_d = datd[0]/float(datd[0].sum())
    
    return datd[0], norm_hist_d

# -------------------------------------------------------------------------------------------------------------------------------
"""
    This function takes a 2-d histogram as input (and other preferences) and plots it.
    
    Input: hist --> 2-d histogram to be plotted
        other inputs --> refer to the matplotlib documentation of pcolormesh
    Return: None --> matplotlib will display the finished plot
"""
def plot_2D_hist(hist, bin_D, bin_val, title, ylabel, xlabel, xlim, ylim, cmap, filename):
    plt.figure(figsize=(10,7), dpi=200)
    plt.pcolormesh(bin_D, bin_val, hist.T, cmap=cmap)
    plt.title(title, size=20)
    plt.ylabel(ylabel, size=20)
    plt.xlabel(xlabel, size=20)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    cb = plt.colorbar(label = 'counts', extend="max")
    cb.set_label(label="Counts", size=20)
    cb.ax.tick_params(labelsize=16) 
    plt.grid()
    # saving the plot is disabled for now, uncomment the following lines to save plots again
    #plt.savefig("/home/jrichter/python/mqt/" + filename, bbox_inches='tight', pad_inches=0.1)
    #plt.savefig("/data/jrichter/mqt/Histograms/" + filename)
    plt.show()
    return None

# -------------------------------------------------------------------------------------------------------------------------------
"""
    This function takes a 2-d normalized histogram as input (and other preferences) and plots it.
    
    Input: hist --> 2-d normalized histogram to be plotted
        other inputs --> refer to the matplotlib documentation of pcolormesh
    Return: None --> matplotlib will display the finished plot
"""
def plot_2D_norm(norm, bin_D, bin_val, title, ylabel, xlabel, xlim, ylim, vmin, vmax, filename):
    plt.figure(figsize=(10,7), dpi=200)
    plt.pcolormesh(bin_D, bin_val, norm.T*100, cmap="seismic", vmin=vmin, vmax=vmax)
    plt.title(title, size=20)
    plt.ylabel(ylabel, size=20)
    plt.xlabel(xlabel, size=20)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    cb = plt.colorbar(label = 'counts', extend='both')
    cb.set_label(label="Normalized Counts (%)", size=20)
    cb.ax.tick_params(labelsize=16) 
    plt.grid()
    # saving the plot is disabled for now, uncomment the following lines to save plots again
    #plt.savefig("/home/jrichter/python/mqt/" + filename, bbox_inches='tight', pad_inches=0.1)
    #plt.savefig("/data/jrichter/mqt/Histograms/" + filename)
    plt.show()
    return None

# -------------------------------------------------------------------------------------------------------------------------------
"""
    This function takes a filename as input (specific format needed) and creates the composite 2-d MRR histograms of the data.
    
    Input: filename --> path to file that contains list of snowfall events coinciding with MRR measurements.
    Return: ze_hist[0], ze_hist_norm, w_hist[0], w_hist_norm, sw_hist[0], sw_hist_norm --> 2-d and norm 2-d composite histograms
"""
def make_MRR_histograms(filename):
    
    print("Starting function...")
    file_events = open(filename, "r")
    datadir = '/data/LakeEffect/MRR/NetCDF_DN/'

    counter = 0
    for event in file_events:
        args = event.strip().split(",")
        length_range = int(int(args[1]) - int(args[0])) + 1
        if (args[2].strip() != "None"):
            cut_1 = convert(args[2])
        else:
            cut_1 = None
        if (args[3].strip() != "None"):
            cut_2 = convert(args[3])
        else:
            cut_2 = None
        
        MRR_dict = {}
        if (length_range == 2):
            for i in range(length_range):
                MRR_dict["MRR_filename_{}".format(i)] = 'MRR_NWS_MQT_' + str(int(args[0]) + i) + '_snow.nc'
                MRR_dict["f_MRR_{}".format(i)] = nc.Dataset(MRR_datadir + MRR_dict["MRR_filename_{}".format(i)], 'r')
                MRR_dict["ze_{}".format(i)] = MRR_dict["f_MRR_{}".format(i)]['Ze'][:]
                MRR_dict["W_{}".format(i)] = MRR_dict["f_MRR_{}".format(i)]['W'][:]
                MRR_dict["SW_{}".format(i)] = MRR_dict["f_MRR_{}".format(i)]['spectralWidth'][:]
                heightvar = MRR_dict["f_MRR_{}".format(i)]['height'][0]
                MRR_dict["timevar_{}".format(i)] = nc.num2date(MRR_dict["f_MRR_{}".format(i)]['time'][:], MRR_dict["f_MRR_{}".format(i)]['time'].units)
                MRR_dict["yearmonthday_{}".format(i)] = MRR_dict["timevar_{}".format(i)][0].strftime("%Y%m%d")
            total_reflectivity = np.ma.concatenate((MRR_dict["ze_{}".format(0)], MRR_dict["ze_{}".format(1)]))
            total_W = np.ma.concatenate((MRR_dict["W_{}".format(0)], MRR_dict["W_{}".format(1)]))
            total_SW = np.ma.concatenate((MRR_dict["SW_{}".format(0)], MRR_dict["SW_{}".format(1)]))
            total_timevar = np.ma.concatenate((MRR_dict["timevar_{}".format(0)], MRR_dict["timevar_{}".format(1)]))
            if (cut_2 != None):
                ze = total_reflectivity[:int((1440*length_range)-(1440*cut_2))]
                W = total_W[:int((1440*length_range)-(1440*cut_2))]
                SW = total_SW[:int((1440*length_range)-(1440*cut_2))]
                timevar = total_timevar[:int((1440*length_range)-(1440*cut_2))]
            if (cut_1 != None):
                ze = total_reflectivity[int(1440*cut_1):]
                W = total_W[int(1440*cut_1):]
                SW = total_SW[int(1440*cut_1):]
                timevar = total_timevar[int(1440*cut_1):]
        else:
            MRR_datadir = '/data/LakeEffect/MRR/NetCDF_DN/'
            MRR_filename = 'MRR_NWS_MQT_' + str(args[0]) + '_snow.nc'
            f_MRR = nc.Dataset(MRR_datadir + MRR_filename, 'r')
            ze = f_MRR['Ze'][:]
            W = f_MRR["W"][:]
            SW = f_MRR["spectralWidth"][:]
            heightvar = f_MRR['height'][0]
            timevar = nc.num2date(f_MRR['time'][:], f_MRR['time'].units)
            yearmonthday = timevar[0].strftime("%Y%m%d")
            if (cut_2 != None):
                ze = ze[:int((1440)-(1440*cut_2))]
                W = W[:int((1440)-(1440*cut_2))]
                SW = SW[:int((1440)-(1440*cut_2))]
                timevar = timevar[:int((1440)-(1440*cut_2))]
            if (cut_1 != None):
                ze = ze[int(1440*cut_1):]
                W = W[int(1440*cut_1):]
                SW = SW[int(1440*cut_1):]
                timevar = timevar[int(1440*cut_1):]
        
        if (counter == 0):
            total_ze = ze
            total_W = W
            total_SW = SW
            #print(len(total_ze), len(total_W), len(total_SW))
        else:
            total_ze = np.ma.concatenate([total_ze, ze])
            total_W = np.ma.concatenate([total_W, W])
            total_SW = np.ma.concatenate([total_SW, SW])
            #print(len(total_ze), len(total_W), len(total_SW))
    
        counter += 1
    
        continue
    
    file_events.close()
    
    print(len(total_ze), len(total_W), len(total_SW))
    
    # 2D histogram code
    h=np.ones((len(total_ze),31))*heightvar[:]/1000. 
    h_bins = np.linspace(0.050, 3.150, 32)
    z_bins=np.linspace(-10,30,41)
    w = np.ones((len(total_W),31))*heightvar[:]/1000.
    w_bins=np.linspace(-3,3,61)
    sw=np.ones((len(total_SW),31))*heightvar[:]/1000
    sw_bins=np.linspace(0,1.5,61)
    ze_hist = np.histogram2d(total_ze.flatten(), h.flatten(), (z_bins, h_bins),normed=False) 
    ze_hist_norm = ze_hist[0]/float(ze_hist[0].sum())
    w_hist = np.histogram2d(total_W.flatten(), w.flatten(), (w_bins, h_bins),normed=False) 
    w_hist_norm = w_hist[0]/float(w_hist[0].sum())
    sw_hist = np.histogram2d(total_SW.flatten(), sw.flatten(), (sw_bins, h_bins),normed=False)
    sw_hist_norm = sw_hist[0]/float(sw_hist[0].sum())
    
    return ze_hist[0], ze_hist_norm, w_hist[0], w_hist_norm, sw_hist[0], sw_hist_norm

# -------------------------------------------------------------------------------------------------------------------------------
"""
    This function takes a filename as input (specific format needed) and creates the composite 2-d VVD histogram of the data.
    
    Input: filename --> path to file that contains list of snowfall events coinciding with VVD measurements.
    Return: datd[0], norm_hist_d --> 2-d and norm 2-d composite histograms of the VVDs
"""
def make_vvd_histogram(filename):
    
    file_events = open(filename, "r")

    counter = 0
    for event in file_events:
        args = event.strip().split(",")
        if int((args[0])[:4]) == 2014: # weird unicode error for 2014 files ??? Debug later
            continue
        length_range = int(int(args[1]) - int(args[0])) + 1
        if (args[2].strip() != "None"):
            cut_1 = convert(args[2])
        else:
            cut_1 = None
        if (args[3].strip() != "None"):
            cut_2 = convert(args[3])
        else:
            cut_2 = None
        # data retrieval and formatting PIP
        VVD_datadir = '/data/LakeEffect/PIP/' + str(args[0])[:4] + '_MQT/PIP_3/f_2_4_VVD_Tables/'
        VVD_dict = {}
        if (length_range == 2):
            for i in range(length_range):
                VVD_dict["VVD_filename_{}".format(i)] = '006' + str(int(args[0]) + int(i))
                VVD_dict["VVD_fullfiledir_{}".format(i)] = glob.glob(VVD_datadir + VVD_dict["VVD_filename_{}".format(i)] + '*A*')
                if (len(VVD_dict["VVD_fullfiledir_{}".format(i)]) == 0):
                    print("No File:", str(int(args[0]) + int(i)))
                    continue
                else:
                    VVD_dict["VVD_fullfiledir_{}".format(i)] = VVD_dict["VVD_fullfiledir_{}".format(i)][0]
                if (str(args[0] + str(i))[4] != '0' and str(args[0] + str(i))[6] != '0'): 
                    [VVD_dict["VVD_avg_{}".format(i)], VVD_dict["vvdperminute_{}".format(i)], VVD_dict["bin_cen_{}".format(i)], VVD_dict["bin_edge_{}".format(i)], VVD_dict["timevar_PIP_{}".format(i)], VVD_dict["instrument_time_{}".format(i)]] = open_dist_data(VVD_dict["VVD_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[4:6], str(int(args[0]) + i)[6:], 'mqt')
                elif (str(args[0] + str(i))[4] == '0' and str(args[0] + str(i))[6] != '0'): 
                    [VVD_dict["VVD_avg_{}".format(i)], VVD_dict["vvdperminute_{}".format(i)], VVD_dict["bin_cen_{}".format(i)], VVD_dict["bin_edge_{}".format(i)], VVD_dict["timevar_PIP_{}".format(i)], VVD_dict["instrument_time_{}".format(i)]] = open_dist_data(VVD_dict["VVD_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[5:6], str(int(args[0]) + i)[6:], 'mqt')
                elif (str(args[0] + str(i))[4] != '0' and str(args[0] + str(i))[6] == '0'): 
                    [VVD_dict["VVD_avg_{}".format(i)], VVD_dict["vvdperminute_{}".format(i)], VVD_dict["bin_cen_{}".format(i)], VVD_dict["bin_edge_{}".format(i)], VVD_dict["timevar_PIP_{}".format(i)], VVD_dict["instrument_time_{}".format(i)]] = open_dist_data(VVD_dict["VVD_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[4:6], str(int(args[0]) + i)[6:], 'mqt')        
                elif (str(args[0] + str(i))[4] == '0' and str(args[0] + str(i))[6] == '0'): 
                    [VVD_dict["VVD_avg_{}".format(i)], VVD_dict["vvdperminute_{}".format(i)], VVD_dict["bin_cen_{}".format(i)], VVD_dict["bin_edge_{}".format(i)], VVD_dict["timevar_PIP_{}".format(i)], VVD_dict["instrument_time_{}".format(i)]] = open_dist_data(VVD_dict["VVD_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[5:6], str(int(args[0]) + i)[6:], 'mqt')      
                VVD_dict["bins_{}".format(i)] = np.array(VVD_dict["bin_edge_{}".format(i)])
                VVD_dict["vvdperminute_{}".format(i)] = np.ma.masked_less(VVD_dict["vvdperminute_{}".format(i)], 0)
            try:
                vvdperminute = np.ma.concatenate((VVD_dict["vvdperminute_{}".format(0)], VVD_dict["vvdperminute_{}".format(1)]))
            except:
                print("Concatenation problem:", str(int(args[0]) + int(i)))                
                continue
        else:
            VVD_dict["VVD_filename_{}".format(0)] = '006' + str(int(args[0]))
            VVD_dict["VVD_fullfiledir_{}".format(0)] = glob.glob(VVD_datadir + VVD_dict["VVD_filename_{}".format(0)] + '*A*')
            if (len(VVD_dict["VVD_fullfiledir_{}".format(0)]) == 0):
                print("No File:", str(int(args[0])))
                continue
            else:
                VVD_dict["VVD_fullfiledir_{}".format(0)] = VVD_dict["VVD_fullfiledir_{}".format(0)][0]
            if (str(args[0])[4] != '0' and str(args[0])[6] != '0'): 
                [VVD_dict["VVD_avg_{}".format(0)], VVD_dict["vvdperminute_{}".format(0)], VVD_dict["bin_cen_{}".format(0)], VVD_dict["bin_edge_{}".format(0)], VVD_dict["timevar_PIP_{}".format(0)], VVD_dict["instrument_time_{}".format(0)]] = open_dist_data(VVD_dict["VVD_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[4:6], str(int(args[0]))[6:], 'mqt')
            elif (str(args[0])[4] == '0' and str(args[0])[6] != '0'): 
                try:
                    [VVD_dict["VVD_avg_{}".format(0)], VVD_dict["vvdperminute_{}".format(0)], VVD_dict["bin_cen_{}".format(0)], VVD_dict["bin_edge_{}".format(0)], VVD_dict["timevar_PIP_{}".format(0)], VVD_dict["instrument_time_{}".format(0)]] = open_dist_data(VVD_dict["VVD_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[5:6], str(int(args[0]))[6:], 'mqt')
                except UnicodeDecodeError:
                    print("UnicodeDecodeError:", str(int(args[0])))
                    continue
            elif (str(args[0])[4] != '0' and str(args[0])[6] == '0'): 
                [VVD_dict["VVD_avg_{}".format(0)], VVD_dict["vvdperminute_{}".format(0)], VVD_dict["bin_cen_{}".format(0)], VVD_dict["bin_edge_{}".format(0)], VVD_dict["timevar_PIP_{}".format(0)], VVD_dict["instrument_time_{}".format(0)]] = open_dist_data(VVD_dict["VVD_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[4:6], str(int(args[0]))[6:], 'mqt')        
            elif (str(args[0])[4] == '0' and str(args[0])[6] == '0'): 
                [VVD_dict["VVD_avg_{}".format(0)], VVD_dict["vvdperminute_{}".format(0)], VVD_dict["bin_cen_{}".format(0)], VVD_dict["bin_edge_{}".format(0)], VVD_dict["timevar_PIP_{}".format(0)], VVD_dict["instrument_time_{}".format(0)]] = open_dist_data(VVD_dict["VVD_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[5:6], str(int(args[0]))[6:], 'mqt')       
            VVD_dict["bins_{}".format(0)] = np.array(VVD_dict["bin_edge_{}".format(0)])
            VVD_dict["vvdperminute_{}".format(0)] = np.ma.masked_less(VVD_dict["vvdperminute_{}".format(0)], 0)
            vvdperminute = VVD_dict["vvdperminute_{}".format(0)]
    
        if (cut_2 != None):
            vvdperminute = vvdperminute[:int((1440*length_range)-(1440*cut_2))]
    
        if (cut_1 != None):
            vvdperminute = vvdperminute[int(1440*cut_1):]
    
        if (counter == 0):
            total_vvdperminute = vvdperminute
            bin_cen = VVD_dict["bin_cen_0"]
            #print(np.shape(total_vvdperminute))            
        else:
            total_vvdperminute = np.ma.concatenate([total_vvdperminute, vvdperminute])
            #print(np.shape(total_vvdperminute))
    
        counter += 1
    
        continue
    
    file_events.close()
    
    bin_VVD = np.arange(0.1,3.1,0.1) 
    bin_D = np.arange(0.4,26.2,0.2)
    bin_edge_4bins = np.ones((np.shape(total_vvdperminute)))*bin_cen
    datd = np.histogram2d(total_vvdperminute.flatten(), bin_edge_4bins.flatten(), (bin_VVD,bin_D),normed=False) 
    norm_hist_d = datd[0]/float(datd[0].sum())
    
    return datd[0], norm_hist_d

# -------------------------------------------------------------------------------------------------------------------------------
"""
    This function takes a filename as input (specific format needed) and creates the composite 2-d eden histogram of the data.
    
    Input: filename --> path to file that contains list of snowfall events coinciding with eden measurements.
    Return: datd[0], norm_hist_d --> 2-d and norm 2-d composite histograms of the eden
"""
def make_eden_histogram(filename):
    
    file_events = open(filename, "r")

    counter = 0
    for event in file_events:
        args = event.strip().split(",")
        length_range = int(int(args[1]) - int(args[0])) + 1
        if (args[2].strip() != "None"):
            cut_1 = convert(args[2])
        else:
            cut_1 = None
        if (args[3].strip() != "None"):
            cut_2 = convert(args[3])
        else:
            cut_2 = None
        # data retrieval and formatting PIP
        eden_datadir = '/data/LakeEffect/PIP/' + str(args[0])[:4] + '_MQT/Study/f_2_6_rho_Plots_D_minute_dat/'
        eden_dict = {}
        if (length_range == 2):
            for i in range(length_range):
                eden_dict["eden_filename_{}".format(i)] = '006' + str(int(args[0]) + int(i))
                eden_dict["eden_fullfiledir_{}".format(i)] = glob.glob(eden_datadir + eden_dict["eden_filename_{}".format(i)] + '*')
                if (len(eden_dict["eden_fullfiledir_{}".format(i)]) == 0):
                    print("No file:", str(int(args[0]) + int(i)))
                    continue
                else:
                    eden_dict["eden_fullfiledir_{}".format(i)] = eden_dict["eden_fullfiledir_{}".format(i)][0]
                if (str(args[0] + str(i))[4] != '0' and str(args[0] + str(i))[6] != '0'): 
                    [eden_dict["eden_avg_{}".format(i)], eden_dict["edenperminute_{}".format(i)], eden_dict["bin_cen_{}".format(i)], eden_dict["bin_edge_{}".format(i)], eden_dict["timevar_PIP_{}".format(i)], eden_dict["instrument_time_{}".format(i)]] = open_eden_data(eden_dict["eden_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[4:6], str(int(args[0]) + i)[6:], 'mqt')        
                elif (str(args[0] + str(i))[4] == '0' and str(args[0] + str(i))[6] != '0'): 
                    [eden_dict["eden_avg_{}".format(i)], eden_dict["edenperminute_{}".format(i)], eden_dict["bin_cen_{}".format(i)], eden_dict["bin_edge_{}".format(i)], eden_dict["timevar_PIP_{}".format(i)], eden_dict["instrument_time_{}".format(i)]] = open_eden_data(eden_dict["eden_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[5:6], str(int(args[0]) + i)[6:], 'mqt')        
                elif (str(args[0] + str(i))[4] != '0' and str(args[0] + str(i))[6] == '0'): 
                    [eden_dict["eden_avg_{}".format(i)], eden_dict["edenperminute_{}".format(i)], eden_dict["bin_cen_{}".format(i)], eden_dict["bin_edge_{}".format(i)], eden_dict["timevar_PIP_{}".format(i)], eden_dict["instrument_time_{}".format(i)]] = open_eden_data(eden_dict["eden_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[4:6], str(int(args[0]) + i)[6:], 'mqt')        
                elif (str(args[0] + str(i))[4] == '0' and str(args[0] + str(i))[6] == '0'): 
                    [eden_dict["eden_avg_{}".format(i)], eden_dict["edenperminute_{}".format(i)], eden_dict["bin_cen_{}".format(i)], eden_dict["bin_edge_{}".format(i)], eden_dict["timevar_PIP_{}".format(i)], eden_dict["instrument_time_{}".format(i)]] = open_eden_data(eden_dict["eden_fullfiledir_{}".format(i)], str(int(args[0]) + i)[:4], str(int(args[0]) + i)[5:6], str(int(args[0]) + i)[6:], 'mqt')       
                eden_dict["bins_{}".format(i)] = np.array(eden_dict["bin_edge_{}".format(i)])
                eden_dict["edenperminute_{}".format(i)] = np.ma.masked_less(eden_dict["edenperminute_{}".format(i)], 0)
            try:
                edenperminute = np.ma.concatenate((eden_dict["edenperminute_{}".format(0)], eden_dict["edenperminute_{}".format(1)]))
            except KeyError:
                print("Concatenation problem:", str(int(args[0]) + int(i)))
                continue
        else:
            eden_dict["eden_filename_{}".format(0)] = '006' + str(int(args[0]))
            eden_dict["eden_fullfiledir_{}".format(0)] = glob.glob(eden_datadir + eden_dict["eden_filename_{}".format(0)] + '***')
            if (len(eden_dict["eden_fullfiledir_{}".format(0)]) == 0):
                print("No file:", str(int(args[0])))
                continue
            else:
                eden_dict["eden_fullfiledir_{}".format(0)] = eden_dict["eden_fullfiledir_{}".format(0)][0]
            if (str(args[0])[4] != '0' and str(args[0])[6] != '0'): 
                [eden_dict["eden_avg_{}".format(0)], eden_dict["edenperminute_{}".format(0)], eden_dict["bin_cen_{}".format(0)], eden_dict["bin_edge_{}".format(0)], eden_dict["timevar_PIP_{}".format(0)], eden_dict["instrument_time_{}".format(0)]] = open_eden_data(eden_dict["eden_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[4:6], str(int(args[0]))[6:], 'mqt')        
            elif (str(args[0])[4] == '0' and str(args[0])[6] != '0'): 
                [eden_dict["eden_avg_{}".format(0)], eden_dict["edenperminute_{}".format(0)], eden_dict["bin_cen_{}".format(0)], eden_dict["bin_edge_{}".format(0)], eden_dict["timevar_PIP_{}".format(0)], eden_dict["instrument_time_{}".format(0)]] = open_eden_data(eden_dict["eden_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[5:6], str(int(args[0]))[6:], 'mqt')        
            elif (str(args[0])[4] != '0' and str(args[0])[6] == '0'): 
                [eden_dict["eden_avg_{}".format(0)], eden_dict["edenperminute_{}".format(0)], eden_dict["bin_cen_{}".format(0)], eden_dict["bin_edge_{}".format(0)], eden_dict["timevar_PIP_{}".format(0)], eden_dict["instrument_time_{}".format(0)]] = open_eden_data(eden_dict["eden_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[4:6], str(int(args[0]))[6:], 'mqt')        
            elif (str(args[0])[4] == '0' and str(args[0])[6] == '0'): 
                [eden_dict["eden_avg_{}".format(0)], eden_dict["edenperminute_{}".format(0)], eden_dict["bin_cen_{}".format(0)], eden_dict["bin_edge_{}".format(0)], eden_dict["timevar_PIP_{}".format(0)], eden_dict["instrument_time_{}".format(0)]] = open_eden_data(eden_dict["eden_fullfiledir_{}".format(0)], str(int(args[0]))[:4], str(int(args[0]))[5:6], str(int(args[0]))[6:], 'mqt')       
            eden_dict["bins_{}".format(0)] = np.array(eden_dict["bin_edge_{}".format(0)])
            eden_dict["edenperminute_{}".format(0)] = np.ma.masked_less(eden_dict["edenperminute_{}".format(0)], 0)
            edenperminute = eden_dict["edenperminute_{}".format(0)]
    
        if (cut_2 != None):
            edenperminute = edenperminute[:int((1440*length_range)-(1440*cut_2))]
    
        if (cut_1 != None):
            edenperminute = edenperminute[int(1440*cut_1):]
    
        if (counter == 0):
            total_edenperminute = edenperminute
            bin_cen = eden_dict["bin_cen_0"]
            #print(np.shape(total_edenperminute))            
        else:
            total_edenperminute = np.ma.concatenate([total_edenperminute, edenperminute])
            #print(np.shape(total_edenperminute))
    
        counter += 1
    
        continue
    
    file_events.close()

    bin_eden = np.arange(0.01,1.01,0.01)    
    bin_D = np.arange(0.4,26.2,0.2)
    bin_edge_4bins = np.ones((np.shape(total_edenperminute)))*bin_cen
    datd = np.histogram2d(total_edenperminute.flatten(), bin_edge_4bins.flatten(), (bin_eden,bin_D),normed=False) 
    norm_hist_d = datd[0]/float(datd[0].sum())
    
    return datd[0], norm_hist_d

