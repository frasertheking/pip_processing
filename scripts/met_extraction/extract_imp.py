from netCDF4 import Dataset, date2num
from datetime import datetime, timedelta
import numpy as np
import os

LAT=41.807
LON=-72.294
SITE="UConn"

file_paths = ['/Users/fraserking/Development/pip_processing/data/MET/IMP/AIO_21_22/AIO_202112.dat',
               '/Users/fraserking/Development/pip_processing/data/MET/IMP/AIO_21_22/AIO_202201.dat',
               '/Users/fraserking/Development/pip_processing/data/MET/IMP/AIO_21_22/AIO_202202.dat',
               '/Users/fraserking/Development/pip_processing/data/MET/IMP/AIO_21_22/AIO_202203.dat',
               '/Users/fraserking/Development/pip_processing/data/MET/IMP/AIO_21_22/AIO_202204.dat',
               '/Users/fraserking/Development/pip_processing/data/MET/IMP/AIO_22_23/AIO_GAIL_202212.dat',
               '/Users/fraserking/Development/pip_processing/data/MET/IMP/AIO_22_23/AIO_GAIL_202301.dat',
               '/Users/fraserking/Development/pip_processing/data/MET/IMP/AIO_22_23/AIO_GAIL_202302.dat',
               '/Users/fraserking/Development/pip_processing/data/MET/IMP/AIO_22_23/AIO_GAIL_202303.dat',
               '/Users/fraserking/Development/pip_processing/data/MET/IMP/AIO_22_23/AIO_GAIL_202304.dat']
output_folder_base_path = '/Users/fraserking/Desktop/IMP_OUT/'

def parse_line(line):
    parts = line.strip().split()
    # Basic checks remain unchanged
    year = int(parts[1].split('+')[1].rstrip('.'))
    doy = int(parts[2].split('+')[1].rstrip('.'))
    hour = int(parts[3].split('+')[1].rstrip('.')) // 100
    minute = int(parts[3].split('+')[1].rstrip('.')) % 100
    wind_speed = float(parts[4].split('+')[1].rstrip('.'))
    wind_direction = float(parts[5].split('+')[1].rstrip('.'))
    temperature = float(parts[7].split('+')[1].rstrip('.'))
    relative_humidity = float(parts[8].split('+')[1].rstrip('.'))
    pressure = float(parts[9].split('+')[1].rstrip('.'))
    
    # Optionally parse the QNH if present
    qnh = float(parts[10].split('+')[1].rstrip('.')) if len(parts) > 10 else None
    
    date_time = datetime(year, 1, 1, hour, minute) + timedelta(days=doy - 1)
    # Include QNH in the returned tuple if needed
    return date_time, wind_direction, wind_speed, temperature, pressure, relative_humidity, qnh


def read_txt_file(filename):
    data_by_date = {}
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            # Attempt to parse the year to ensure we're processing a data line
            try:
                # If this fails, it means we're not on a data line, so we skip
                year_test = int(parts[1].split('+')[1].rstrip('.'))
            except ValueError:
                continue  # Skip this line if year parsing fails
            
            # Proceed with parsing since we have a valid data line
            parsed = parse_line(line)
            date_time, wind_direction, wind_speed, temperature, pressure, rh, qnh = parsed
            date_str = date_time.strftime('%Y%m%d')
            if date_str not in data_by_date:
                data_by_date[date_str] = {
                    'times': [], 'wind_direction': [], 'wind_speed': [],
                    'temperature': [], 'pressure': [], 'relative_humidity': [],
                }
                # Optionally include 'qnh' if you decide to process and store it
                # if qnh is not None:
                #     data_by_date[date_str].setdefault('qnh', []).append(qnh)
            
            data_by_date[date_str]['times'].append(date_time)
            data_by_date[date_str]['wind_direction'].append(wind_direction)
            data_by_date[date_str]['wind_speed'].append(wind_speed)
            data_by_date[date_str]['temperature'].append(temperature)
            data_by_date[date_str]['pressure'].append(pressure)
            data_by_date[date_str]['relative_humidity'].append(rh)
            # # Append 'qnh' only if it exists
            # if qnh is not None:
            #     data_by_date[date_str]['qnh'].append(qnh)
    
    return data_by_date



def create_netcdf(data, date_str, output_folder_base_path, site):
    if not os.path.exists(output_folder_base_path):
        os.makedirs(output_folder_base_path)

    filename = os.path.join(output_folder_base_path, f'{date_str}_met.nc')
    with Dataset(filename, 'w', format='NETCDF4') as nc:
        nc.site_info = f"Data was acquired at the {site} site."

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
        
        wd_var.units = 'degrees'
        ws_var.units = 'm/s'
        temp_var.units = 'degrees C'
        press_var.units = 'mb'
        rh_var.units = 'percent'
        
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

# Main code to handle multiple files
for path in file_paths:
    data_by_date = read_txt_file(path)
    for date_str, data in data_by_date.items():
        create_netcdf(data, date_str, output_folder_base_path, SITE)