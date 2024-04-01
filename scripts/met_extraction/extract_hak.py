import os
import xarray as xr
import pandas as pd

LAT=59.81
LON=7.21
SITE="Haukeliseter, Norway"

input_file_path = '/Users/fraserking/Development/pip_processing/data/MET/HAUK/Haukeliseter_Norway_met.nc'
output_folder_base_path = '/Users/fraserking/Desktop/HAK_OUT/'

try:
    ds = xr.open_dataset(input_file_path)

    # Convert 'UTC_Time' to datetime64, assuming it's in nanoseconds
    ds['time'] = pd.to_datetime(ds['Time_Unix'], unit='ns')

    # Renaming variables according to your specification
    variable_mapping = {
        'Temperature': 'temperature',
        'Wind_speed_10m_mast1': 'wind_speed_mast1',
        'Wind_speed_10m_mast2': 'wind_speed_mast2',
        'Wind_direction_10m_mast1': 'wind_direction_mast1',
        'Wind_direction_10m_mast2': 'wind_direction_mast2',
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
