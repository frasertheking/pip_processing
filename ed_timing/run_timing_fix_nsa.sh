#!/bin/bash

# Path to the directories
# ED_PATH="edensity_lwe_rate"
# RHO_PATH="edensity_distributions"
# OUT_PATH="fixed"
# PYTHON_SCRIPT="fix_timing.py"

ED_PATH="edensity_lwe_rate"
RHO_PATH="edensity_distributions"
OUT_PATH="adjusted_edensity_lwe_rate"
PYTHON_SCRIPT="fix_timing.py"

MAIN_PATH='/data2/fking/s03/converted/'
declare -a subfolders=("2018_NSA/netCDF/" "2019_NSA/netCDF/" "2020_NSA/netCDF/")

PYTHON_SCRIPT="fix_timing.py"

# Loop through each subfolder
for subfolder in "${subfolders[@]}"; do
    # Prepend MAIN_PATH and subfolder to each path
    CUR_ED_PATH="${MAIN_PATH}${subfolder}${ED_PATH}"
    CUR_RHO_PATH="${MAIN_PATH}${subfolder}${RHO_PATH}"
    CUR_OUT_PATH="${MAIN_PATH}${subfolder}${OUT_PATH}"
    
    echo "Processing subfolder: ${subfolder}"

    # Loop through files in the current edensity_lwe_rate directory
    for ed_file in "${CUR_ED_PATH}"/*_P_Minute.nc; do
        echo $ed_file
        # Extract the date from the filename
        date_string=$(echo "$ed_file" | cut -c 65-72)
        echo $date_string

        # Find the corresponding file in the current edensity_distributions directory
        matching_rho_file=$(find "$CUR_RHO_PATH" -name "*${date_string}*_D_minute.nc")

        # If there's a matching file
        if [ -n "$matching_rho_file" ]; then
            echo "Matching files: $ed_file and $matching_rho_file"
            
            # Call the Python script with required arguments
            python "$PYTHON_SCRIPT" "$matching_rho_file" "$ed_file" "$CUR_OUT_PATH"
        else
            echo "No matching file for $ed_file"
        fi
    done
done