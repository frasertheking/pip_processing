import os
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
from skimage.io import imread

site_lats = [46.532, 44.908, 61.845, 69.058, 59.81, 67.84, 37.665]
site_lons = [-87.548, -84.719, 24.287, -152.863, 7.21, 20.41, 128.7]
names = ['MQT', 'APX', 'FIN', 'NSA', 'HAUK', 'KIR', 'ICE-POP']

colors = ['black', 'r', 'g', 'b', 'orange', 'c', 'm']  # colors for each site

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