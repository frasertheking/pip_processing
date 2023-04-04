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
SHORT="MQT"
SITE="NWS Marquette, Michigan"
START_YEAR=2014
END_YEAR=2022
PIP_PATH="/data/LakeEffect/PIP/"

mkdir -p "${OUT_PATH}particle_size_distributions/"
mkdir -p "${OUT_PATH}velocity_distributions/"
mkdir -p "${OUT_PATH}edensity_distributions/"
mkdir -p "${OUT_PATH}edensity_lwe_rate/"

declare -a arr=("PIP_3/f_1_4_DSD_Tables_ascii/" "PIP_3/f_2_4_VVD_Tables/" "Study/f_2_6_rho_Plots_D_minute_dat/" "Study/f_3_1_Summary_Tables_P/")
declare -a wild=("" "_A" "" "") # Need this since VVD has A/S/N filepath pattern

declare -a longnames=("particle_size_distributions" "velocity_distributions" "edensity_distributions" "edensity_lwe_rate")
declare -a vars=("psd" "vvd" "rho" "ed")
declare -a units=("m−3 mm−1" "m s-1" "g cm-3" "g cm-3")
declare -a long=("Drop size distributions" "Vertical velocity distributions" "Effective density distributions" "Effective density")
declare -a standard=("drop_size_distribution" "velocity_distribution" "effective_density_distribution" "effective_density")

for y in $(seq $START_YEAR $END_YEAR)
do
    LOC=0
    for i in "${arr[@]}"
    do
        DATA_PATH="${PIP_PATH}${y}_${SHORT}"
        OUT_PATH="${DATA_PATH}/netCDF"
        echo "${DATA_PATH}${i}"
        for file in "${DATA_PATH}${i}"*"${wild[$LOC]}".dat; do
            # echo python dist_wrap.py $file "${OUT_PATH}${vars[$LOC]}/" ${vars[$LOC]} $LAT $LON ${units[$LOC]} ${long[$LOC]} ${standard[$LOC]}
            if [[ $LOC -lt 3 ]]; then
                python dist_wrap.py $file "${OUT_PATH}${longnames[$LOC]}/" "${vars[$LOC]}" $LAT $LON "${units[$LOC]}" "${long[$LOC]}" "${standard[$LOC]}" "${SITE}"
            else
                python ed_wrap.py $file "${OUT_PATH}${longnames[$LOC]}/" $LAT $LON "${SITE}"
            fi
            break
        done
        (( LOC++ ))
    done
done

echo "Conversion complete!"
