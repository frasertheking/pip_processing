import sys,os
import pandas as pd
import numpy as np
import xarray as xr
from scipy.stats import pearsonr
import warnings
import argparse
warnings.filterwarnings("ignore")

def calculate_correlation(a, b):
    return np.corrcoef(a, b)[0, 1]

def best_align_slice(ed_slice, rho_slice, max_nan_prepend=25):
    best_correlation = -np.inf
    best_n = 0
    
    for n in range(max_nan_prepend + 1): # +1 to include the 0 nans case
        aligned_ed_slice = np.concatenate([np.array([np.nan] * n), ed_slice])

        if len(aligned_ed_slice) > len(rho_slice):
            aligned_rho_slice = np.concatenate([rho_slice, np.array([np.nan] * (len(aligned_ed_slice) - len(rho_slice)))])
        else:
            aligned_rho_slice = rho_slice

        valid_ed = aligned_ed_slice[~np.isnan(aligned_rho_slice) & ~np.isnan(aligned_ed_slice)]
        valid_rho = aligned_rho_slice[~np.isnan(aligned_rho_slice) & ~np.isnan(aligned_ed_slice)]
        
        if len(valid_ed) == 0:
            continue
        
        correlation = calculate_correlation(valid_ed, valid_rho)
        if correlation > best_correlation:
            best_correlation = correlation
            best_n = n
            
    return np.array([np.nan] * best_n), np.concatenate([np.array([np.nan] * best_n), ed_slice])

def align_ed_data(ed_data, rho_data, chunk_size=360, max_nan_prepend=60):
    fixed_ed_data = []

    prefix_nans = []
    prefix_indices = []

    i = 0
    while i < len(ed_data):
        ed_slice = ed_data[i:i+chunk_size]
        rho_slice = rho_data[i:i+chunk_size]
        nans, aligned_ed_slice = best_align_slice(ed_slice, rho_slice, max_nan_prepend)

        prefix_nans.append(nans)
        prefix_indices.append(i)

        fixed_ed_data.extend(aligned_ed_slice)
        i += len(aligned_ed_slice)

    return np.asarray(fixed_ed_data)[:1440], prefix_indices, prefix_nans

def fix_timing(rho_path, ed_path, out_path, SIZE=1):
    name = os.path.basename(ed_path)
    print("Fixing " + name + ' eD and NRR values...')

    rho_ds = xr.open_dataset(rho_path)
    ed_ds = xr.open_dataset(ed_path)

    non_zeros_rho = rho_ds['rho'].where(rho_ds['rho'] != 0)
    resampled_rho = non_zeros_rho.resample(time=str(SIZE)+'T').mean('time', skipna=True).values
    rho_data = np.nanmean(resampled_rho, axis=1)

    reshaped_data = ed_ds['ed'].values.reshape(-1, SIZE)
    ed_data = reshaped_data.mean(axis=1)

    reshaped_data_nrr = ed_ds['nrr'].values.reshape(-1, SIZE)
    nrr_data_orig = reshaped_data_nrr.mean(axis=1)
    
    reshaped_data_rr = ed_ds['rr'].values.reshape(-1, SIZE)
    rr_data_orig = reshaped_data_rr.mean(axis=1)

    ed_data = np.clip(ed_data, 0, 1)
    nrr_data_orig = np.clip(nrr_data_orig, 0, None)
    rr_data_orig = np.clip(nrr_data_orig, 0, None)

    fixed_ed_data, pre_i, pre_nan = align_ed_data(ed_data, rho_data)

    valid_rho2 = rho_data[~np.isnan(rho_data) & ~np.isnan(ed_data)]
    valid_ed2 = ed_data[~np.isnan(rho_data) & ~np.isnan(ed_data)]
    valid_ed_fixed = fixed_ed_data[~np.isnan(rho_data) & ~np.isnan(fixed_ed_data)]
    valid_rho_fixed = rho_data[~np.isnan(rho_data) & ~np.isnan(fixed_ed_data)]

    correlation, _ = pearsonr(valid_rho2, valid_ed2)
    correlation2, _ = pearsonr(valid_rho_fixed, valid_ed_fixed)

    for i, index in enumerate(pre_i):
        nans = pre_nan[i]
        nrr_data = np.insert(nrr_data_orig, index, nans)
        rr_data = np.insert(rr_data_orig, index, nans)

    fixed_nrr_data = np.asarray(nrr_data)[:1440]
    fixed_rr_data = np.asarray(rr_data)[:1440]

    if correlation > correlation2:  # edge case where the correction fails
        print("Updated correlation was not improved.. using original values:" + str(correlation) + ' to ' + str(correlation2))
        print("Max & Min Values:" + str(np.nanmax(ed_data)) + ', ' + str(np.nanmin(ed_data)))
        ed_ds['ed_adj'] = xr.DataArray(ed_data, dims='time')
        ed_ds['nrr_adj'] = xr.DataArray(nrr_data_orig, dims='time')
        ed_ds['rr_adj'] = xr.DataArray(rr_data_orig, dims='time')
    else:
        print("Correlation improved from " + str(correlation) + ' to ' + str(correlation2))
        print("Max & Min Values:" + str(np.nanmax(fixed_ed_data)) + ', ' + str(np.nanmin(fixed_ed_data)))
        ed_ds['ed_adj'] = xr.DataArray(fixed_ed_data, dims='time')
        ed_ds['nrr_adj'] = xr.DataArray(fixed_nrr_data, dims='time')
        ed_ds['rr_adj'] = xr.DataArray(fixed_rr_data, dims='time')

    ed_ds['ed_adj'].attrs['units'] = 'g cm-3'
    ed_ds['ed_adj'].attrs['long_name'] = 'Adjusted effective density'
    ed_ds['ed_adj'].attrs['standard_name'] = 'adjusted_effective_density'
    ed_ds['ed_adj'].attrs['missing_value'] = 'NaN'

    ed_ds['nrr_adj'].attrs['units'] = 'mm hr-1'
    ed_ds['nrr_adj'].attrs['long_name'] = 'Adjusted non-rain rate'
    ed_ds['nrr_adj'].attrs['standard_name'] = 'adjusted_non_rainfall_rate'
    ed_ds['nrr_adj'].attrs['missing_value'] = 'NaN'

    ed_ds['rr_adj'].attrs['units'] = 'mm hr-1'
    ed_ds['rr_adj'].attrs['long_name'] = 'Adjusted rain rate'
    ed_ds['rr_adj'].attrs['standard_name'] = 'adjusted_rainfall_rate'
    ed_ds['rr_adj'].attrs['missing_value'] = 'NaN'

    encoding = {var: {'dtype': 'float64'} for var in ed_ds.data_vars}
    ed_ds.to_netcdf(out_path + '/' + name, encoding=encoding)
    print("File saved!")

    df = pd.DataFrame(data={'rho': rho_data, 'ed': ed_data, 'adj_ed': fixed_ed_data})
    df.to_csv(out_path + '/' + name + '.csv')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix timing for given rho and ed files.")
    parser.add_argument("rho_path", help="Path to the rho file.")
    parser.add_argument("ed_path", help="Path to the ed file.")
    parser.add_argument("out_path", help="Output path.")
    parser.add_argument("--SIZE", type=int, default=1, help="Optional SIZE argument. Defaults to 1 if not provided.")
    
    args = parser.parse_args()

    fix_timing(args.rho_path, args.ed_path, args.out_path, args.SIZE)





