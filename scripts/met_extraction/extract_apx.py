import os
import numpy as np
from netCDF4 import Dataset, num2date, date2num
from datetime import datetime, timedelta

LAT=44.9079
LON=-84.7187
SITE="Gaylord, Michigan"

input_file_1 = '/Users/fraserking/Development/pip_processing/data/MET/APX/CRNS0101-05-2022-MI_Gaylord_9_SSW.txt'
input_file_2 = '/Users/fraserking/Development/pip_processing/data/MET/APX/CRNS0101-05-2023-MI_Gaylord_9_SSW.txt'
output_folder_base_path = '/Users/fraserking/Desktop/APX_OUT/'

def parse_line(line):
    parts = line.split()
    utc_date = parts[1]
    utc_time = parts[2]
    latitude = float(parts[7])
    longitude = float(parts[6])
    air_temperature = float(parts[8])
    relative_humidity = float(parts[15])
    wind_speed = float(parts[21])
    return utc_date, utc_time, latitude, longitude, air_temperature, relative_humidity, wind_speed

def read_txt_file(filename):
    data_by_date = {}
    with open(filename, 'r') as f:
        for line in f:
            utc_date, utc_time, lat, lon, temp, rh, ws = parse_line(line)
            if utc_date not in data_by_date:
                data_by_date[utc_date] = {'times': [], 'lat': lat, 'lon': lon,
                                          'temperature': [], 'relative_humidity': [], 'wind_speed': []}
            time_obj = datetime.strptime(f'{utc_date}{utc_time}', '%Y%m%d%H%M')
            data_by_date[utc_date]['times'].append(time_obj)
            data_by_date[utc_date]['temperature'].append(temp)
            data_by_date[utc_date]['relative_humidity'].append(rh)
            data_by_date[utc_date]['wind_speed'].append(ws)
    return data_by_date

def create_netcdf(data, date_str, lat, lon, output_folder_base_path, site):
    filename = os.path.join(output_folder_base_path, f'{date_str}_met.nc')
    with Dataset(filename, 'w', format='NETCDF4') as nc:
        nc.Comment1 = f"Data was acquired at the {site} site (Lat: {lat}, Lon: {lon})"
        
        nc.createDimension('time', None)
        time_var = nc.createVariable('time', 'f8', ('time',))
        time_var.units = f'minutes since {date_str} 00:00:00'
        time_var.calendar = 'gregorian'
        
        lat_var = nc.createVariable('lat', 'f8')
        lon_var = nc.createVariable('lon', 'f8')
        temp_var = nc.createVariable('temperature', 'f4', ('time',), fill_value=-9999.0)
        rh_var = nc.createVariable('relative_humidity', 'f4', ('time',), fill_value=-9999.0)
        ws_var = nc.createVariable('wind_speed', 'f4', ('time',), fill_value=-9999.0)
        
        temp_var.units = 'degrees C'
        rh_var.units = 'percent'
        ws_var.units = 'm/s'

        lat_var[:] = lat
        lon_var[:] = lon
        start_of_day = datetime.strptime(date_str, '%Y%m%d')
        time_var[:] = [(time - start_of_day).total_seconds() / 60 for time in data['times']]
        temp_var[:] = data['temperature']
        rh_var[:] = data['relative_humidity']
        ws_var[:] = data['wind_speed']
        
        print(f'Created {filename}')

if not os.path.exists(output_folder_base_path):
    os.makedirs(output_folder_base_path)

file_paths = [input_file_1, input_file_2]
for path in file_paths:
    data_by_date = read_txt_file(path)
    for date_str, data in data_by_date.items():
        create_netcdf(data, date_str, data['lat'], data['lon'], output_folder_base_path, SITE)
