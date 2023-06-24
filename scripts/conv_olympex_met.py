import pandas as pd
import xarray as xr
import os
import glob
from datetime import datetime
import numpy as np

# Save units for later (they never change)
units = ['hh:mm','ge_0.2_mm/h','mm/h','m','mm/h','m','dBZ','mm/h','hPa','degC','%','mm/h','m/s', 'deg']

# Initialize a list to store xarray Datasets
ds_list = []

# Loop over each .csv file in the directory
for file in glob.glob("/Users/fraserking/Development/pip_processing/data/to_upload/OLYMPEx_MET/olympex_AHD_********_met-station.csv"):

    print(file)

    # Read the first line of the file to get the date
    with open(file, 'r') as f:
        first_line = f.readline().strip()
    file_date = datetime.strptime(first_line, '%Y-%m-%d').date()

    # Read the csv file, skip the first two lines, and set the third line as the header
    df = pd.read_csv(file, skiprows=[0, 2], header=[0])

    # Convert 'time' column to datetime
    df['time'] = pd.to_datetime(df['time'].apply(lambda x: str(file_date) + ' ' + x), format='%Y-%m-%d %H:%M')

    # Set 'time' as index
    df.set_index('time', inplace=True)

    # Convert all non-time columns to numerical data (this will convert 'NaN' strings to actual NaN values)
    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # Convert the DataFrame into an xarray Dataset
    ds = xr.Dataset.from_dataframe(df)

    # Replace all 'NaN' values with np.nan
    ds = ds.where(ds != 'NaN', np.nan)

    # Assign units to variables
    for var, unit in zip(ds.data_vars, units[1:]):  # skip first unit (it's for time)
        ds[var].attrs['units'] = unit

    # Append the Dataset to the list
    ds_list.append(ds)

# Concatenate all Datasets along the 'time' dimension
ds_combined = xr.concat(ds_list, dim='time')

# Sort by time
ds_combined = ds_combined.sortby('time')

# Save the combined Dataset into a .nc file
ds_combined.to_netcdf('/Users/fraserking/Development/pip_processing/data/to_upload/OLYMPEx_MET/combined_dataset.nc')
