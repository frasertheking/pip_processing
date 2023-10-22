import os
import xarray as xr

def check_time_steps(filepath):
    try:
        with xr.open_dataset(filepath) as ds:
            if len(ds['time']) < 1440:
                print(filepath)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def process_directory(directory):
    file_endings = [
        '_rho_Plots_D_minute.nc',
        '01_dsd.nc',
        '_vvd_A.nc'
    ]

    # Loop through all subfolders and files in the given directory
    for subdir, _, files in os.walk(directory):
        for file in files:
            # Check if the file ends with one of the specified strings
            for ending in file_endings:
                if file.endswith(ending):
                    filepath = os.path.join(subdir, file)
                    check_time_steps(filepath)

if __name__ == "__main__":
    process_directory('/data2/fking/s03/converted/2022_MQT/')
