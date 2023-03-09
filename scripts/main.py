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
    df['Timestamp'] = pd.to_datetime(df['yr'] * 1000 + df['DOY'], format='%Y%j')
    df['Timestamp'] +=  pd.to_timedelta(df.hr, unit='h')
    df['Timestamp'] +=  pd.to_timedelta(df.minute, unit='m')
    df.drop(columns=['yr', 'DOY', 'hr', 'minute'], inplace=True)

    # Check first and last timestamp to make sure its the beginning/end of doy
    # otherwise add it for gap filling later
    end_datetime = df.iloc[len(df)-1]
    start_datetime = df.iloc[0]

    if start_datetime.Timestamp.minute != 0:
        correct_start = pd.DataFrame(data={'Timestamp': pd.to_datetime(str(end_datetime.Timestamp.year) + '-' + \
                                                                str(end_datetime.Timestamp.month) + '-' + \
                                                                    str(end_datetime.Timestamp.day) + ' 00:00:00'), 
                                'R_mmhr': np.nan, 'nR_mmhr': np.nan, 'eDensity': np.nan}, index=[0])
        df = pd.concat([df, correct_start], axis=0)

    if end_datetime.Timestamp.minute != 59:
        correct_end = pd.DataFrame(data={'Timestamp': pd.to_datetime(str(end_datetime.Timestamp.year) + '-' + \
                                                                      str(end_datetime.Timestamp.month) + '-' + \
                                                                         str(end_datetime.Timestamp.day) + ' 23:59:00'), 
                                        'R_mmhr': np.nan, 'nR_mmhr': np.nan, 'eDensity': np.nan}, index=[0])
        df = pd.concat([df, correct_end], axis=0)
    
    df.sort_values('Timestamp', inplace=True)
    df = df.set_index('Timestamp').asfreq('1Min')
    df.reset_index(inplace=True)

    ds = df.to_xarray()
    ds.to_netcdf('asd.nc')

    break



