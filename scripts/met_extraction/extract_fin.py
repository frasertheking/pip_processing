import os
import xarray as xr

LAT = 61.845
LON = 24.287
SITE = "Hyytiälä Forestry Field Station"

input_folder_path = '/data2/fking/s03/data/Finland/'  
output_folder_path = '/data2/fking/s03/met_converted/FIN/'  

variable_attrs = {
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

try:
    for filename in os.listdir(input_folder_path):
        if filename.endswith('.nc'):
            date = filename[:8]
            input_file_path = os.path.join(input_folder_path, filename)
            output_file_name = f"{date}_met.nc"
            output_file_path = os.path.join(output_folder_path, output_file_name)
            
            ds = xr.open_dataset(input_file_path)
            
            variables_to_extract = [var for var in ['temperature', 'pressure', 'relative_humidity', 'wind_speed', 'wind_direction'] if var in ds.variables]
            extracted_variables = ds[variables_to_extract]
            
            if 'temperature' in extracted_variables:
                temp_values = extracted_variables['temperature'].values - 273.15
                extracted_variables['temperature'].values = temp_values
                
            for var in extracted_variables.variables:
                if var in variable_attrs:
                    extracted_variables[var].attrs.update(variable_attrs[var])

            extracted_variables['lat'] = xr.DataArray(data=LAT, dims=())
            extracted_variables['lon'] = xr.DataArray(data=LON, dims=())
            extracted_variables.attrs['Comment1'] = f"Data was acquired at the {SITE} site (Lat: {LAT}, Lon: {LON})"
            extracted_variables.attrs['Comment2'] = f"3 second temporal resolution."
            extracted_variables.to_netcdf(output_file_path)

            print(f"Successfully processed {filename} and saved to {output_file_name}")
except Exception as e:
    print(f"An error occurred: {e}")
