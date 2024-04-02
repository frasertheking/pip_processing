import os
import xarray as xr
import pandas as pd

LAT=67.84
LON=20.41
SITE="Kiruna, Sweden"

input_file_path = '/Users/fraserking/Development/pip_processing/data/MET/KIS/Kiruna_Sweden_met.nc'
output_folder_base_path = '/Users/fraserking/Desktop/KIS_OUT/'

try:
    ds = xr.open_dataset(input_file_path)
    ds['time'] = pd.to_datetime(ds['Time_Unix'], unit='ns')

    variable_mapping = {
        'Temperature': 'temperature',
        'Pressure': 'pressure',
        'Relative_Humidity': 'relative_humidity',
        'Wind_Speed': 'wind_speed',
        'Wind_Direction': 'wind_direction',
    }
    
    ds_renamed = ds.rename(variable_mapping)

    attrs_to_assign = {
        'temperature': {
            'units': 'degrees C',
            'standard_name': 'surface_temperature',
            'long_name': 'Surface Temperature'
        },
        'pressure': {
            'units': 'hPa',
            'standard_name': 'surface_air_pressure',
            'long_name': 'Surface Air Pressure'
        },
        'relative_humidity': {
            'units': 'percent',
            'standard_name': 'relative_humidity',
            'long_name': 'Relative Humidity'
        },
        'wind_speed': {
            'units': 'm s-1',
            'standard_name': 'wind_speed',
            'long_name': 'Wind Speed'
        },
        'wind_direction': {
            'units': 'degrees',
            'standard_name': 'wind_from_direction',
            'long_name': 'Wind From Direction'
        }
    }
    
    for var_name, attrs in attrs_to_assign.items():
        ds_renamed[var_name].attrs.update(attrs)
    
    ds_renamed = ds_renamed.assign(lat=xr.DataArray(LAT, dims=()), lon=xr.DataArray(LON, dims=()))
    ds_renamed.attrs['Comment1'] = f"Data was acquired at the {SITE} site (Lat: {LAT}, Lon: {LON})"
    ds_renamed.attrs['Comment2'] = f"1 minute temporal resolution."
    
    filtered_variables = list(variable_mapping.values()) + ['lat', 'lon', 'time']
    ds_filtered = ds_renamed[filtered_variables]
    
    for group, group_ds in ds_filtered.resample(time='D'):
        if group_ds.sizes['time'] == 0:
            continue
            
        group_date = pd.to_datetime(str(group)).date()
        
        date_str = group_date.strftime('%Y%m%d')
        output_file_path = os.path.join(output_folder_base_path, f"{date_str}_met.nc")
        
        group_ds.to_netcdf(output_file_path)
        print(f"Saved data for {date_str} to {output_file_path}")

except Exception as e:
    print(f"An error occurred: {e}")
