#!/bin/bash
# file: example_pt_convert.sh
# author: Fraser King
# date: March 22, 2023

# Loop through PIP .dat files in a directory and convert them to netCDF
# using our conv_pip.py utility function. This example differs from example_convert.sh
# as the PIP_3 particle table files are zipped and the structure of the file is unique
# compared to the other variables we convert. 

### NOTE: Replace the path and lat/lon/site information for the site you are converting.
###       We also delete the extracted .dat files after the conversion to netCDF is
###       complete to save on system space.

LAT=46.53
LON=-87.55
SITE="NWS Marquette, Michigan"
DATA_PATH="/Users/fraserking/Development/pip_processing/example_data/LakeEffect/PIP/2020_MQT/"
OUT_PATH="/Users/fraserking/Development/pip_processing/example_data/LakeEffect/PIP/2020_MQT/netCDF/"
mkdir -p "${OUT_PATH}particle_tables/"

for dir in "${DATA_PATH}PIP_3/f_1_2_Particle_Tables_ascii/"*/; do
    if [ -d "$dir" ]; then
        for filepath in "${dir}"*.zip; do
            last_dir=$(basename ${dir})
            mkdir -p "${OUT_PATH}particle_tables/${last_dir}"
            unzip $filepath -d $dir     # Need to unzip the tables first
            python pt_wrap.py "${filepath%.zip}" "${OUT_PATH}particle_tables/${last_dir}/" $LAT $LON $SITE
            rm -r "${filepath%.zip}"    # Delete unzipped file
        done
    fi
done

