import os
import xarray as xr

LAT = 69.0579
LON = -152.8628
SITE = "North Slope, Alaska"

input_folder_path = '/Users/fraserking/Development/pip_processing/data/MET/NSA/'  
output_folder_path = '/Users/fraserking/Desktop/NSA_OUT/'  

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
            
            extracted_variables = ds_renamed[list(variable_mapping.values())]
            extracted_variables['lat'] = xr.DataArray(data=LAT, dims=())
            extracted_variables['lon'] = xr.DataArray( data=LON, dims=())
            extracted_variables.attrs['Comment1'] = f"Data was acquired at the {SITE} site (Lat: {LAT}, Lon: {LON})"

            extracted_variables.to_netcdf(output_file_path)

            print(f"Successfully processed {filename} and saved to {output_file_name}")
except Exception as e:
    print(f"An error occurred: {e}")