import os
import xarray as xr
import numpy as np


def extend_and_save(filepath, data_var_name):
    ds = xr.open_dataset(filepath)
    
    # Check if the length of the time dimension is less than 1440
    if len(ds['time']) < 1440:
        # Create a time range from 0 to 1439
        full_time_range = np.arange(0, 1440)

        # Extend the dataset
        ds_extended = ds.reindex(time=full_time_range)

        # Print out dataset details for debugging
        print(ds_extended)
        for var in ds_extended.variables:
            print(f"{var}: {ds_extended[var].dtype}")

        # Rename the original file
        original_filepath = filepath.replace('.nc', '_original.nc')
        os.rename(filepath, original_filepath)
        
        try:
            ds_extended.attrs = {}
            print(ds_extended)
            ds_extended.to_netcdf(filepath, encoding={})
        except Exception as e:
            print(f"Error while saving {filepath}: {e}")

    ds.close()

def process_directory(directory):
    file_ending_map = {
        '_rho_Plots_D_minute.nc': 'rho',
        '01_dsd.nc': 'psd',
        '_vvd_A.nc': 'vvd'
    }

    # Loop through all subfolders and files in the given directory
    for subdir, _, files in os.walk(directory):
        for file in files:
            # Check if the file ends with one of the specified strings
            for ending, data_var in file_ending_map.items():
                if file.endswith(ending):
                    filepath = os.path.join(subdir, file)
                    extend_and_save(filepath, data_var)

if __name__ == "__main__":
    directory = "/Users/fraserking/Desktop/asd"
    process_directory(directory)
