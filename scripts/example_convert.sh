#!/bin/bash
# file: example_convert.sh
# author: Fraser King
# date: March 15, 2023

# Loop through PIP .dat files in a directory and convert them to netCDF
# using our conv_pip.py utility function. Can convert both distributions
# and 1D effective density / precipitation rates

LAT=46.53
LON=-87.55
DATA_PATH="/Users/fraserking/Development/pip_processing/example_data/LakeEffect/PIP/2020_MQT/"
OUT_PATH="/Users/fraserking/Development/pip_processing/example_data/LakeEffect/PIP/2020_MQT/netCDF/"
mkdir -p $OUT_PATH

## declare an array variable
declare -a arr=("PIP_3/f_1_4_DSD_Tables_ascii/" "PIP_3/f_2_4_VVD_Tables/" "Study/f_2_6_rho_Plots_D_minute_dat/" "Study/f_3_1_Summary_Tables_P/")
declare -a vars=("dsd" "vvd" "rho" "ed")
declare -a units=("m−3 mm−1" "m s-1" "g cm-3" "g cm-3")
declare -a long=("Drop size distributions" "Vertical velocity distributions" "Effective density distributions" "Effective density")
declare -a standard=("drop_size_distribution" "velocity_distribution" "effective_density_distribution" "effective_density")

## now loop through the above array
$LOC=0
for i in "${arr[@]}"
do
    echo "${DATA_PATH}${i}"
    for file in "${DATA_PATH}${i}"*.dat; do
        # echo python dist_wrap.py $file "${OUT_PATH}" ${vars[$LOC]} $LAT $LON ${units[$LOC]} ${long[$LOC]} ${standard[$LOC]}
        if [[ $LOC -lt 3 ]]; then
            python dist_wrap.py $file "${OUT_PATH}" ${vars[$LOC]} $LAT $LON ${units[$LOC]} ${long[$LOC]} ${standard[$LOC]}
        else
            python ed_wrap.py $file "${OUT_PATH}" ${vars[$LOC]} $LAT $LON ${units[$LOC]} ${long[$LOC]} ${standard[$LOC]}
        fi
        break
    done
    (( LOC++ ))
done

