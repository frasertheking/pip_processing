#!/bin/bash
# file: example_convert.sh
# author: Fraser King
# date: March 15, 2023

# Loop through PIP .dat files in a directory and convert them to netCDF
# using our conv_pip.py utility function. Can convert both distributions
# and 1D effective density / precipitation rates

### NOTE: Replace the path and lat/lon/site information for the site you are converting.

LAT=46.5318
LON=-87.5483
SITE="NWS Marquette, Michigan"
DATA_PATH="/Users/fraserking/Desktop/asd/"
OUT_PATH="/Users/fraserking/Desktop/asd/"
mkdir -p "${OUT_PATH}velocity_distributions/"

declare -a arr=("PIP_3/f_2_4_VVD_Tables/")
declare -a wild=("_A") # Need this since VVD has A/S/N filepath pattern

declare -a longnames=("velocity_distributions")
declare -a vars=("vvd")
declare -a units=("m s-1")
declare -a long=("Vertical velocity distributions")
declare -a standard=("velocity_distribution")

LOC=0
for i in "${arr[@]}"
do
    echo "${DATA_PATH}${i}"
    for file in "${DATA_PATH}${i}"*"${wild[$LOC]}".dat; do
        # echo python dist_wrap.py $file "${OUT_PATH}${vars[$LOC]}/" ${vars[$LOC]} $LAT $LON ${units[$LOC]} ${long[$LOC]} ${standard[$LOC]}
        if [[ $LOC -lt 3 ]]; then
            python dist_wrap.py $file "${OUT_PATH}${longnames[$LOC]}/" "${vars[$LOC]}" $LAT $LON "${units[$LOC]}" "${long[$LOC]}" "${standard[$LOC]}" "${SITE}"
        else
            python ed_wrap.py $file "${OUT_PATH}${longnames[$LOC]}/" $LAT $LON "${SITE}"
        fi
        # break
    done
    (( LOC++ ))
done

