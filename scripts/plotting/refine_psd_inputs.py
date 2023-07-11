import pandas as pd
import glob
import os
from datetime import datetime, timedelta

# List to hold dataframes
dfs = []

# Get list of all csv files
files = glob.glob('../../data/processed/psd_inputs/*.csv')

# Iterate over all files
for file in files:
    print("On file", file)
    # Read csv file into a pandas dataframe
    df = pd.read_csv(file, header=0)

    # Get NAME and date from file name
    basename = os.path.basename(file)
    name, date_str = basename.split('_')
    date_str = date_str.split('.')[0]

    # Convert string to datetime object
    date = datetime.strptime(date_str, "%Y%m%d")

    # Add a NAME column
    df['NAME'] = name

    # Convert the index column to datetime using the date from filename and minute information from index
    df['datetime'] = [date + timedelta(minutes=int(i)) for i in df.iloc[:,0]]

    # Add the dataframe to the list
    dfs.append(df)

# Concatenate all dataframes in the list
final_df = pd.concat(dfs, ignore_index=True)

# Save the final dataframe to a new csv file
final_df.to_csv('../../data/processed/psd_inputs/final_data.csv', index=False)
