import pandas as pd
import numpy as np

nuts_df = pd.read_csv("../data/nutskoodikesed.csv", sep=";")
nuts_sr = pd.read_csv("../data/nutsSR.csv", sep=";")
nuts_latin = pd.read_csv("../data/nutscyrandgreek.csv", sep=";")

#print(nuts_df.columns)
nuts_latin = nuts_latin[["Code", "Label", "Transliteration to Latin"]]
nuts_df = nuts_df[["Country code", "NUTS Code", "NUTS label", "NUTS level","Country order"]]
nuts_sr = nuts_sr[['Country code', 'SR Code', 'SR label', 'SR level', 'Country order']]
data = pd.DataFrame({
    "Country code": pd.concat([nuts_df["Country code"], nuts_sr["Country code"]], axis=0),
    "NUTS Code": pd.concat([nuts_df["NUTS Code"], nuts_sr["SR Code"]], axis=0),
    "NUTS label": pd.concat([nuts_df["NUTS label"], nuts_sr["SR label"]], axis=0)
})

data=data.dropna(how="all")
data = data.sort_values("NUTS Code")
data = data.loc[data["Country code"]!="Country code", ["Country code","NUTS Code", "NUTS label"]]
data.to_csv("..\\data\\nutsAndSR.csv", sep="\t", index=False)

#print(nuts_latin.columns)
#print(nuts_df.head())
