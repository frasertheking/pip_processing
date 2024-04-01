import os
import shutil

def find_and_delete_files(directory):
    for dirpath, _, filenames in os.walk(directory):
        checked_files = set()

        for fname1 in filenames:
            for fname2 in filenames:
                if fname1 == fname2 or (fname1, fname2) in checked_files or (fname2, fname1) in checked_files:
                    continue

                # Check if the start and end of the filenames are the same
                if fname1[:11] == fname2[:11] and fname1[15:] == fname2[15:]:
                    # Extract the differing numbers
                    num1 = int(fname1[11:15])
                    num2 = int(fname2[11:15])

                    # Determine which file to delete
                    if num1 < num2:
                        file_to_delete = os.path.join(dirpath, fname1)
                    else:
                        file_to_delete = os.path.join(dirpath, fname2)
                    
                    print(f"Deleting {file_to_delete}")
                    try:
                        os.remove(file_to_delete)
                    except:
                        print("could not delete")
                    # shutil.move(file_to_move, dest_path)
                    print('------')

                checked_files.add((fname1, fname2))

if __name__ == '__main__':
    find_and_delete_files('/Users/fraserking/Development/pip_processing/data/converted/')
