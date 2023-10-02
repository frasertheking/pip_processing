## Check NSA
import os, sys
import xarray as xr
import numpy as np
import warnings
import matplotlib.pyplot as plt
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')
plt.rcParams.update({'font.size': 15})

def check_NSA():
    base_folder = '/Users/fraserking/Development/pip_processing/data/converted'
    subdirs = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]
    matching_subdirs = [d for d in subdirs if 'NSA' in d]
    bad_nsa_days = []

    for subdir in matching_subdirs:
        full_path = os.path.join(base_folder, subdir)
        print(f"Processing subdirectory: {full_path}")

        netcdf_path = os.path.join(full_path, 'netCDF/particle_size_distributions')
        if os.path.exists(netcdf_path):
            all_files = os.listdir(netcdf_path)
            nc_files = [f for f in all_files if f.endswith('.nc')]
            
            for nc_file in nc_files:
                nc_file_path = os.path.join(netcdf_path, nc_file)
                ds_pip = xr.open_dataset(nc_file_path)   
                dsd = ds_pip['psd'].values
                if np.nanmean(dsd.T[1]) > 2500:
                    bad_nsa_days.append(nc_file[:11])
                    
    return bad_nsa_days

def delete_files(bad_file_strings):

    # List of root paths where the bad files could be located
    root_paths = [
        '/Users/fraserking/Development/pip_processing/data/converted/2018_NSA',
        '/Users/fraserking/Development/pip_processing/data/converted/2019_NSA',
        '/Users/fraserking/Development/pip_processing/data/converted/2020_NSA',
        '/Users/fraserking/Development/pip_processing/data/converted/2021_NSA',
        '/Users/fraserking/Development/pip_processing/data/converted/2022_NSA',
        '/Users/fraserking/Development/pip_processing/data/converted/2023_NSA'
    ]

    # Loop through each root path
    for root_path in root_paths:
        # Check if root path exists
        if not os.path.exists(root_path):
            print(f"Path {root_path} does not exist.")
            continue
        
        # Recursively walk through all subfolders
        for dirpath, _, filenames in os.walk(root_path):
            # Loop through each file in the current directory
            for filename in filenames:
                # Loop through each bad file string
                for bad_string in bad_file_strings:
                    if bad_string in filename:
                        # Construct the full path to the file
                        full_file_path = os.path.join(dirpath, filename)
                        
                        # Delete the file
                        print(f"Deleting {full_file_path}...")
                        os.remove(full_file_path)



bad_nsa_days = check_NSA()
print(bad_nsa_days)
delete_files(bad_nsa_days)
print("all done")
