"""
Dm_helpers.py --> functions to assist analysis of PIP PSD mass-weighted mean diameter
Jack Richter

File Created: 05/16/2023
Last Updated: 05/16/2023 --> implementation started
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
from pip_tools_original_JackCopy import open_dist_data

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
    This function takes a filename representing a snowfall event dataset as input and calculates the mass-weighted mean 
    diameters (Dm) across 15-minute running PSD averages throughout the dataset
    
    Input: filename --> path name representing a file containing a dataset of snowfall events***
    *** see /home/jrichter/python/mqt/txt_files/MQT_ARs_Snow.txt for how my datasets are organized
    *** format: start date, end date, fraction to cut at the beginning, fraction to cut at the end, start time, duration (hours)
    
    Output: Dm_array --> array of Dm values across the dataset
"""
def get_Dm(filename):
        
    file_events = open(filename, "r")
    
    Dm_array = np.empty(np.shape([]))
    
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
                bin_cen = np.array(PIP_dict["bin_cen_0"])
            try:
                dsdperminute = np.ma.concatenate((PIP_dict["dsdperminute_{}".format(0)], PIP_dict["dsdperminute_{}".format(1)]))
                if (cut_2 != None):
                    dsdperminute = dsdperminute[:int((1440*length_range)-(1440*cut_2))]

                if (cut_1 != None):
                    dsdperminute = dsdperminute[int(1440*cut_1):]
                
                dsdperminute_running_avg = np.empty(np.shape(dsdperminute))
                
                for i in range(np.shape(dsdperminute)[0]):
                    if i < 8:
                        curr_avg = np.mean(dsdperminute[0:15, :], axis=0)
                    elif i >= 8 and i <= np.shape(dsdperminute)[0] - 7:
                        curr_avg = np.mean(dsdperminute[int(i-(15/2)):int(i+(15/2)), :], axis=0)
                    elif i > np.shape(dsdperminute)[0] - 7:
                        curr_avg = np.mean(dsdperminute[np.shape(dsdperminute)[0]-15:, :], axis=0)
                    dsdperminute_running_avg[i] = curr_avg
                    
                curr_diam_d = np.zeros(dsdperminute_running_avg.shape)
                curr_diam_d[:] = bin_cen[:][np.newaxis,:]

                curr_mom3_d = np.sum((curr_diam_d**3)*dsdperminute_running_avg, axis=1)
                curr_mom4_d = np.sum((curr_diam_d**4)*dsdperminute_running_avg, axis=1)

                curr_Dm_d = curr_mom4_d / curr_mom3_d
                
            except Exception as e:
                print("Concatenation problem or Dm Issue:", str(int(args[0]) + int(i)))
                print(e)
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
            bin_cen = np.array(PIP_dict["bin_cen_0"])
    
            if (cut_2 != None):
                dsdperminute = dsdperminute[:int((1440*length_range)-(1440*cut_2))]
    
            if (cut_1 != None):
                dsdperminute = dsdperminute[int(1440*cut_1):]
            
            dsdperminute_running_avg = np.empty(np.shape(dsdperminute))
                
            for i in range(np.shape(dsdperminute)[0]):
                if i < 8:
                    curr_avg = np.mean(dsdperminute[0:15, :], axis=0)
                elif i >= 8 and i <= np.shape(dsdperminute)[0] - 7:
                    curr_avg = np.mean(dsdperminute[int(i-(15/2)):int(i+(15/2)), :], axis=0)
                elif i > np.shape(dsdperminute)[0] - 7:
                    curr_avg = np.mean(dsdperminute[np.shape(dsdperminute)[0]-15:, :], axis=0)
                dsdperminute_running_avg[i] = curr_avg
                    
            curr_diam_d = np.zeros(dsdperminute_running_avg.shape)
            curr_diam_d[:] = bin_cen[:][np.newaxis,:]

            curr_mom3_d = np.sum((curr_diam_d**3)*dsdperminute_running_avg, axis=1)
            curr_mom4_d = np.sum((curr_diam_d**4)*dsdperminute_running_avg, axis=1)

            curr_Dm_d = curr_mom4_d / curr_mom3_d
         
        Dm_array = np.ma.concatenate((Dm_array, curr_Dm_d))
                
        continue
    
    file_events.close()
    
    return Dm_array
