#!/bin/bash

# Define the root path
ROOT_PATH="/data2/fking/s03/converted/2018_NSA/"

# Define subdirectories and suffixes
SUBDIRS=("adjusted_edensity_lwe_rate" "particle_size_distributions" "edensity_distributions" "velocity_distributions")
SUFFIXES=("_min" "_dsd" "_rho" "_vvd")

# Loop through each subfolder
for SUBFOLDER in "$ROOT_PATH"/*/; do
    # Check if it's a directory before proceeding
    if [ -d "$SUBFOLDER" ]; then
        # Loop through each subdirectory type
        for INDEX in "${!SUBDIRS[@]}"; do
            SUBDIR="${SUBDIRS[$INDEX]}"
            SUFFIX="${SUFFIXES[$INDEX]}"

            # Loop through each file in the subdirectory
            for FILE in "$SUBFOLDER/netCDF/$SUBDIR/"*.nc; do
                FILENAME=$(basename "$FILE")
                PREFIX="${FILENAME:0:11}"
                NEW_NAME="${PREFIX}${SUFFIX}.nc"
                
                # Check if the file actually exists (to handle the case where no .nc files are found)
                if [ -e "$FILE" ]; then
                    echo mv "$FILE" "$SUBFOLDER/netCDF/$SUBDIR/$NEW_NAME"
                    mv "$FILE" "$SUBFOLDER/netCDF/$SUBDIR/$NEW_NAME"
                fi
            done
        done
    fi
done
