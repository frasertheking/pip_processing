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
import os, re
import pandas as pd
import xarray as xr

"""convert_dist
   This function is used to convert a PIP .dat distribution file to netCDF format
"""
def convert_dist(filepath, outpath, var, lat, lon, units, long_name, standard_name, loc):
    basename = os.path.splitext(os.path.basename(filepath))[0]
    print("Working on", basename)

    skip_toks = 4
    if var == 'psd': # psd files are slightly different
        skip_toks = 5

    f = open(filepath)
    lines = f.readlines()
    if len(lines) < 14:
        print("File is empty!")
        return
    
    year, month, day = re.split(r'\t+', lines[5].rstrip('\t\n'))[0], \
                        re.split(r'\t+', lines[5].rstrip('\t\n'))[1], \
                        re.split(r'\t+', lines[5].rstrip('\t\n'))[2]
    
    bin_edges = [float(i) for i in re.split(r'\t+', lines[9].rstrip('\t\n'))[skip_toks:]]
    bin_centers = [float(i) for i in re.split(r'\t+', lines[11].rstrip('\t\n'))[skip_toks:]]

    ##### Parse input
    df = pd.read_csv(filepath, sep='\t', skiprows=range(0, 11))
    df = df[df['hr_d'] > -99]

    df['year'] = year
    df['month'] = month
    df['day'] = day
    df['hour'] = df['hr_d']
    df['minute'] = df['min_d']
    df['time'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute']], format = '%Y/%MM/%DD %HH:%mm')

    columns = ['Bin_cen', 'day_time', 'hr_d', 'min_d', 'year', 'month', 'day', 'hour', 'minute']
    if var == 'psd':
        columns=['Bin_cen', 'Num_d', 'day_time', 'hr_d', 'min_d', 'year', 'month', 'day', 'hour', 'minute']
    df.drop(columns=columns, inplace=True)

    # ##### Fill missing time
    # end_datetime = df.iloc[len(df)-1]
    # start_datetime = df.iloc[0]
    # if start_datetime.time.minute != 0:
    #     correct_start = pd.DataFrame(data={'time': pd.to_datetime(str(start_datetime.time.year) + '-' + \
    #                                                             str(start_datetime.time.month) + '-' + \
    #                                                                 str(start_datetime.time.day) + ' 00:00:00')}, index=[0])
    #     df = pd.concat([df, correct_start], axis=0)

    # if end_datetime.time.minute != 59:
    #     correct_end = pd.DataFrame(data={'time': pd.to_datetime(str(end_datetime.time.year) + '-' + \
    #                                                                 str(end_datetime.time.month) + '-' + \
    #                                                                     str(end_datetime.time.day) + ' 23:59:00')}, index=[0])
    #     df = pd.concat([df, correct_end], axis=0)

    # ##### Fill missing values with NaN and convert to xarray dataset
    # df.sort_values('time', inplace=True)
    # df = df.set_index('time').asfreq('1Min')
    # times = df.index.values
    # df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    ##### Fill missing time
    start_datetime = df['time'].iloc[0]
    end_datetime = df['time'].iloc[-1]

    all_dates_range = pd.date_range(start=start_datetime.replace(hour=0, minute=0),
                                    end=end_datetime.replace(hour=23, minute=59),
                                    freq='1Min')

    # Set dataframe with full day's range and fill with NaN by default
    df = df.set_index('time').reindex(all_dates_range).reset_index().rename(columns={"index": "time"})

    ##### Fill missing values with NaN and convert to xarray dataset
    df.sort_values('time', inplace=True)
    df = df.set_index('time').asfreq('1Min')
    times = df.index.values
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    ds = xr.Dataset(coords={'time': times, 'bin_centers': bin_centers})
    ds['lat'] = float(lat)
    ds['lon'] = float(lon)
    ds[var] =(['time', 'bin_centers'], df.to_numpy())
    ds['bin_edges'] = bin_edges
    
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
    print(outpath)
    ds.to_netcdf(outpath + basename + '.nc', encoding=encoding)
    print("Conversion complete!")


"""convert_ed
   This function is used to convert a PIP effective density .dat file to netCDF format
"""
def convert_ed(filepath, outpath, lat, lon, loc):
    basename = os.path.splitext(os.path.basename(filepath))[0]
    print("Working on", basename)

    f = open(filepath)
    lines = f.readlines()
    if len(lines) < 11:
        print("File is empty!")
        return

    ##### Parse input
    df = pd.read_csv(filepath, sep='\t', skiprows=range(0, 8))
    df = df[df['yr'] > -99]
    df['time'] = pd.to_datetime(df['yr'] * 1000 + df['DOY'], format='%Y%j')
    df['time'] +=  pd.to_timedelta(df.hr, unit='h')
    df['time'] +=  pd.to_timedelta(df.minute, unit='m')
    df.drop(columns=['yr', 'DOY', 'hr', 'minute'], inplace=True)

    ##### Fill missing time
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
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    ds = df.to_xarray()
    ds = ds.rename({'nR_mmhr': 'nrr', 'R_mmhr': 'rr', 'eDensity': 'ed'})
    ds['lat'] = float(lat)
    ds['lon'] = float(lon)

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
    print("Conversion complete!")
