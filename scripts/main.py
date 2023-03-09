import glob
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

data_path = '../example_data/LakeEffect/PIP/2020_MQT/PIP_3/f_3_1_Summary_Tables_R/'
files = sorted(glob.glob(data_path + '*.dat'))

for file in files:
    print(file)
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
    print(start_datetime)

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
    
    df.sort_values('time', inplace=True)
    df = df.set_index('time').asfreq('1Min')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    ds = df.to_xarray()
    print(ds)

    ds.to_netcdf('asd.nc')


    break



