import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize 
from scipy.interpolate import interpn
from matplotlib.colors import LogNorm

MAIN_PATH = '/data2/fking/s03/converted/'
LAST_PATH = '/netCDF/adjusted_edensity_lwe_rate/'
subfolders = ['2015_MQT', '2016_MQT', '2017_MQT', '2018_MQT', '2019_MQT', '2020_MQT', '2021_MQT', '2022_MQT']

CUT = 0.4

# 1. Read all CSV files from the combinations of directories
all_data1 = []
all_data2 = []
all_data3 = []

for subfolder in subfolders:
    dir_path = MAIN_PATH+subfolder+LAST_PATH
    print(dir_path)
    csv_files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
    
    for file in csv_files:
        file_path = os.path.join(dir_path, file)
        df = pd.read_csv(file_path)

        # Drop rows where either variable has NaN or a value <= 0
        df = df.dropna(subset=['rho', 'ed', 'adj_ed'])
        df1 = df[['rho', 'ed']]
        df2 = df[['rho', 'adj_ed']]
        df3 = df[['rho', 'ed', 'adj_ed']]
        df1 = df1[(df1['rho'] > 0) & (df1['ed'] > 0)]
        df1 = df1[(df1['rho'] <= CUT) & (df1['ed'] <= CUT)]
        df2 = df2[(df2['rho'] > 0) & (df2['adj_ed'] > 0)]
        df2 = df2[(df2['rho'] <= CUT) & (df2['adj_ed'] <= CUT)]
        df3 = df3[(df3['rho'] > 0) & (df3['ed'] > 0) & (df3['adj_ed'] > 0)]
        df3 = df3[(df3['rho'] <= CUT) & (df3['adj_ed'] <= CUT) & (df3['ed'] <= CUT)]
        
        all_data1.append(df1)
        all_data2.append(df2)
        all_data3.append(df3)

merged_data1 = pd.concat(all_data1, ignore_index=True)
merged_data2 = pd.concat(all_data2, ignore_index=True)
merged_data3 = pd.concat(all_data3, ignore_index=True)

valid_rho1 = merged_data1['rho']
valid_ed = merged_data1['ed']
valid_rho2 = merged_data2['rho']
valid_ed_fixed = merged_data2['adj_ed']
correlation_ed = merged_data1['rho'].corr(merged_data1['ed'])
correlation_adj_ed = merged_data2['rho'].corr(merged_data2['adj_ed'])


fig, axs = plt.subplots(1, 2, figsize=(16, 8))
H1, xedges1, yedges1 = np.histogram2d(merged_data1["ed"], merged_data1["rho"], bins=200)
axs[0].pcolormesh(xedges1, yedges1, H1.T, cmap='viridis', norm=LogNorm(vmin=5, vmax=250))
axs[0].set_title(f'Old Effective Density (Corr: {correlation_ed:.3f})')
axs[0].plot([0, CUT], [0,  CUT], linewidth=2, color='black', linestyle='--')
axs[0].set_facecolor('#3e0751')
axs[0].set_xlim((0, CUT))
axs[0].set_ylim((0, CUT))
H2, xedges2, yedges2 = np.histogram2d(merged_data2["adj_ed"], merged_data2["rho"], bins=200)
axs[1].pcolormesh(xedges2, yedges2, H2.T, cmap='viridis', norm=LogNorm(vmin=5, vmax=250))
axs[1].set_title(f'Corrected Effective Density (Corr: {correlation_adj_ed:.3f})')
axs[1].plot([0, CUT], [0,  CUT], linewidth=2, color='black', linestyle='--')
axs[1].set_facecolor('#3e0751')
axs[1].set_xlim((0, CUT))
axs[1].set_ylim((0, CUT))
plt.tight_layout()
plt.savefig('hist.png')
plt.show()

plt.figure(figsize=(10, 6))  # You can adjust the numbers (10, 6) to your desired dimensions
sns.kdeplot(data=merged_data3)
plt.savefig('kdeplot.png')

