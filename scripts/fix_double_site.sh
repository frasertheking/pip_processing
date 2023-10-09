#!/bin/bash

# Check if a path is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory_path>"
    exit 1
fi

directory_path="$1"

# Find all .nc files recursively and run the Python script on each
find "$directory_path" -type f -name "*.nc" | while read -r ncfile; do
    python3 fix_double_site_comment.py "$ncfile"
    echo "Processed: $ncfile"
done

echo "All files processed!"
