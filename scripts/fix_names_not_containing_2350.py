import os

def find_files(base_path):
    # Loop through the folder
    for root, dirs, files in os.walk(base_path):
        # Loop through each file in the current folder
        for filename in files:
            # Check if filename contains "_01_"
            if "_01_" in filename:
                # Split the filename into its prefix and suffix
                prefix, suffix = filename.split("_01_", 1)
                
                # If last 4 characters of prefix are not "2350"
                if prefix[-4:] != "2350":
                    # Create new filename replacing last 4 characters of prefix with "2350"
                    new_filename = prefix[:-4] + "2350" + "_01_" + suffix
                    old_full_path = os.path.join(root, filename)
                    new_full_path = os.path.join(root, new_filename)
                    
                    # Rename the file
                    os.rename(old_full_path, new_full_path)
                    print(f"Renamed: {old_full_path} -> {new_full_path}")

                # Else just print the path of files that do not contain "2350_01"
                elif "2350_01" not in filename:
                    full_path = os.path.join(root, filename)
                    print(full_path)



base_path = '/data2/fking/s03/converted/'  # Replace with the path you want to search
find_files(base_path)