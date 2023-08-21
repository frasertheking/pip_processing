import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

MAIN_PATH = '/data2/fking/s03/converted/'
LAST_PATH = '/netCDF/adjusted_edensity_lwe_rate/'
subfolders = ['2015_MQT', '2016_MQT', '2017_MQT', '2018_MQT', '2019_MQT', '2020_MQT', '2021_MQT', '2022_MQT']

# 1. Read all CSV files from the combinations of directories
all_data = []

for subfolder in subfolders:
    dir_path = MAIN_PATH+subfolder+LAST_PATH
    print(dir_path)
    csv_files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
    
    for file in csv_files:
        file_path = os.path.join(dir_path, file)
        df = pd.read_csv(file_path)

        # Drop rows where either variable has NaN or a value <= 0
        df = df.dropna(subset=['rho', 'ed', 'adj_ed'])
        df = df[(df['rho'] > 0) & (df['ed'] > 0) & (df['adj_ed'] > 0)]
        
        all_data.append(df)

merged_data = pd.concat(all_data, ignore_index=True)

valid_rho = merged_data['rho']
valid_ed = merged_data['ed']
valid_ed_fixed = merged_data['adj_ed']
correlation_ed = merged_data['rho'].corr(merged_data['ed'])
correlation_adj_ed = merged_data['rho'].corr(merged_data['adj_ed'])

# Create a 1x2 subplot layout
fig, axarr = plt.subplots(1, 2, figsize=(16,8))

# Heatmap scatter for the first dataset
hb1, xedges, yedges, im1 = axarr[0].hist2d(valid_rho, valid_ed, bins=100, cmap='viridis', cmin=1)
cb1 = plt.colorbar(im1, ax=axarr[0], label='Density')
axarr[0].set_facecolor('#3e0751')
axarr[0].set_xlim((0, 1))
axarr[0].set_ylim((0, 1))
axarr[0].plot([0, 1], [0, 1], linewidth=2, color='black', linestyle='--')
axarr[0].set_title(f'Old Effective Density (Corr: {correlation_ed:.3f})')
axarr[0].set_xlabel('Rho (g cm-3)')
axarr[0].set_ylabel('eD (g cm-3)')

# Heatmap scatter for the second dataset
hb2, xedges, yedges, im2 = axarr[1].hist2d(valid_rho, valid_ed_fixed, bins=100, cmap='viridis', cmin=1)
cb2 = plt.colorbar(im2, ax=axarr[1], label='Density')
axarr[1].set_facecolor('#3e0751')
axarr[1].set_xlim((0, 1))
axarr[1].set_ylim((0, 1))
axarr[1].plot([0, 1], [0, 1], linewidth=2, color='black', linestyle='--')
axarr[1].set_title(f'Corrected Effective Density (Corr: {correlation_adj_ed:.3f})')
axarr[1].set_xlabel('Rho (g cm-3)')
axarr[1].set_ylabel('eD (g cm-3)')

plt.tight_layout()
plt.savefig('comparison.png')

