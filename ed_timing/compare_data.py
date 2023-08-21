import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Read all CSV files from the 'fixed' directory
csv_files = [f for f in os.listdir('fixed') if f.endswith('.csv')]

# 2. Load all the data from these CSV files into a single pandas DataFrame
all_data = []
for file in csv_files:
    file_path = os.path.join('fixed', file)
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
hb1 = axarr[0].hexbin(valid_rho, valid_ed, gridsize=250, cmap='viridis', bins='log', vmin=1, vmax=100)
cb1 = plt.colorbar(hb1, ax=axarr[0], label='Density')
axarr[0].set_facecolor('#3e0751')
axarr[0].set_xlim((0, 0.4))
axarr[0].set_ylim((0, 0.4))
axarr[0].plot([0, 0.4], [0, 0.4], linewidth=2, color='black', linestyle='--')
axarr[0].set_title(f'Old Effective Density (Corr: {correlation_ed:.3f})')
axarr[0].set_xlabel('Rho (g cm-3)')
axarr[0].set_ylabel('eD (g cm-3)')

# Heatmap scatter for the second dataset
hb2 = axarr[1].hexbin(valid_rho, valid_ed_fixed, gridsize=250, cmap='viridis', bins='log', vmin=1, vmax=100)
cb2 = plt.colorbar(hb2, ax=axarr[1], label='Density')
axarr[1].set_facecolor('#3e0751')
axarr[1].set_xlim((0, 0.4))
axarr[1].set_ylim((0, 0.4))
axarr[1].plot([0, 0.4], [0, 0.4], linewidth=2, color='black', linestyle='--')
axarr[1].set_title(f'Corrected Effective Density (Corr: {correlation_adj_ed:.3f})')
axarr[1].set_xlabel('Rho (g cm-3)')
axarr[1].set_ylabel('eD (g cm-3)')
plt.tight_layout()
plt.show()

