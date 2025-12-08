

import pandas as pd
import numpy as np
import os

# Loeme tsv faili sisse (sep='\t' tähendab, et eraldajaks on tabulaator)
# Asenda 'faili_nimi.tsv' oma faili tegeliku teekonnaga
cities_df = pd.read_csv('../data/ESTAT_CITIES_6.0.tsv', sep='\t')
geo_df = pd.read_csv('../data/ESTAT_GEO_25.3.tsv', sep='\t')
df = pd.read_csv('../data/nutsAndSR.csv', sep='\t')
df_latin = pd.read_csv('../data/nutscyrandgreek.csv', sep=';')
df_latin = df_latin.rename(columns={
    "Code": "NUTS Code",
    "Label": "NUTS label",
    "Transliteration to Latin": "Latin Name"
})
print(df_latin.head())
print()
print(df.head())
df_new = pd.merge(
    df,
    df_latin[['NUTS Code', 'Latin Name']],
    on='NUTS Code',
    how='left'
)
df_new["Region name"] = np.where(
    df_new["Latin Name"].notna(),
    df_new['Latin Name'],
    df_new['NUTS label']
)
df_new = df_new.drop(columns=["Latin Name"])
print(df_new.head())
print()
cities_df = cities_df[['CODE','Label - English']]
cities_df = cities_df.loc[cities_df['CODE'].str.contains('C')]
geo_df = geo_df[['CODE','Label - English']]
geo_dict = pd.Series(geo_df['Label - English'].values, index=geo_df['CODE']).to_dict()
city_dict = pd.Series(cities_df['Label - English'].values, index=cities_df['CODE']).to_dict()
# Loome sõnastiku, kus võtmeks on 'NUTS Code' ja väärtuseks 'NUTS label'
nuts_dict = pd.Series(df_new['Region name'].values, index=df_new['NUTS Code']).to_dict()
COUNTRY_CODES = {
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'HR': 'Croatia',
    'CY': 'Cyprus', 'CZ': 'Czechia', 'DK': 'Denmark', 'EE': 'Estonia',
    'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'EL': 'Greece',
    'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'MT': 'Malta', 'NL': 'Netherlands',
    'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'SK': 'Slovakia',
    'SI': 'Slovenia', 'ES': 'Spain', 'SE': 'Sweden',

    # Ühendkuningriigid
    'UK': 'United Kingdom',
    'UKC-L': 'England and Wales',
    'UKM': 'Scotland',
    'UKN': 'Northern Ireland',

    # Kandidaatriigid ja muud Euroopa riigid
    'IS': 'Iceland', 'LI': 'Liechtenstein', 'NO': 'Norway', 'CH': 'Switzerland',
    'ME': 'Montenegro', 'MK': 'North Macedonia', 'AL': 'Albania', 'RS': 'Serbia',
    'TR': 'Turkey',
    'BA': 'Bosnia and Herzegovina',
    'XK': 'Kosovo',

    # Muud koodid
    'US': 'United States',
    'FX': 'Metropolitan France',
    'EU_V': 'European Union - Aggregate'
}
def get_country_name(geo_code):
    # võtab vastu geokoodi ja tagastab riigi nime
    if isinstance(geo_code, str) and len(geo_code) == 2:
        prefix = geo_code[:2]
        return COUNTRY_CODES.get(prefix, geo_code)
    if isinstance(geo_code, str) and len(geo_code) >= 3:
        prefix = geo_code[:5]
        return COUNTRY_CODES.get(prefix, geo_code)
    return geo_code

def get_region_name(geo_code):
    if isinstance(geo_code, str) and len(geo_code) >=2:
        if geo_code.__contains__('C'):
            if geo_code[:-1] == 'C' or geo_code[:-2] == 'C':
                return city_dict.get(geo_code, geo_code)
            else:
                return geo_dict.get(geo_code, geo_code)
    return geo_dict.get(geo_code, geo_code)

#df_nuts3_data['Country_Code'] = df_nuts3_data['NUTS3_ID'].str[:2]
def lisa_riik(df):
    if not df.empty:
        if 'geo' in df.columns:
            df['country'] = df['geo'].str[:2]
            df['country'] = df['country'].apply(get_country_name)
            df['geo'] = df['geo'].apply(get_region_name)
            return df
        else:
            df['country'] = df['cities'].str[:2]
            df['country'] = df['country'].apply(get_country_name)
            df['cities'] = df['cities'].apply(get_region_name)
    return df


def tyhjadRead(df):
    if not df.empty:
        copy_df = df.copy(deep=True)
        for column in df.columns:
            copy_df.loc[copy_df[column]==": ", column] = np.nan
            copy_df.loc[copy_df[column] == ": m", column] = np.nan
            copy_df.loc[copy_df[column] == ":", column] = np.nan
            copy_df.loc[copy_df[column] == 0, column] = np.nan
        return copy_df



'''
directory = r"..\data\cleanedDatasets\nan_rows\regionDatasets"
new_directory = r"..\data\cleanedDatasets\nan_rows\regionDatasets\region_names_changed"
for name in os.listdir(directory):
    full_path = os.path.join(directory, name)

    if not os.path.isfile(full_path):
        continue  # skip folders

    data = pd.read_csv(full_path, sep="\t")
    new_data = lisa_riik(data)
    #new_data = eemaldaRead(tyhjadRead(data))
    new_data.to_csv(os.path.join(new_directory, name), sep="\t", index=False)
    print(name)
'''

data = pd.read_csv("../data/population_by_NUTS3_region.tsv", sep="\t")
new_data = lisa_riik(data)
new_data = tyhjadRead(new_data)
new_data.to_csv("../data/population_by_NUTS3_region_regions_new.tsv", sep="\t", index=False)
print(data.head())
