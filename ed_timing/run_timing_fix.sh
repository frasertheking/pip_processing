#!/bin/bash

# Path to the directories
ED_PATH="edensity_lwe_rate"
RHO_PATH="edensity_distributions"
OUT_PATH="fixed"
PYTHON_SCRIPT="fix_timing.py"

# Loop through files in the edensity_lwe_rate directory
for ed_file in "$ED_PATH"/*_P_Minute.nc; do
    echo $ed_file
    # Extract the date from the filename
    date_string=$(echo "$ed_file" | cut -c 23-30)

    # Find the corresponding file in the edensity_distributions directory
    matching_rho_file=$(find "$RHO_PATH" -name "*${date_string}*_D_minute.nc")

    # If there's a matching file
    if [ -n "$matching_rho_file" ]; then
        echo "Matching files: $ed_file and $matching_rho_file"
        
        # Call the Python script with required arguments
        python "$PYTHON_SCRIPT" "$matching_rho_file" "$ed_file" "$OUT_PATH"
    else
        echo "No matching file for $ed_file"
    fi
done