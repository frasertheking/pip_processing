#!/bin/bash

# Start in the base directory
BASE_DIR="/data2/fking/s03/converted/"

# Define the array of subfolders to look in
SUBFOLDERS=("edensity_distributions" "edensity_lwe_rate" "particle_size_distributions" "velocity_distributions")

# Loop through each subfolder in the base directory
for dir in "$BASE_DIR"*/; do

  # Initialize an associative array to keep track of the file dates in adjusted_edensity_lwe_rate folder
  declare -A file_dates=()

  # Loop through the files in the adjusted_edensity_lwe_rate subfolder to remember the list of file dates
  for file in "${dir}netCDF/adjusted_edensity_lwe_rate/"*.nc; do
    if [ -f "$file" ]; then
      # Extract the date part from the filename (assumes format like 004201601012350_01_P_Minute.nc)
      file_date=$(echo "$(basename "$file")" | cut -d "_" -f 1 | cut -c 4-11)
      # Store the date in the associative array
      file_dates["$file_date"]=1
    fi
  done

  # Loop through each type of subfolder
  for subfolder in "${SUBFOLDERS[@]}"; do
    target_dir="${dir}netCDF/$subfolder/"

    # Check if the target directory exists
    if [ -d "$target_dir" ]; then

      # Loop through the files in the target directory
      for file in "${target_dir}"*.nc; do
        if [ -f "$file" ]; then
          # Extract the date part from the filename (assumes format like 004201601012350_01_P_Minute.nc)
          file_date=$(echo "$(basename "$file")" | cut -d "_" -f 1 | cut -c 4-11)

          # Check if the file_date exists in the list of file dates from adjusted_edensity_lwe_rate folder
          if [ -z "${file_dates["$file_date"]}" ]; then
            # If not found, rename the file by prepending "_old_"
            new_file="${target_dir}_old_$(basename "$file")"
            echo "mv \"$file\" \"$new_file\""  # Remove 'echo' to actually rename the file
          fi
        fi
      done
    fi
  done

  # Unset the associative array for the next iteration
  unset file_dates
done