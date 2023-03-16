#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""convert_edensity.py
   This file includes a set of utility functions for parsing,
   editing and converting PIP edensity data from .dat files 
   to compressed netCDF4 files.
"""

##### Imports
import os, glob
import pandas as pd
import numpy as np

##### Globals
data_path = '../example_data/LakeEffect/PIP/2020_MQT/Study/f_3_1_Summary_Tables_P/'
files = sorted(glob.glob(data_path + '*.dat'))

##### convert_edensity
##### Takes in PIP L3 summary table .dat files and extracts relevant climate variables to save in netCDF format
def convert_edensity():
    ##### Loop through all PIP L3 .dat files that need to have eDensity converted
    for file in files:
        basename = os.path.splitext(os.path.basename(file))[0]
        print("Working on", basename)

        ##### Parse input
        df = pd.read_csv(file, sep='\t', skiprows=range(0, 8))
        df = df[df['yr'] > -99]
        df['time'] = pd.to_datetime(df['yr'] * 1000 + df['DOY'], format='%Y%j')
        df['time'] +=  pd.to_timedelta(df.hr, unit='h')
        df['time'] +=  pd.to_timedelta(df.minute, unit='m')
        df.drop(columns=['yr', 'DOY', 'hr', 'minute'], inplace=True)

        # Check first and last time to make sure its the beginning/end of doy
        # otherwise add it for gap filling later
        end_datetime = df.iloc[len(df)-1]
        start_datetime = df.iloc[0]
        if start_datetime.time.minute != 0:
            correct_start = pd.DataFrame(data={'time': pd.to_datetime(str(start_datetime.time.year) + '-' + \
                                                                    str(start_datetime.time.month) + '-' + \
                                                                        str(start_datetime.time.day) + ' 00:00:00'), 
                                    'R_mmhr': np.nan, 'nR_mmhr': np.nan, 'eDensity': np.nan}, index=[0])
            df = pd.concat([df, correct_start], axis=0)

        if end_datetime.time.minute != 59:
            correct_end = pd.DataFrame(data={'time': pd.to_datetime(str(end_datetime.time.year) + '-' + \
                                                                        str(end_datetime.time.month) + '-' + \
                                                                            str(end_datetime.time.day) + ' 23:59:00'), 
                                            'R_mmhr': np.nan, 'nR_mmhr': np.nan, 'eDensity': np.nan}, index=[0])
            df = pd.concat([df, correct_end], axis=0)

        ##### Fill missing values with NaN and convert to xarray dataset
        df.sort_values('time', inplace=True)
        df = df.set_index('time').asfreq('1Min')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        ds = df.to_xarray()
        ds = ds.rename({'nR_mmhr': 'nrr', 'R_mmhr': 'rr', 'eDensity': 'ed'})
        ds['lat'] = 46.53
        ds['lon'] = -87.55

        ##### Define global/variable attributes according to CF-1.10 conventions
        ds.ed.attrs['units'] = 'g cm-3'
        ds.ed.attrs['long_name'] = 'Effective density'
        ds.ed.attrs['standard_name'] = 'effective_density'
        ds.ed.attrs['missing_value'] = 'NaN'
        
        ds.nrr.attrs['units'] ='mm hr-1'
        ds.nrr.attrs['long_name'] = 'Non-rain rate'
        ds.nrr.attrs['standard_name'] = 'non_rainfall_rate'
        ds.nrr.attrs['missing_value'] = 'NaN'

        ds.rr.attrs['units'] ='mm hr-1'
        ds.rr.attrs['long_name'] = 'Rain rate'
        ds.rr.attrs['standard_name'] = 'rainfall_rate'
        ds.rr.attrs['missing_value'] = 'NaN'

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

    convert_edensity()


