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
extent = 1

# Histplot with KDE for the first dataset
sns.histplot(x=valid_rho, y=valid_ed, bins=250, ax=axarr[0], cmap='viridis', kde=True)
axarr[0].set_facecolor('#3e0751')
axarr[0].set_xlim((0, extent))
axarr[0].set_ylim((0, extent))
axarr[0].plot([0, extent], [0, extent], linewidth=2, color='black', linestyle='--')
axarr[0].set_title(f'Old Effective Density (Corr: {correlation_ed:.3f})')
axarr[0].set_xlabel('Rho (g cm-3)')
axarr[0].set_ylabel('eD (g cm-3)')

# Histplot with KDE for the second dataset
sns.histplot(x=valid_rho, y=valid_ed_fixed, bins=250, ax=axarr[1], cmap='viridis', kde=True)
axarr[1].set_facecolor('#3e0751')
axarr[1].set_xlim((0, extent))
axarr[1].set_ylim((0, extent))
axarr[1].plot([0, extent], [0, extent], linewidth=2, color='black', linestyle='--')
axarr[1].set_title(f'Corrected Effective Density (Corr: {correlation_adj_ed:.3f})')
axarr[1].set_xlabel('Rho (g cm-3)')
axarr[1].set_ylabel('eD (g cm-3)')

plt.tight_layout()
plt.savefig('comparison.png')

# # Create a 1x2 subplot layout
# fig, axarr = plt.subplots(1, 2, figsize=(16,8))

# extent = 1

# # Heatmap scatter for the first dataset
# hb1 = axarr[0].hexbin(valid_rho, valid_ed, gridsize=250, cmap='viridis')#, bins='log')#, vmin=1, vmax=100)
# cb1 = plt.colorbar(hb1, ax=axarr[0], label='Density')
# axarr[0].set_facecolor('#3e0751')
# axarr[0].set_xlim((0, extent))
# axarr[0].set_ylim((0, extent))
# axarr[0].plot([0, extent], [0, extent], linewidth=2, color='black', linestyle='--')
# axarr[0].set_title(f'Old Effective Density (Corr: {correlation_ed:.3f})')
# axarr[0].set_xlabel('Rho (g cm-3)')
# axarr[0].set_ylabel('eD (g cm-3)')

# # Heatmap scatter for the second dataset
# hb2 = axarr[1].hexbin(valid_rho, valid_ed_fixed, gridsize=250, cmap='viridis')#, bins='log')#, vmin=1, vmax=100)
# cb2 = plt.colorbar(hb2, ax=axarr[1], label='Density')
# axarr[1].set_facecolor('#3e0751')
# axarr[1].set_xlim((0, extent))
# axarr[1].set_ylim((0, extent))
# axarr[1].plot([0, extent], [0, extent], linewidth=2, color='black', linestyle='--')
# axarr[1].set_title(f'Corrected Effective Density (Corr: {correlation_adj_ed:.3f})')
# axarr[1].set_xlabel('Rho (g cm-3)')
# axarr[1].set_ylabel('eD (g cm-3)')
# plt.tight_layout()
# plt.savefig('comparison.png')

