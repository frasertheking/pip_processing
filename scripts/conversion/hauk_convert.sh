#!/bin/bash
# file: example_convert.sh
# author: Fraser King
# date: March 15, 2023

# Loop through PIP .dat files in a directory and convert them to netCDF
# using our conv_pip.py utility function. Can convert both distributions
# and 1D effective density / precipitation rates

### NOTE: Replace the path and lat/lon/site information for the site you are converting.
LAT=59.81
LON=7.21
SHORT="HAUK"
SITE="Haukeliseter, Norway"
START_YEAR=2016
END_YEAR=2017
PIP_PATH="/data/HiLaMS/HAUK/PIP/"
TMP_OUT="/data2/fking/s03/converted/"
CONV_PATH="/data2/fking/s03/temporary"

declare -a arr=("PIP_3/f_1_4_DSD_Tables_ascii/" "PIP_3/f_2_4_VVD_Tables/" "Study/f_2_6_rho_Plots_D_minute_dat/" "Study/f_3_1_Summary_Tables_P/")
declare -a wild=("" "_A" "" "") # Need this since VVD has A/S/N filepath pattern

declare -a longnames=("particle_size_distributions" "velocity_distributions" "edensity_distributions" "edensity_lwe_rate")
declare -a vars=("psd" "vvd" "rho" "ed")
declare -a units=("m−3 mm−1" "m s-1" "g cm-3" "g cm-3")
declare -a long=("Drop size distributions" "Vertical velocity distributions" "Effective density distributions" "Effective density")
declare -a standard=("drop_size_distribution" "velocity_distribution" "effective_density_distribution" "effective_density")


# mkdir -p "${TMP_OUT}${SHORT}/netCDF/particle_size_distributions/"
# mkdir -p "${TMP_OUT}${SHORT}/netCDF/velocity_distributions/"
# mkdir -p "${TMP_OUT}${SHORT}/netCDF/edensity_distributions/"
# mkdir -p "${TMP_OUT}${SHORT}/netCDF/edensity_lwe_rate/"

# LOC=0
# for i in "${arr[@]}"
# do
#     DATA_PATH="${PIP_PATH}"
#     OUT_PATH="${TMP_OUT}${SHORT}/netCDF/"
#     echo "${DATA_PATH}${i}"
#     for file in "${DATA_PATH}${i}"*"${wild[$LOC]}".dat; do
#         # echo python dist_wrap.py $file "${OUT_PATH}${vars[$LOC]}/" ${vars[$LOC]} $LAT $LON ${units[$LOC]} ${long[$LOC]} ${standard[$LOC]}
#         if [[ $LOC -lt 3 ]]; then
#             python dist_wrap.py $file "${OUT_PATH}${longnames[$LOC]}/" "${vars[$LOC]}" $LAT $LON "${units[$LOC]}" "${long[$LOC]}" "${standard[$LOC]}" "${SITE}"
#         else
#             python ed_wrap.py $file "${OUT_PATH}${longnames[$LOC]}/" $LAT $LON "${SITE}"
#         fi
#         # break
#     done
#     (( LOC++ ))
# done


# mkdir -p "${TMP_OUT}${SHORT}/netCDF/particle_tables/"
# DATA_PATH="${PIP_PATH}"
# OUT_PATH="${TMP_OUT}${SHORT}/netCDF/"
# for dir in "${DATA_PATH}PIP_3/f_1_2_Particle_Tables_ascii/"*/; do
#     if [ -d "$dir" ]; then
#         # handle .zip files
#         for filepath in "${dir}"*.zip; do
#             echo "Found zipfiles"
#             echo $filepath

#             last_dir=$(basename ${dir})
#             mkdir -p "${OUT_PATH}particle_tables/${last_dir}"
#             mkdir -p "${CONV_PATH}${dir}"
#             cp  $filepath -d "${CONV_PATH}${filepath}"

#             unzip "${CONV_PATH}${filepath}" -d "${CONV_PATH}${filepath%/*}/" # "${CONV_PATH}${filepath%.zip}"   # Need to unzip the tables first
#             python pt_wrap.py "${CONV_PATH}${filepath%.zip}" "${OUT_PATH}particle_tables/${last_dir}/" $LAT $LON "${SITE}"
#             rm -r "${CONV_PATH}${filepath}"    # Delete unzipped file
#             rm -r "${CONV_PATH}${dir}"
#         done

#         # handle .gz files
#         for filepath in "${dir}"*.gz; do
#             echo "Found gz files"
#             last_dir=$(basename ${dir})
#             mkdir -p "${OUT_PATH}particle_tables/${last_dir}"
#             mkdir -p "${CONV_PATH}${dir}"
#             cp  $filepath -d "${CONV_PATH}${filepath}"
#             gzip "${CONV_PATH}${filepath}" -d "${CONV_PATH}${filepath%.gz}"   # Need to unzip the tables first
#             python pt_wrap.py "${CONV_PATH}${filepath%.gz}" "${OUT_PATH}particle_tables/${last_dir}/" $LAT $LON "${SITE}"
#             rm -r "${CONV_PATH}${filepath}"    # Delete unzipped file
#             rm -r "${CONV_PATH}${dir}"
#         done

#         # handle uncompressed files
#         for filepath in "${dir}"*.dat; do
#             echo "Found uncompressed files"
#             last_dir=$(basename ${dir})
#             mkdir -p "${OUT_PATH}particle_tables/${last_dir}"
#             python pt_wrap.py "${filepath}" "${OUT_PATH}particle_tables/${last_dir}/" $LAT $LON "${SITE}"
#         done

#     fi
# done

# PIP_2
mkdir -p "${TMP_OUT}${SHORT}/netCDF/a_particle_tables/"
DATA_PATH="${PIP_PATH}"
OUT_PATH="${TMP_OUT}${SHORT}/netCDF/"
for dir in "${DATA_PATH}PIP_2/a_Particle_Tables/"*/; do
    if [ -d "$dir" ]; then
        # handle .zip files
        for filepath in "${dir}"*.zip; do
            echo "Found zipfiles"
            echo $filepath
            last_dir=$(basename ${dir})

            # define output file name based on the input file (assuming output extension is .nc)
            outfile="${OUT_PATH}a_particle_tables/${last_dir}/$(basename "${filepath%.*.*}").nc"

            # if output file already exists, skip to the next iteration
            if [ -f "$outfile" ]; then
                echo "Skipping already processed file: $filepath"
                continue
            fi

            mkdir -p "${OUT_PATH}a_particle_tables/${last_dir}"
            mkdir -p "${CONV_PATH}${dir}"
            cp  $filepath -d "${CONV_PATH}${filepath}"

            unzip "${CONV_PATH}${filepath}" -d "${CONV_PATH}${filepath%/*}/" # "${CONV_PATH}${filepath%.zip}"   # Need to unzip the tables first
            python pt_wrap.py "${CONV_PATH}${filepath%.zip}" "${OUT_PATH}a_particle_tables/${last_dir}/" $LAT $LON "${SITE}"
            rm -r "${CONV_PATH}${filepath}"    # Delete unzipped file
            rm -r "${CONV_PATH}${dir}"
        done

        # handle .gz files
        for filepath in "${dir}"*.gz; do
            echo "Found gz files"
            echo $filepath

            last_dir=$(basename ${dir})

            # define output file name based on the input file (assuming output extension is .nc)
            outfile="${OUT_PATH}a_particle_tables/${last_dir}/$(basename "${filepath%.*.*}").nc"

            # if output file already exists, skip to the next iteration
            if [ -f "$outfile" ]; then
                echo "Skipping already processed file: $filepath"
                continue
            fi

            mkdir -p "${OUT_PATH}a_particle_tables/${last_dir}"
            mkdir -p "${CONV_PATH}${dir}"
            cp  $filepath -d "${CONV_PATH}${filepath}"
            gzip "${CONV_PATH}${filepath}" -d "${CONV_PATH}${filepath%.gz}"   # Need to unzip the tables first
            python pt_wrap.py "${CONV_PATH}${filepath%.gz}" "${OUT_PATH}a_particle_tables/${last_dir}/" $LAT $LON "${SITE}"
            rm -r "${CONV_PATH}${filepath}"    # Delete unzipped file
            rm -r "${CONV_PATH}${dir}"
        done

        # handle uncompressed files
        for filepath in "${dir}"*.dat; do
            echo "Found uncompressed files"
            echo $filepath
            last_dir=$(basename ${dir})

            # define output file name based on the input file (assuming output extension is .nc)
            outfile="${OUT_PATH}a_particle_tables/${last_dir}/$(basename "${filepath%.*}").nc"
            echo $outfile

            # if output file already exists, skip to the next iteration
            if [ -f "$outfile" ]; then
                echo "Skipping already processed file: $filepath"
                continue
            fi

            mkdir -p "${OUT_PATH}a_particle_tables/${last_dir}"
            python pt_wrap.py "${filepath}" "${OUT_PATH}a_particle_tables/${last_dir}/" $LAT $LON "${SITE}"
        done

    fi
done


echo "Conversion complete!"
