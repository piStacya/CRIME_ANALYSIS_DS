import pandas as pd
import numpy as np
import os

def eemaldaRead(df):
    veeruNr = df.shape[1]
    mitu =  veeruNr - 3;
    print(mitu)
    if not df.empty:
        copy_df = df.copy(deep=True)
        copy_df = copy_df.dropna(thresh=mitu)
        return copy_df

def tyhjadRead(df):
    if not df.empty:
        copy_df = df.copy(deep=True)
        for column in df.columns:
            copy_df.loc[copy_df[column]==": ", column] = np.nan
        return copy_df

directory = r"..\cleanedDatasets"
new_directory = r"..\cleanedDatasets\nan_rows"
for name in os.listdir(directory):
    full_path = os.path.join(directory, name)

    if not os.path.isfile(full_path):
        continue  # skip folders

    data = pd.read_csv(full_path, sep="\t")
    new_data = eemaldaRead(tyhjadRead(data))
    new_data.to_csv(os.path.join(new_directory, name), sep="\t", index=False)
    print(name)
    #print(new_data.value_counts())
#df = pd.read_csv("..\\cleanedDatasets\\crimes_recorded_by_the_police_by_offence_category_new.tsv", sep="\t")

#new_df = tyhjadRead(df)

