import os
import xarray as xr
import pandas as pd
import numpy as np

LAT = 47.97
LON = 123.5
SITE = "Washington State, USA"

input_file_path = '/Users/fraserking/Development/pip_processing/data/MET/OLY/olympex_AHD_met_2015_2016.nc'
output_folder_base_path = '/Users/fraserking/Desktop/OLY_OUT/'

try:
    ds = xr.open_dataset(input_file_path)

    # Check if 'time' needs conversion from numeric values representing minutes
    if not np.issubdtype(ds['time'].dtype, np.datetime64):
        # Assuming ds['time'] contains numeric values representing minutes since the origin
        time_origin = pd.Timestamp("2015-11-14 00:00:00")
        ds['time'] = pd.to_timedelta(ds['time'].values, unit='m') + time_origin
    else:
        # Handle case where 'time' is already in datetime64 format
        # This part might need adjustment based on actual dataset characteristics
        print("'time' appears to be already in datetime format.")


    # Renaming variables according to your specification
    variable_mapping = {
        'WXT520_temp': 'temperature',
        'WXT520_press': 'pressure',
        'WXT520_rh': 'relative_humidity',
        'WXT520_wspd': 'wind_speed',
        'WXT520_wdir': 'wind_direction',
    }
    
    # Apply renaming
    ds_renamed = ds.rename(variable_mapping)
    
    # Ensure latitude, longitude, and metadata are set
    ds_renamed = ds_renamed.assign(lat=xr.DataArray(LAT, dims=()), lon=xr.DataArray(LON, dims=()))
    ds_renamed.attrs['Comment1'] = f"Data was acquired at the {SITE} site (Lat: {LAT}, Lon: {LON})"
    
    # Filter to only include specified variables plus 'lat', 'lon', and 'time'
    filtered_variables = list(variable_mapping.values()) + ['lat', 'lon', 'time']
    ds_filtered = ds_renamed[filtered_variables]
    
    # Group by day and save separate files
    for group, group_ds in ds_filtered.resample(time='D'):
        # Skip empty groups
        if group_ds.sizes['time'] == 0:
            continue
            
        # Convert numpy.datetime64 to datetime.date for the group label
        group_date = pd.to_datetime(str(group)).date()
        
        # Format the date for the filename
        date_str = group_date.strftime('%Y%m%d')
        output_file_path = os.path.join(output_folder_base_path, f"{date_str}_met.nc")
        
        # Save the daily data
        group_ds.to_netcdf(output_file_path)
        print(f"Saved data for {date_str} to {output_file_path}")

except Exception as e:
    print(f"An error occurred: {e}")
