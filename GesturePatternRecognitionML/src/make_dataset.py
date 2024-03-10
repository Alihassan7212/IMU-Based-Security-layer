import pandas as pd
from glob import glob
import os


def read_data_from_files(data_path):
    print(data_path)
    files = glob(data_path+"*.csv")

    df = pd.DataFrame()

    for f in files:
        data = pd.read_csv(f)
        f_name = os.path.splitext(f)[0].split('\\')[-1]

        data['participant'] = os.path.split(f)[0].split('/')[-1]
        data['label'] = f_name
        data.drop_duplicates(subset=['time'], inplace=True)
        
        df = pd.concat([df, data])
        
    df['time'] = pd.to_timedelta(df['time'], unit='s')
    df.set_index('time', inplace=True)

    return df


data_path = "../data/Ali/"
df1 = read_data_from_files(data_path)

data_path = "../data/Osama/"
df2 = read_data_from_files(data_path)

data_merged = pd.concat([df1, df2])

sampling = {
    "ax": "mean",
    "ay": "mean",
    "az": "mean",
    "wx": "mean",
    "wy": "mean",
    "wz": "mean",
    "participant": "last",
    "label": "last",
}

data_merged.reset_index(inplace=True)
data_merged.to_csv("data/interim/01_data_processed.csv", index=False)
