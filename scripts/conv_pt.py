#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- author: Fraser King -*-
# -*- date: March 15, 2023 -*-
# -*- affil: University of Michigan -*-

"""conv_pip.py
   This file includes a set of utility functions for parsing,
   editing and converting PIP level3/study data from .dat files 
   to compressed netCDF4 files.
"""

##### Imports
import os, re, sys
import pandas as pd
import xarray as xr

"""convert_dist
   This function is used to convert a PIP .dat distribution file to netCDF format
"""
def convert_particles(filepath, outpath, lat, lon):
    basename = os.path.splitext(os.path.basename(filepath))[0]
    print("Working on", basename)

    # skip_toks = 4
    # if var == 'psd': # psd files are slightly different
    #     skip_toks = 5

    f = open(filepath)
    lines = f.readlines()
    if len(lines) < 14:
        print("File is empty!")
        return
    
    year, month, day = re.split(r'\t+', lines[5].rstrip('\t\n'))[0], \
                        re.split(r'\t+', lines[5].rstrip('\t\n'))[1], \
                        re.split(r'\t+', lines[5].rstrip('\t\n'))[2]
    
    print(year, month, day)

    columns = re.split(r'\t+', lines[8].rstrip('\t\n'))[:]
    units = re.split(r'\t+', lines[9].rstrip('\t\n'))[:]

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

    ##### Compress and save in NETCDF4 format
    comp = dict(zlib=True, complevel=2)
    encoding = {var: comp for var in ds.data_vars}
    print(outpath)
    ds.to_netcdf(outpath + basename + '.nc', encoding=encoding)
    print("Conversion complete!")

    return
    
    ##### Define global/variable attributes according to CF-1.10 conventions
    ds[var].attrs['units'] = units
    ds[var].attrs['long_name'] = long_name
    ds[var].attrs['standard_name'] = standard_name
    ds[var].attrs['missing_value'] = 'NaN'
    
    ds.bin_centers.attrs['units'] ='mm'
    ds.bin_centers.attrs['long_name'] = 'Vertical bin centers'
    ds.bin_centers.attrs['standard_name'] = 'bin_center'
    ds.bin_centers.attrs['missing_value'] = 'NaN'

    ds.bin_edges.attrs['units'] ='mm'
    ds.bin_edges.attrs['long_name'] = 'Vertical bin edges'
    ds.bin_edges.attrs['standard_name'] = 'bin_edge'
    ds.bin_edges.attrs['missing_value'] = 'NaN'

    ds.time.attrs['long_name'] = ['time']

    ds.attrs['Conventions'] = 'CF-1.10'
    ds.attrs['Contact'] = 'Claire Pettersen (pettersc@umich.edu)'
    ds.attrs['Reference'] = 'https://doi.org/10.3390/atmos11080785'
    # ds.attrs['Author'] = 'Fraser King'

    ##### Compress and save in NETCDF4 format
    comp = dict(zlib=True, complevel=2)
    encoding = {var: comp for var in ds.data_vars}
    print(outpath)
    ds.to_netcdf(outpath + basename + '.nc', encoding=encoding)
    print("Conversion complete!")

convert_particles('/Users/fraserking/Development/pip_processing/example_data/LakeEffect/PIP/2020_MQT/PIP_3/f_1_2_Particle_Tables_ascii/00620200102/0062020010213200_a_p_60.dat', 
                  '', 46.53, -87.55)