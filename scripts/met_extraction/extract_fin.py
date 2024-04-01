import os
import xarray as xr

LAT = 61.845
LON = 24.287
SITE = "Hyytiälä Forestry Field Station"

input_folder_path = '/Users/fraserking/Development/pip_processing/data/MET/FIN/'  
output_folder_path = '/Users/fraserking/Desktop/FIN_OUT/'  

try:
    for filename in os.listdir(input_folder_path):
        if filename.endswith('.nc'):
            date = filename[:8]
            input_file_path = os.path.join(input_folder_path, filename)
            output_file_name = f"{date}_met.nc"
            output_file_path = os.path.join(output_folder_path, output_file_name)
            
            ds = xr.open_dataset(input_file_path)
            extracted_variables = ds[['temperature', 'pressure', 'relative_humidity', 'wind_speed', 'wind_direction']]
            extracted_variables['lat'] = xr.DataArray(data=LAT, dims=())
            extracted_variables['lon'] = xr.DataArray(data=LON, dims=())
            extracted_variables.attrs['Comment1'] = f"Data was acquired at the {SITE} site (Lat: {LAT}, Lon: {LON})"
            extracted_variables.to_netcdf(output_file_path)

            print(f"Successfully processed {filename} and saved to {output_file_name}")
except Exception as e:
    print(f"An error occurred: {e}")
