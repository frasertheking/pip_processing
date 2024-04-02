import os
import xarray as xr

LAT = 69.0579
LON = -152.8628
SITE = "North Slope, Alaska"

input_folder_path = '/data/jshates/northslope/met/'  
output_folder_path = '/data2/fking/s03/met_converted/NSA/'  

try:
    for filename in os.listdir(input_folder_path):
        if filename.endswith('.cdf'):
            date = filename[12:20]
            input_file_path = os.path.join(input_folder_path, filename)
            output_file_name = f"{date}_met.nc"
            output_file_path = os.path.join(output_folder_path, output_file_name)
            
            ds = xr.open_dataset(input_file_path)

            variable_mapping = {
                'temp_mean': 'temperature',
                'atmos_pressure': 'pressure',
                'rh_mean': 'relative_humidity',
                'wspd_arith_mean': 'wind_speed',
                'wdir_vec_mean': 'wind_direction'
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

            extracted_variables = ds_renamed[list(variable_mapping.values())]
            extracted_variables['lat'] = xr.DataArray(data=LAT, dims=())
            extracted_variables['lon'] = xr.DataArray( data=LON, dims=())
            extracted_variables.attrs['Comment1'] = f"Data was acquired at the {SITE} site (Lat: {LAT}, Lon: {LON})"
            extracted_variables.attrs['Comment2'] = f"1 minute temporal resolution."

            extracted_variables.to_netcdf(output_file_path)

            print(f"Successfully processed {filename} and saved to {output_file_name}")
except Exception as e:
    print(f"An error occurred: {e}")