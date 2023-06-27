"""
make_PIP_quicklooks.py --> functions to plot a quicklook of PIP data for a given event/date
Jack Richter

Created: 06/15/2023
"""

import netCDF4 as nc
import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import numpy.ma
import sys
import glob

# sys.path.insert(1, '/home/jrichter/python/mqt/py_files')
from pip_tools_original_JackCopy import open_dist_data
from pip_tools_original_JackCopy import open_eden_data

# -------------------------------------------------------------------------------------------------------------------------------

# from https://stackoverflow.com/questions/575925/how-to-convert-rational-and-decimal-number-strings-to-floats-in-python
"""
    Simple function found on stackoverflow that will convert string representations of floats to actual floats
    
    input: s --> string representation of a float, e.g. "20.3"
    output: actual float of s, e.g. 20.3
"""
def convert(s):
    try:
        return float(s)
    except ValueError:
        num, denom = s.split('/')
        return float(num) / float(denom)
    
# -------------------------------------------------------------------------------------------------------------------------------

"""
    This script takes a date as input and plots a PIP quicklook (PSD and eden) for that date. Currently, this script plots data 
    from Marquette, MI (MQT). To plot PIP data from other sites, change the PIP directory and glob.glob call.
    
    input: date --> date (YYYYMMDD) to plot. Can be a string or integer.
           cut_1 --> amount in fraction of the day to cut from the beginning of the event. For example, if a date has snowfall
               beginning at 8 UTC, you may want to have cut_1 = 8/24 so that the quicklook focuses on the actual precip.
           cut_2 --> amount in fraction of the day to cut from the end of the event. For example, if a date has snowfall ending
               at 16 UTC, you may want to have cut_2 = 8/24 so that the end of the day is cut off and the quicklook focuses on 
               the actual precip.
               
    output: None --> implicitly returns the completed figure (at least in jupyter). You may need to update the output to return 
                fig or axs if you are using a shell.
"""
def plot_PIP_quicklook(date, cut_1=None, cut_2=None):
    
    if (cut_1 != "None" and cut_1 != None):
        cut_1 = convert(cut_1)
    elif (cut_1 == "None"):
        cut_1 = None
    
    if (cut_2 != "None" and cut_2 != None):
        cut_2 = convert(cut_2)   
    elif (cut_2 == "None"):
        cut_2 = None
    
    # Obtaining and formatting PIP PSD data
    #/Users/fraserking/Development/pip_processing/data/PIP/2019_MQT/f_1_4_DSD_Tables_ascii/006201902152350_01_dsd.dat
    # PIP_datadir = '/data/LakeEffect/PIP/' + str(date)[:4] + '_MQT/PIP_3/f_1_4_DSD_Tables_ascii/'
    # PIP_filename = '006' + str(date)
    # PIP_fullfiledir = glob.glob(PIP_datadir + PIP_filename + '***')
    # if (len(PIP_fullfiledir) == 0):
    #     print("No PSD File Found:", date)
    #     # Note, just because there is no PSD file doesn't necessarily mean that there is no eDensity file
    #     # Try plotting just the eDensity
    #     return plot_PIP_eDensity(date, cut_1, cut_2)
    # else:
    #     PIP_fullfiledir = PIP_fullfiledir[0]
        
    # # Obtaining and formatting PIP eDensity data
    # PIP_eDensity_datadir = '/data/LakeEffect/PIP/' + str(date)[:4] + '_MQT/Study/f_2_6_rho_Plots_D_minute_dat/'
    # PIP_eDensity_filename = '006' + str(date)
    # PIP_eDensity_fullfiledir = glob.glob(PIP_eDensity_datadir + PIP_eDensity_filename + '***')
    # if len(PIP_eDensity_fullfiledir) == 0:
    #     print("No eDensity File Found:", date)
    #     # Note, just because there is no eDensity file doesn't necessarily mean that there is no PSD file
    #     # Try plotting just the PSD
    #     return plot_PIP_PSD(date, cut_1, cut_2)
    # else:
    #     PIP_eDensity_fullfiledir = PIP_eDensity_fullfiledir[0]

    PIP_fullfiledir = '/Users/fraserking/Development/pip_processing/data/PIP/2019_MQT/f_1_4_DSD_Tables_ascii/006201902152350_01_dsd.dat'
    PIP_eDensity_fullfiledir = '/Users/fraserking/Development/pip_processing/data/PIP/2019_MQT/f_2_6_rho_Plots_D_minute_dat/006201902152350_01_rho_Plots_D_minute.dat'

    # these conditionals look messy but they just format the input args to open_dist_data based on the date
    if (str(date)[4] != '0' and str(date)[6] != '0'): 
        [DSD_avg, dsdperminute, bin_cen, bin_edge, timevar_PIP, instrument_time] = open_dist_data(PIP_fullfiledir, str(date)[:4], str(date)[4:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] == '0' and str(date)[6] != '0'): 
        [DSD_avg, dsdperminute, bin_cen, bin_edge, timevar_PIP, instrument_time] = open_dist_data(PIP_fullfiledir, str(date)[:4], str(date)[5:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] != '0' and str(date)[6] == '0'): 
        [DSD_avg, dsdperminute, bin_cen, bin_edge, timevar_PIP, instrument_time] = open_dist_data(PIP_fullfiledir, str(date)[:4], str(date)[4:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] == '0' and str(date)[6] == '0'): 
        [DSD_avg, dsdperminute, bin_cen, bin_edge, timevar_PIP, instrument_time] = open_dist_data(PIP_fullfiledir, str(date)[:4], str(date)[5:6], str(date)[6:], 'mqt')
        
    timevar_PIP = np.array(timevar_PIP)
    bins = np.array(bin_cen) # if the bins end up looking weird try switching this to np.array(bin_edge)
    DSD_avg = numpy.ma.masked_less(DSD_avg,0)
    dsdperminute = numpy.ma.masked_less(dsdperminute, 0)
    
    # these conditionals format the input args to open_eden_data
    if (str(date)[4] != '0' and str(date)[6] != '0'): 
        [EDEN_avg, edenperminute, bin_cen_eden, bin_edge_eDensity, timevar_PIP_eDensity, instrument_time] = open_eden_data(PIP_eDensity_fullfiledir, str(date)[:4], str(date)[4:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] == '0' and str(date)[6] != '0'): 
        [EDEN_avg, edenperminute, bin_cen_eden, bin_edge_eDensity, timevar_PIP_eDensity, instrument_time] = open_eden_data(PIP_eDensity_fullfiledir, str(date)[:4], str(date)[5:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] != '0' and str(date)[6] == '0'): 
        [EDEN_avg, edenperminute, bin_cen_eden, bin_edge_eDensity, timevar_PIP_eDensity, instrument_time] = open_eden_data(PIP_eDensity_fullfiledir, str(date)[:4], str(date)[4:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] == '0' and str(date)[6] == '0'): 
        [EDEN_avg, edenperminute, bin_cen_eden, bin_edge_eDensity, timevar_PIP_eDensity, instrument_time] = open_eden_data(PIP_eDensity_fullfiledir, str(date)[:4], str(date)[5:6], str(date)[6:], 'mqt')
        
    timevar_PIP_eDensity = np.array(timevar_PIP_eDensity)
    bins_eDensity = np.array(bin_cen_eden) # if the bins end up looking weird try switching this to np.array(bin_edge_eDensity)
    EDEN_avg = numpy.ma.masked_less(EDEN_avg,0)
    edenperminute = numpy.ma.masked_less(edenperminute, 0)
    
    # slicing the data so that we just plot the precipitation. Use cut_1 = None and cut_2 = None to plot the entire day
    if (cut_2 != None):
        timevar_PIP = timevar_PIP[:int((1440)-(1440*cut_2))]
        timevar_PIP_eDensity = timevar_PIP_eDensity[:int((1440)-(1440*cut_2))]
        dsdperminute = dsdperminute[:int((1440)-(1440*cut_2))]
        edenperminute = edenperminute[:int((1440)-(1440*cut_2))]
    
    if (cut_1 != None):
        timevar_PIP = timevar_PIP[int(1440*cut_1):]
        timevar_PIP_eDensity = timevar_PIP_eDensity[int(1440*cut_1):]
        dsdperminute = dsdperminute[int(1440*cut_1):]
        edenperminute = edenperminute[int(1440*cut_1):]
    
    # creating the subplots
    fig, axs = plt.subplots(2, figsize=(12,8), dpi=150, sharex=True)
    plt.subplots_adjust(hspace=0)
    
    # PIP PSD plot
    PSD = axs[0].pcolormesh(timevar_PIP, bins, numpy.ma.log10(dsdperminute).T, cmap = "jet")
    cb = plt.colorbar(PSD, ax=axs[0], label="$log_{10}$(PSD) [$m^{-3}$ $mm^{-1}$]", shrink=.9, pad=.02)
    cb.set_label(label='$log_{10}$(PSD) [$m^{-3}$ $mm^{-1}$]', size='16')
    cb.ax.tick_params(labelsize='16')
    axs[0].grid()
    axs[0].tick_params(axis='y', labelsize=16)
    axs[0].set_ylabel('Diameter [mm]', size=16) 
    axs[0].set_title('PIP Quicklook ' + str(date), size=20)
    
    # PIP eDensity plot
    eDensity = axs[1].pcolormesh(timevar_PIP_eDensity, bins_eDensity, edenperminute.T, cmap = "jet", vmin=0, vmax=1)
    cb = plt.colorbar(eDensity, ax=axs[1], label="eDensity (gm/ml)", shrink=.9, pad=.02)
    cb.set_label(label='Effective Density [$g cm^{-3}$]', size='16')
    cb.ax.tick_params(labelsize='16')
    axs[1].grid()
    axs[1].tick_params(axis='y', labelsize=16)
    axs[1].set_ylabel('Diamter [mm]', size=16) 
    axs[1].set_xlabel('Time [UTC]', size=16)
    date_form = DateFormatter("%H:%M")
    plt.gca().xaxis.set_major_formatter(date_form)
    plt.show()

    # Save the figure if you want, just uncomment and update the file path
    #fig.savefig('/home/jrichter/python/mqt/{}'.format(date) + '.png')
    #fig.savefig('/data/jrichter/mqt/AR_panels/{}'.format(date) + ".png")

    return None # switch this to fig or axs if the plot doesn't show up on your viewer


plot_PIP_quicklook('20190215')

# -------------------------------------------------------------------------------------------------------------------------------
"""
    Similar functionality as plot_PIP_quicklook --> except only for eDensity data (NO PSD)
    See function header above for more info on inputs and outputs.
"""
def plot_PIP_eDensity(date, cut_1=None, cut_2=None):
    
    if (cut_1 != "None" and cut_1 != None):
        cut_1 = convert(cut_1)
    elif (cut_1 == "None"):
        cut_1 = None
    
    if (cut_2 != "None" and cut_2 != None):
        cut_2 = convert(cut_2)   
    elif (cut_2 == "None"):
        cut_2 = None
        
    # Obtaining and formatting PIP eDensity data
    PIP_eDensity_datadir = '/data/LakeEffect/PIP/' + str(date)[:4] + '_MQT/Study/f_2_6_rho_Plots_D_minute_dat/'
    PIP_eDensity_filename = '006' + str(date)
    PIP_eDensity_fullfiledir = glob.glob(PIP_eDensity_datadir + PIP_eDensity_filename + '***')
    if len(PIP_eDensity_fullfiledir) == 0:
        print("No eDensity File Found:", date)
        return None
    else:
        PIP_eDensity_fullfiledir = PIP_eDensity_fullfiledir[0]
        
    # these conditionals format the input args to open_eden_data
    if (str(date)[4] != '0' and str(date)[6] != '0'): 
        [EDEN_avg, edenperminute, bin_cen_eden, bin_edge_eDensity, timevar_PIP_eDensity, instrument_time] = open_eden_data(PIP_eDensity_fullfiledir, str(date)[:4], str(date)[4:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] == '0' and str(date)[6] != '0'): 
        [EDEN_avg, edenperminute, bin_cen_eden, bin_edge_eDensity, timevar_PIP_eDensity, instrument_time] = open_eden_data(PIP_eDensity_fullfiledir, str(date)[:4], str(date)[5:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] != '0' and str(date)[6] == '0'): 
        [EDEN_avg, edenperminute, bin_cen_eden, bin_edge_eDensity, timevar_PIP_eDensity, instrument_time] = open_eden_data(PIP_eDensity_fullfiledir, str(date)[:4], str(date)[4:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] == '0' and str(date)[6] == '0'): 
        [EDEN_avg, edenperminute, bin_cen_eden, bin_edge_eDensity, timevar_PIP_eDensity, instrument_time] = open_eden_data(PIP_eDensity_fullfiledir, str(date)[:4], str(date)[5:6], str(date)[6:], 'mqt')
        
    timevar_PIP_eDensity = np.array(timevar_PIP_eDensity)
    bins_eDensity = np.array(bin_cen_eden) # if the bins end up looking weird try switching this to np.array(bin_edge_eDensity)
    EDEN_avg = numpy.ma.masked_less(EDEN_avg,0)
    edenperminute = numpy.ma.masked_less(edenperminute, 0)
    
    # slicing the data so that we just plot the precipitation. Use cut_1 = None and cut_2 = None to plot the entire day
    if (cut_2 != None):
        timevar_PIP_eDensity = timevar_PIP_eDensity[:int((1440)-(1440*cut_2))]
        edenperminute = edenperminute[:int((1440)-(1440*cut_2))]
    
    if (cut_1 != None):
        timevar_PIP_eDensity = timevar_PIP_eDensity[int(1440*cut_1):]
        edenperminute = edenperminute[int(1440*cut_1):]
        
    plt.figure(figsize=(12,4), dpi=150)
    # PIP eDensity plot
    eDensity = plt.pcolormesh(timevar_PIP_eDensity, bins_eDensity, edenperminute.T, cmap = "jet", vmin=0, vmax=1)
    cb = plt.colorbar(eDensity, label="eDensity (gm/ml)", shrink=.9, pad=.02)
    cb.set_label(label='Effective Density [$g cm^{-3}$]', size='16')
    cb.ax.tick_params(labelsize='16')
    plt.grid()
    plt.tick_params(axis='y', labelsize=16)
    plt.ylabel('Diamter [mm]', size=16) 
    plt.xlabel('Time [UTC]', size=16)
    date_form = DateFormatter("%H:%M")
    plt.gca().xaxis.set_major_formatter(date_form)
    plt.title("PIP Effective Density " + str(date), size=20)
    
    # Save the figure if you want, just uncomment and update the file path
    #plt.savefig('/home/jrichter/python/mqt/{}'.format(date) + '.png')
    #plt.savefig('/data/jrichter/mqt/AR_panels/{}'.format(date) + ".png")
    
    plt.show()

    return None

# -------------------------------------------------------------------------------------------------------------------------------
"""
    Similar functionality as plot_PIP_quicklook --> except only for PSD data (NO EDENSITY)
    See function header above for more info on inputs and outputs.
"""
def plot_PIP_PSD(date, cut_1=None, cut_2=None):
    
    if (cut_1 != "None" and cut_1 != None):
        cut_1 = convert(cut_1)
    elif (cut_1 == "None"):
        cut_1 = None
    
    if (cut_2 != "None" and cut_2 != None):
        cut_2 = convert(cut_2)   
    elif (cut_2 == "None"):
        cut_2 = None
    
    # Obtaining and formatting PIP PSD data
    PIP_datadir = '/data/LakeEffect/PIP/' + str(date)[:4] + '_MQT/PIP_3/f_1_4_DSD_Tables_ascii/'
    PIP_filename = '006' + str(date)
    PIP_fullfiledir = glob.glob(PIP_datadir + PIP_filename + '***')
    if (len(PIP_fullfiledir) == 0):
        print("No PSD File Found:", date)
        return None
    else:
        PIP_fullfiledir = PIP_fullfiledir[0]
    
    # these conditionals look messy but they just format the input args to open_dist_data based on the date
    if (str(date)[4] != '0' and str(date)[6] != '0'): 
        [DSD_avg, dsdperminute, bin_cen, bin_edge, timevar_PIP, instrument_time] = open_dist_data(PIP_fullfiledir, str(date)[:4], str(date)[4:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] == '0' and str(date)[6] != '0'): 
        [DSD_avg, dsdperminute, bin_cen, bin_edge, timevar_PIP, instrument_time] = open_dist_data(PIP_fullfiledir, str(date)[:4], str(date)[5:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] != '0' and str(date)[6] == '0'): 
        [DSD_avg, dsdperminute, bin_cen, bin_edge, timevar_PIP, instrument_time] = open_dist_data(PIP_fullfiledir, str(date)[:4], str(date)[4:6], str(date)[6:], 'mqt')
        
    elif (str(date)[4] == '0' and str(date)[6] == '0'): 
        [DSD_avg, dsdperminute, bin_cen, bin_edge, timevar_PIP, instrument_time] = open_dist_data(PIP_fullfiledir, str(date)[:4], str(date)[5:6], str(date)[6:], 'mqt')
        
    timevar_PIP = np.array(timevar_PIP)
    bins = np.array(bin_cen) # if the bins end up looking weird try switching this to np.array(bin_edge)
    DSD_avg = numpy.ma.masked_less(DSD_avg,0)
    dsdperminute = numpy.ma.masked_less(dsdperminute, 0)
    
    # slicing the data so that we just plot the precipitation. Use cut_1 = None and cut_2 = None to plot the entire day
    if (cut_2 != None):
        timevar_PIP = timevar_PIP[:int((1440)-(1440*cut_2))]
        dsdperminute = dsdperminute[:int((1440)-(1440*cut_2))]
    
    if (cut_1 != None):
        timevar_PIP = timevar_PIP[int(1440*cut_1):]
        dsdperminute = dsdperminute[int(1440*cut_1):]
        
    plt.figure(figsize=(12,4), dpi=150)
    # PIP PSD plot
    PSD = plt.pcolormesh(timevar_PIP, bins, np.ma.log10(dsdperminute.T), cmap = "jet")
    cb = plt.colorbar(PSD, label="$log_{10}$(PSD) [$m^{-3}$ $mm^{-1}$]", shrink=.9, pad=.02)
    cb.set_label(label='$log_{10}$(PSD) [$m^{-3}$ $mm^{-1}$]', size='16')
    cb.ax.tick_params(labelsize='16')
    plt.grid()
    plt.tick_params(axis='y', labelsize=16)
    plt.ylabel('Diamter [mm]', size=16) 
    plt.xlabel('Time [UTC]', size=16)
    date_form = DateFormatter("%H:%M")
    plt.gca().xaxis.set_major_formatter(date_form)
    plt.title("PIP PSD " + str(date), size=20)
    
    # Save the figure if you want, just uncomment and update the file path
    #plt.savefig('/home/jrichter/python/mqt/{}'.format(date) + '.png')
    #plt.savefig('/data/jrichter/mqt/AR_panels/{}'.format(date) + ".png")
    
    plt.show()

    return None
    