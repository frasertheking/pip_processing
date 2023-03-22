#!/bin/bash
# file: example_convert.sh
# author: Fraser King
# date: March 15, 2023

# Loop through PIP .dat files in a directory and convert them to netCDF
# using our conv_pip.py utility function. Can convert both distributions
# and 1D effective density / precipitation rates

### NOTE: Replace the path and lat/lon information for the site you are converting

LAT=46.53
LON=-87.55
DATA_PATH="/Users/fraserking/Development/pip_processing/example_data/LakeEffect/PIP/2020_MQT/"
OUT_PATH="/Users/fraserking/Development/pip_processing/example_data/LakeEffect/PIP/2020_MQT/netCDF/"
mkdir -p "${OUT_PATH}particle_tables/"


declare -a arr=("PIP_3/f_1_4_DSD_Tables_ascii/" "PIP_3/f_2_4_VVD_Tables/" "Study/f_2_6_rho_Plots_D_minute_dat/" "Study/f_3_1_Summary_Tables_P/")
declare -a wild=("" "_A" "" "") # Need this since VVD has A/S/N filepath pattern

declare -a longnames=("particle_size_distributions" "velocity_distributions" "edensity_distributions" "edensity_lwe_rate")
declare -a vars=("psd" "vvd" "rho" "ed")
declare -a units=("m−3 mm−1" "m s-1" "g cm-3" "g cm-3")
declare -a long=("Drop size distributions" "Vertical velocity distributions" "Effective density distributions" "Effective density")
declare -a standard=("drop_size_distribution" "velocity_distribution" "effective_density_distribution" "effective_density")


for dir in "${DATA_PATH}PIP_3/f_1_2_Particle_Tables_ascii/"*/; do
    if [ -d "$dir" ]; then
        for filepath in "${dir}"*.zip; do
            echo "${filepath}"
            unzip $filepath -d $dir # Need to decompress the tables first
            echo "Doing stuff with unzipped file in Python..."
            # rm -r "${filepath%.zip}"
        done
    fi
done

