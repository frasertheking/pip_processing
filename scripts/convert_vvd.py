#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""convert_vvd.py
   This file includes a set of utility functions for parsing,
   editing and converting PIP VVD data from .dat files 
   to compressed netCDF4 files.
"""

##### Imports
import os, glob, re
import pandas as pd
import numpy as np
import xarray as xr

##### Globals
data_path = '../example_data/LakeEffect/PIP/2020_MQT/PIP_3/f_2_4_VVD_Tables/'
files = sorted(glob.glob(data_path + '*_A.dat'))

##### convert_edensity
##### Takes in PIP L3 summary table .dat files and extracts relevant climate variables to save in netCDF format
def convert_vvd():
    ##### Loop through all PIP L3 .dat files that need to have eDensity converted
    for file in files:
        basename = os.path.splitext(os.path.basename(file))[0]
        print("Working on", basename)


        f = open(file)
        lines = f.readlines()
        year, month, day = re.split(r'\t+', lines[5].rstrip('\t\n'))[0], \
                            re.split(r'\t+', lines[5].rstrip('\t\n'))[1], \
                            re.split(r'\t+', lines[5].rstrip('\t\n'))[2]
        bin_edges = [float(i) for i in re.split(r'\t+', lines[9].rstrip('\t\n'))[4:]]
        bin_centers = [float(i) for i in re.split(r'\t+', lines[11].rstrip('\t\n'))[4:]]

        ##### Parse input
        df = pd.read_csv(file, sep='\t', skiprows=range(0, 11))
        df = df[df['hr_d'] > -99]
        df['year'] = year
        df['month'] = month
        df['day'] = day
        df['hour'] = df['hr_d']
        df['minute'] = df['min_d']
        df['time'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute']], format = '%Y/%MM/%DD %HH:%mm')
        df.drop(columns=['Bin_cen', 'day_time', 'hr_d', 'min_d', 'year', 'month', 'day', 'hour', 'minute'], inplace=True)


        # Check first and last time to make sure its the beginning/end of doy
        # otherwise add it for gap filling later
        end_datetime = df.iloc[len(df)-1]
        start_datetime = df.iloc[0]
        if start_datetime.time.minute != 0:
            correct_start = pd.DataFrame(data={'time': pd.to_datetime(str(start_datetime.time.year) + '-' + \
                                                                    str(start_datetime.time.month) + '-' + \
                                                                        str(start_datetime.time.day) + ' 00:00:00')}, index=[0])
            df = pd.concat([df, correct_start], axis=0)

        if end_datetime.time.minute != 59:
            correct_end = pd.DataFrame(data={'time': pd.to_datetime(str(end_datetime.time.year) + '-' + \
                                                                        str(end_datetime.time.month) + '-' + \
                                                                            str(end_datetime.time.day) + ' 23:59:00')}, index=[0])
            df = pd.concat([df, correct_end], axis=0)

        ##### Fill missing values with NaN and convert to xarray dataset
        df.sort_values('time', inplace=True)
        df = df.set_index('time').asfreq('1Min')
        times = df.index.values
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        ds = xr.Dataset(coords={'time': times, 'bin_centers': bin_centers})
        ds['lat'] = 46.53
        ds['lon'] = -87.55
        ds['vvd'] =(['time', 'bin_centers'], df.to_numpy())
        ds['bin_edges'] = bin_edges
        
        ##### Define global/variable attributes according to CF-1.10 conventions
        ds.vvd.attrs['units'] = 'm s-1'
        ds.vvd.attrs['long_name'] = 'Vertical velocity distributions'
        ds.vvd.attrs['standard_name'] = 'velocity_distribution'
        ds.vvd.attrs['missing_value'] = 'NaN'
        
        ds.bin_centers.attrs['units'] ='mm'
        ds.bin_centers.attrs['long_name'] = 'Vertical bin centers'
        ds.bin_centers.attrs['standard_name'] = 'bin_center'
        ds.bin_centers.attrs['missing_value'] = 'NaN'

        ds.bin_edges.attrs['units'] ='mm'
        ds.bin_edges.attrs['long_name'] = 'Vertical bin edges'
        ds.bin_edges.attrs['standard_name'] = 'bin_edge'
        ds.bin_edges.attrs['missing_value'] = 'NaN'

        ds.time.attrs['long_name'] = ['time']

        ds.attrs['Conventions'] = "CF-1.10"
        ds.attrs['Author'] = "Fraser King"

        ##### Compress and save in NETCDF4 format
        comp = dict(zlib=True, complevel=2)
        encoding = {var: comp for var in ds.data_vars}
        ds.to_netcdf(basename + '.nc', encoding=encoding)

        break

##### Main runscript
if __name__ == "__main__":

    convert_vvd()


