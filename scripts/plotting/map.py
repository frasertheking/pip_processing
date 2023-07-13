import os
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
from skimage.io import imread
plt.rcParams.update({'font.size': 35})

site_lats = [46.532, 44.908, 61.845, 69.058, 59.81, 67.84, 37.665]
site_lons = [-87.548, -84.719, 24.287, -152.863, 7.21, 20.41, 128.7]
names = ['MQT', 'APX', 'FIN', 'NSA', 'HAUK', 'KIR', 'KO2']
snowing_minutes = [580949, 45295, 78636, 95268, 24939, 81112, 9843]
colors = ['black', 'r', 'g', 'b', 'orange', 'c', 'm']  # colors for each site

def plot_map():
    plt.figure(figsize=(40, 40))
    ax = plt.axes(projection=ccrs.LambertConformal(cutoff=30))

    fname = os.path.join('/Users/fraserking/Development/global_ml/NE1_50M_SR_W', 'NE1_50M_SR_W.tif')
    ax.imshow(imread(fname), origin='upper', transform=ccrs.PlateCarree())

    for i, lat in enumerate(site_lats):
        plt.scatter(site_lons[i], lat, color=colors[i], marker='o', edgecolors=['white'], linewidth=6, s=4000, transform=ccrs.Geodetic())
        # plt.text(site_lons[i]+2, lat, names[i], fontsize=60, color='black', transform=ccrs.Geodetic())  # adjust text position as needed
        
    ax.coastlines(resolution='110m')
    ax.gridlines(linewidth=3, color='black', linestyle='--', alpha=0.2)

    plt.savefig('../../images/sites.png')


def plot_timeline():
    fig, ax = plt.subplots(figsize=(22, 12))
    plt.grid()
    plt.title('Data Availability (Matched PIP + Radar)')

    for i, site in enumerate(names):
        df = pd.read_csv('/Users/fraserking/Development/pip_processing/data/other/' + site + '_matched_dates.csv')

        if site == 'FIN':
            df['date'] = pd.to_datetime(df['dates'], format='%Y%m%d')
        else:
            df['date'] = pd.to_datetime(df['dates'])
        
        df = df[df['date'] <= pd.to_datetime('2023-01-01')]

        m_date_data = np.full(len(df), i)
        plt.scatter(df.date, m_date_data, marker='|', s=2000, color=colors[i])


    # Format the x-axis
    ax.xaxis.set_major_locator(mdates.YearLocator())  # show the year on the x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # format the date as 'Year'
    ax.set_axisbelow(True)
    plt.xlabel('Dates')
    plt.ylabel('Site')
    ax.set_ylim((-1, 7))
    ax.set_yticks([0, 1, 2, 3, 4, 5, 6])
    ax.set_yticklabels(names)
    plt.tight_layout()
    plt.savefig('../../images/timeline.png')

plot_timeline()