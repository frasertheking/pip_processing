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
import os, re, gc
import pandas as pd

"""convert_particle_table
   This function is used to convert a PIP .dat distribution file to netCDF format
"""
def convert_particle_table(filepath, outpath, lat, lon, loc):
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
    df = pd.read_csv(filepath, sep='\t', skiprows=range(0, 10), header=0, names=columns, error_bad_lines=False)
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
    ds.attrs['Contact1'] = 'Claire Pettersen (pettersc@umich.edu), Primary Contact'
    ds.attrs['Contact2'] = 'Fraser King (kingfr@umich.edu)'
    ds.attrs['Contact3'] = 'David Wolff (david.b.wolff@nasa.gov)'
    ds.attrs['Reference1'] = 'https://doi.org/10.3390/atmos11080785'
    ds.attrs['Reference2'] = 'https://doi.org/10.3390/rs13112183'
    ds.attrs['Reference3'] = 'https://doi.org/10.1175/JAMC-D-19-0099.1'
    ds.attrs['Reference4'] = 'https://doi.org/10.1175/BAMS-D-19-0128.1'
    ds.attrs['Comment1'] = 'Data was acquired at the ' + loc + ' site (Lat: ' + str(lat) + ', Lon: ' + str(lon) + ')'

    ##### Compress and save in NETCDF4 format
    comp = dict(zlib=True, complevel=2)
    encoding = {var: comp for var in ds.data_vars}
    ds.to_netcdf(outpath + basename + '.nc', encoding=encoding)
    gc.collect()
    print("Conversion complete!")
