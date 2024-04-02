from netCDF4 import Dataset, date2num
from datetime import datetime, timedelta
import numpy as np
import os

LAT=37.72067
LON=128.90103
SITE="South Korea, station 2569 (65 m.a.s.l.)"

input_file_1 = '/Users/fraserking/Development/pip_processing/data/MET/ICP/stn2569.txt'
output_folder_base_path = '/Users/fraserking/Desktop/ICP_OUT/'


def parse_line(line):
    parts = line.split()
    year = int(parts[0])
    doy = int(parts[1])
    hour = int(parts[2])
    minute = int(parts[3])
    wind_direction = float(parts[4])
    wind_speed = float(parts[5])
    temperature = float(parts[6])
    pressure = float(parts[9])
    relative_humidity = float(parts[8])
    date_time = datetime(year, 1, 1, hour, minute) + timedelta(days=doy - 1)
    return date_time, wind_direction, wind_speed, temperature, pressure, relative_humidity

def read_txt_file(filename):
    data_by_date = {}
    with open(filename, 'r') as f:
        for line in f:
            date_time, wind_direction, wind_speed, temp, pressure, rh = parse_line(line)
            date_str = date_time.strftime('%Y%m%d')
            if date_str not in data_by_date:
                data_by_date[date_str] = {'times': [], 'wind_direction': [], 'wind_speed': [],
                                          'temperature': [], 'pressure': [], 'relative_humidity': []}
            data_by_date[date_str]['times'].append(date_time)
            data_by_date[date_str]['wind_direction'].append(wind_direction)
            data_by_date[date_str]['wind_speed'].append(wind_speed)
            data_by_date[date_str]['temperature'].append(temp)
            data_by_date[date_str]['pressure'].append(pressure)
            data_by_date[date_str]['relative_humidity'].append(rh)
    return data_by_date

def create_netcdf(data, date_str, output_folder_base_path, site):
    filename = os.path.join(output_folder_base_path, f'{date_str}_met.nc')
    with Dataset(filename, 'w', format='NETCDF4') as nc:
        nc.site_info = f"Data was acquired at the {site} site (Lat: {LAT}, Lon: {LON})."
        nc.Comment2 = f"1 minute temporal resolution."
        
        nc.createDimension('time', None)
        time_var = nc.createVariable('time', 'f8', ('time',))
        time_var.units = f'minutes since {date_str} 00:00:00'
        time_var.calendar = 'gregorian'
        
        lat_var = nc.createVariable('lat', 'f8')
        lon_var = nc.createVariable('lon', 'f8')
        wd_var = nc.createVariable('wind_direction', 'f4', ('time',), fill_value=-9999.0)
        ws_var = nc.createVariable('wind_speed', 'f4', ('time',), fill_value=-9999.0)
        temp_var = nc.createVariable('temperature', 'f4', ('time',), fill_value=-9999.0)
        press_var = nc.createVariable('pressure', 'f4', ('time',), fill_value=-9999.0)
        rh_var = nc.createVariable('relative_humidity', 'f4', ('time',), fill_value=-9999.0)
        
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
        
        lat_var[:] = LAT
        lon_var[:] = LON
        start_of_day = datetime.strptime(date_str, '%Y%m%d')
        time_var[:] = [(time - start_of_day).total_seconds() / 60 for time in data['times']]
        wd_var[:] = data['wind_direction']
        ws_var[:] = data['wind_speed']
        temp_var[:] = data['temperature']
        press_var[:] = data['pressure']
        rh_var[:] = data['relative_humidity']
        
        print(f'Created {filename}')


if not os.path.exists(output_folder_base_path):
    os.makedirs(output_folder_base_path)

file_paths = [input_file_1]
for path in file_paths:
    data_by_date = read_txt_file(path)
    for date_str, data in data_by_date.items():
        create_netcdf(data, date_str, output_folder_base_path, SITE)