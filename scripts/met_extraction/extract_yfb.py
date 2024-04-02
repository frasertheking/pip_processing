import os
from datetime import datetime
from netCDF4 import Dataset, date2num
import glob

LAT=63.74
LON=-68.51
SITE="Iqaluit, Nunavut"

input_directory = '/Users/fraserking/Development/pip_processing/data/MET/YFB' 
output_directory = '/Users/fraserking/Desktop/YFB_OUT'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

def parse_yfb_line(line):
    date_str, time_str, _id, data_str = line.split(maxsplit=3)
    data_parts = data_str.split(',')
    data_dict = {part.split('=')[0]: part.split('=')[1] for part in data_parts if '=' in part}
    datetime_obj = datetime.strptime(f"{date_str} {time_str}", "%Y/%m/%d %H:%M:%S")
    return datetime_obj, data_dict

def create_netcdf(file_data, filename, date_str):
    with Dataset(filename, 'w', format='NETCDF4') as nc:
        nc.Comment1 = f"Data was acquired at the {SITE} site (Lat: {LAT}, Lon: {LON})."
        nc.Comment2 = f"1 minute temporal resolution."
        nc.createDimension('time', None)
        time_var = nc.createVariable('time', 'f8', ('time',))
        time_var.units = f'minutes since {date_str} 00:00:00'
        time_var.calendar = 'gregorian'
        
        lat_var = nc.createVariable('lat', 'f8')
        lon_var = nc.createVariable('lon', 'f8')
        temp_var = nc.createVariable('temperature', 'f4', ('time',), fill_value=-9999.0)
        press_var = nc.createVariable('pressure', 'f4', ('time',), fill_value=-9999.0)
        rh_var = nc.createVariable('relative_humidity', 'f4', ('time',), fill_value=-9999.0)
        ws_var = nc.createVariable('wind_speed', 'f4', ('time',), fill_value=-9999.0)
        wd_var = nc.createVariable('wind_direction', 'f4', ('time',), fill_value=-9999.0)
        
        temp_var.units = 'degrees C'
        press_var.units = 'hPa'
        rh_var.units = 'percent'
        ws_var.units = 'm s-1'
        wd_var.units = 'degrees'

        temp_var.standard_name = "surface_temperature"
        temp_var.long_name = "Surface Temperature"
        press_var.standard_name = "surface_air_pressure"
        press_var.long_name = "Surface Air Pressure"
        rh_var.standard_name = "relative_humidity"
        rh_var.long_name = "Relative Humidity"
        ws_var.standard_name = "wind_speed"
        ws_var.long_name = "Wind Speed"
        wd_var.standard_name = "wind_from_direction"
        wd_var.long_name = "Wind From Direction"
        
        base_datetime = datetime.strptime(date_str, "%Y%m%d")
        times = [(datetime_obj - base_datetime).total_seconds() / 60 for datetime_obj, _, _, _, _, _ in file_data]
        lat_var[:] = LAT
        lon_var[:] = LON
        time_var[:] = times
        times, temps, press, rhs, wss, wds = zip(*file_data)
        temp_var[:] = temps
        press_var[:] = press
        rh_var[:] = rhs
        ws_var[:] = wss
        wd_var[:] = wds

def safe_float_conversion(value):
    import re
    match = re.match(r"([-+]?\d*\.\d+|\d+)", value)
    return float(match.group(0)) if match else None

for filepath in glob.glob(os.path.join(input_directory, '*.YFB')):
    file_data = []
    with open(filepath, 'r') as file:
        for line in file:
            datetime_obj, data_dict = parse_yfb_line(line)
            try:
                temperature = safe_float_conversion(data_dict['Ta'].rstrip('C'))
                pressure = safe_float_conversion(data_dict['Pa'].rstrip('B')) * 1000
                relative_humidity = safe_float_conversion(data_dict['Ua'].rstrip('P'))
                wind_speed = safe_float_conversion(data_dict['Sm'].rstrip('M#'))
                wind_direction = safe_float_conversion(data_dict['Dm'].rstrip('D'))
                if None not in [temperature, pressure, relative_humidity, wind_speed, wind_direction]:
                    file_data.append((datetime_obj, temperature, pressure, relative_humidity, wind_speed, wind_direction))
            except KeyError:
                continue
    
    base_name = os.path.basename(filepath).replace('.YFB', '')
    output_filename = os.path.join(output_directory, f"20{base_name[7:]}_met.nc")
    date_str = file_data[0][0].strftime("%Y%m%d")
    create_netcdf(file_data, output_filename, date_str)
    print(f"Created netCDF file: {output_filename}")
