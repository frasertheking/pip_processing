#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- author: Fraser King -*-
# -*- date: March 22, 2023 -*-
# -*- affil: University of Michigan -*-

"""conv_pt.py
   This file includes a set of utility functions for parsing,
   editing and converting PIP level3 particle table data from
   .dat files to compressed netCDF4 files.
"""

##### Imports
import os, re
import pandas as pd

"""convert_particle_table
   This function is used to convert a PIP .dat distribution file to netCDF format
"""
def convert_particle_table(filepath, outpath, lat, lon):
    basename = os.path.splitext(os.path.basename(filepath))[0]
    print("Working on", basename)

    f = open(filepath)
    lines = f.readlines()
    if len(lines) < 12:
        print("File is empty!")
        return
    
    columns = re.split(r'\t+', lines[8].rstrip('\t\n'))[:]
    units = ['id', 'nd', 'Site', 'nd', 'Logical', 'nd', 'nd', 'Interval', 'Interval', 'Interval', 'nd', 'mm', 'mm', 'mm^2', 'mm', 'mm', 'deg', 'mm', 'mm', 'mm', 'mm', 'nd', 'nd', 'nd', 'nd', 'mm', 'mm', 'nd', '16_bit', '8_bit']

    ##### Parse input
    df = pd.read_csv(filepath, sep='\t', skiprows=range(0, 10), header=0, names=columns)
    df = df[df['RecNum'] > -99]

    df['Hour'] = df['Hr']
    df['Minute'] = df['Min']
    df['Second'] = df['Sec']
    df['time'] = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']], format = '%Y/%MM/%DD %HH:%mm:%ss')
    df.drop(columns=['Year', 'Month', 'Day', 'Hr', 'Min', 'Sec', 'Hour', 'Minute', 'Second'], inplace=True)
    df.index.names=['particle_ID']

    ds = df.to_xarray()
    ds['lat'] = float(lat)
    ds['lon'] = float(lon)

    for i, var in enumerate(df.columns):
        if var == 'time':
            ds.time.attrs['long_name'] = ['time']
            continue

        ds[var].attrs['units'] = units[i]
        ds[var].attrs['missing_value'] = 'NaN'

    ds.attrs['Conventions'] = 'CF-1.10'
    ds.attrs['Contact'] = 'Claire Pettersen (pettersc@umich.edu)'
    ds.attrs['Reference'] = 'https://doi.org/10.3390/atmos11080785'
    # ds.attrs['Author'] = 'Fraser King'

    ##### Compress and save in NETCDF4 format
    comp = dict(zlib=True, complevel=2)
    encoding = {var: comp for var in ds.data_vars}
    ds.to_netcdf(outpath + basename + '.nc', encoding=encoding)
    print("Conversion complete!")
