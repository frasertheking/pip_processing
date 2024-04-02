import xarray as xr
import os
import numpy as np
import matplotlib.pyplot as plt

def aggregate_data(directory_path, variables):
    aggregated_data = {variable: [] for variable in variables}
    
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if filepath.endswith('.nc'):
            ds = xr.open_dataset(filepath)
            
            for variable in variables:
                if variable in ds.variables:
                    data_with_nans = np.where(ds[variable].values <= -9999, np.nan, ds[variable].values)
                    aggregated_data[variable].append(data_with_nans)
    
    for variable in variables:
        if aggregated_data[variable]:
            aggregated_data[variable] = xr.DataArray(np.concatenate(aggregated_data[variable]))
    
    return aggregated_data

def generate_boxplots(data_by_directory, variables):
    sites = ['FIN', 'MQT', 'YFB', 'NSA', 'OLY', 'KIS', 'ICP', 'IMP']
    variable_names = ['Temperature', 'Relative Humidity', 'Pressure', 'Wind Speed', 'Wind Direction']
    units = ['degrees C', '%', 'hPa', 'm s-1', 'degrees']
    for j, variable in enumerate(variables):
        plt.figure()
        data_to_plot = [np.nan_to_num(data[variable].values.flatten(), nan=np.nan) for data in data_by_directory if variable in data]
        data_to_plot = [data[~np.isnan(data)] for data in data_to_plot if data.size > 0]

        if data_to_plot:
            plt.boxplot(data_to_plot, notch=True, patch_artist=True, showfliers=False)
            plt.title(f'Site MET Comparison for {variable}')
            plt.xticks(range(1, len(data_to_plot) + 1), sites)
            plt.xlabel('Site')
            plt.ylabel(f'{variable_names[j]} ({units[j]})')
            plt.grid(True)            
            plt.savefig(f'/Users/fraserking/Development/pip_processing/images/met/{variable}.png')

def generate_observation_days_barplot(directory_paths):
    num_files = [len([f for f in os.listdir(path) if f.endswith('.nc')]) for path in directory_paths]
    sites = [os.path.basename(path) for path in directory_paths]

    plt.figure()
    plt.grid()
    plt.bar(sites, num_files, color='skyblue')
    plt.title('Number of Days of Observations per Site')
    plt.xlabel('Site')
    plt.ylabel('Days of observations')
    plt.xticks()
    plt.tight_layout() 
    plt.savefig('/Users/fraserking/Development/pip_processing/images/met/observation_days.png')


def main(directory_paths):
    variables = ['temperature', 'relative_humidity', 'pressure', 'wind_speed', 'wind_direction']
    data_by_directory = []
    
    for directory_path in directory_paths:
        aggregated_data = aggregate_data(directory_path, variables)
        data_by_directory.append(aggregated_data)
    
    generate_boxplots(data_by_directory, variables)
    generate_observation_days_barplot(directory_paths)

directory_paths = [
    # '/Users/fraserking/Desktop/MET_OUT/APX',
    '/Users/fraserking/Desktop/MET_OUT/FIN',
    '/Users/fraserking/Desktop/MET_OUT/MQT',
    '/Users/fraserking/Desktop/MET_OUT/YFB',
    '/Users/fraserking/Desktop/MET_OUT/NSA',
    '/Users/fraserking/Desktop/MET_OUT/OLY',
    # '/Users/fraserking/Desktop/MET_OUT/HAK',
    '/Users/fraserking/Desktop/MET_OUT/KIS',
    '/Users/fraserking/Desktop/MET_OUT/ICP',
    '/Users/fraserking/Desktop/MET_OUT/IMP',
]
main(directory_paths)
