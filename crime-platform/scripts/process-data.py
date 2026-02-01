"""
Data processing script for European Crime Analysis Platform
Converts TSV data to JSON format for web consumption
"""
import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'public', 'data')

os.makedirs(os.path.join(OUTPUT_DIR, 'countries'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'crimes'), exist_ok=True)

ICCS_MAPPING = {
    "ICCS0101": "Intentional homicide",
    "ICCS0102": "Attempted intentional homicide",
    "ICCS020111": "Serious assault",
    "ICCS020221": "Kidnapping",
    "ICCS0301": "Sexual violence",
    "ICCS03011": "Rape",
    "ICCS03012": "Sexual assault",
    "ICCS030221": "Child pornography",
    "ICCS0302": "Sexual exploitation",
    "ICCS0401": "Robbery",
    "ICCS0501": "Burglary",
    "ICCS05012": "Burglary of private residential premises",
    "ICCS0502": "Theft",
    "ICCS05021": "Theft of a motorized vehicle",
    "ICCS0601": "Unlawful acts involving controlled drugs",
    "ICCS0701": "Fraud",
    "ICCS0703": "Corruption",
    "ICCS07031": "Bribery",
    "ICCS07041": "Money laundering",
    "ICCS0903": "Acts against computer systems",
    "ICCS09051": "Organized criminal group participation",
    "ICCS1001": "Environmental pollution crimes",
    "ICCS1002": "Waste dumping crimes",
    "ICCS1003": "Protected species crimes",
    "ICCS1004": "Natural resource crimes"
}

CRIME_CATEGORIES = {
    "violence": {
        "label": "Violence",
        "labelEt": "Vägivald",
        "codes": ["ICCS0101", "ICCS0102", "ICCS020111", "ICCS020221", "ICCS0401"]
    },
    "sexual": {
        "label": "Sexual Crimes",
        "labelEt": "Seksuaalkuriteod",
        "codes": ["ICCS0301", "ICCS03011", "ICCS03012", "ICCS030221", "ICCS0302"]
    },
    "property": {
        "label": "Property",
        "labelEt": "Varakuriteod",
        "codes": ["ICCS0501", "ICCS05012", "ICCS0502", "ICCS05021"]
    },
    "drugs": {
        "label": "Drugs",
        "labelEt": "Narkokuriteod",
        "codes": ["ICCS0601"]
    },
    "financial": {
        "label": "Financial",
        "labelEt": "Finantskuriteod",
        "codes": ["ICCS0701", "ICCS0703", "ICCS07031", "ICCS07041"]
    },
    "cyber": {
        "label": "Cyber",
        "labelEt": "Küberkuriteod",
        "codes": ["ICCS0903", "ICCS09051"]
    },
    "environmental": {
        "label": "Environmental",
        "labelEt": "Keskkonnakuriteod",
        "codes": ["ICCS1001", "ICCS1002", "ICCS1003", "ICCS1004"]
    }
}

COUNTRY_NAMES = {
    "AL": "Albania", "AT": "Austria", "BA": "Bosnia and Herzegovina",
    "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland",
    "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany",
    "DK": "Denmark", "EE": "Estonia", "EL": "Greece",
    "ES": "Spain", "FI": "Finland", "FR": "France",
    "HR": "Croatia", "HU": "Hungary", "IE": "Ireland",
    "IS": "Iceland", "IT": "Italy", "LI": "Liechtenstein",
    "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
    "ME": "Montenegro", "MK": "North Macedonia", "MT": "Malta",
    "NL": "Netherlands", "NO": "Norway", "PL": "Poland",
    "PT": "Portugal", "RO": "Romania", "RS": "Serbia",
    "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia",
    "TR": "Turkey", "XK": "Kosovo"
}

COUNTRY_NAMES_ET = {
    "AL": "Albaania", "AT": "Austria", "BA": "Bosnia ja Hertsegoviina",
    "BE": "Belgia", "BG": "Bulgaaria", "CH": "Šveits",
    "CY": "Küpros", "CZ": "Tšehhi", "DE": "Saksamaa",
    "DK": "Taani", "EE": "Eesti", "EL": "Kreeka",
    "ES": "Hispaania", "FI": "Soome", "FR": "Prantsusmaa",
    "HR": "Horvaatia", "HU": "Ungari", "IE": "Iirimaa",
    "IS": "Island", "IT": "Itaalia", "LI": "Liechtenstein",
    "LT": "Leedu", "LU": "Luksemburg", "LV": "Läti",
    "ME": "Montenegro", "MK": "Põhja-Makedoonia", "MT": "Malta",
    "NL": "Holland", "NO": "Norra", "PL": "Poola",
    "PT": "Portugal", "RO": "Rumeenia", "RS": "Serbia",
    "SE": "Rootsi", "SI": "Sloveenia", "SK": "Slovakkia",
    "TR": "Türgi", "XK": "Kosovo"
}

def load_crime_data():
    tsv_path = os.path.join(DATA_DIR, 'cleanedDatasets', 'police_recorded_offences_by_offence_category_new.tsv')
    df = pd.read_csv(tsv_path, sep='\t')

    df.columns = df.columns.str.strip()

    year_cols = [col for col in df.columns if col.isdigit()]

    df_long = df.melt(
        id_vars=['freq', 'iccs', 'unit', 'geo'],
        value_vars=year_cols,
        var_name='year',
        value_name='value'
    )

    df_long['year'] = pd.to_numeric(df_long['year'])
    df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce')

    ignore_geo = ['EU27_2020', 'EA19', 'EA20']
    df_long = df_long[~df_long['geo'].isin(ignore_geo)]

    df_long = df_long[df_long['iccs'].isin(ICCS_MAPPING.keys())]

    return df_long

def create_main_dataset(df):
    data = []

    for _, row in df.iterrows():
        if pd.notna(row['value']):
            data.append({
                'geo': row['geo'],
                'iccs': row['iccs'],
                'unit': row['unit'],
                'year': int(row['year']),
                'value': round(row['value'], 2) if pd.notna(row['value']) else None
            })

    return data

def create_country_data(df):
    countries = df['geo'].unique()

    for country in countries:
        country_df = df[df['geo'] == country]
        data = create_main_dataset(country_df)

        output_path = os.path.join(OUTPUT_DIR, 'countries', f'{country}.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

        print(f"  Created {country}.json ({len(data)} records)")

def create_crime_data(df):
    crimes = df['iccs'].unique()

    for crime in crimes:
        crime_df = df[df['iccs'] == crime]
        data = create_main_dataset(crime_df)

        safe_name = crime.replace('/', '_')
        output_path = os.path.join(OUTPUT_DIR, 'crimes', f'{safe_name}.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

        print(f"  Created {safe_name}.json ({len(data)} records)")

def create_metadata():
    countries_meta = []
    for code, name in COUNTRY_NAMES.items():
        countries_meta.append({
            'code': code,
            'name': name,
            'nameEt': COUNTRY_NAMES_ET.get(code, name)
        })

    with open(os.path.join(OUTPUT_DIR, 'countries.json'), 'w', encoding='utf-8') as f:
        json.dump(countries_meta, f, ensure_ascii=False, indent=2)
    print("Created countries.json")

    crimes_meta = []
    for code, name in ICCS_MAPPING.items():
        category = None
        for cat_key, cat_data in CRIME_CATEGORIES.items():
            if code in cat_data['codes']:
                category = cat_key
                break

        crimes_meta.append({
            'code': code,
            'name': name,
            'category': category
        })

    with open(os.path.join(OUTPUT_DIR, 'crimes.json'), 'w', encoding='utf-8') as f:
        json.dump(crimes_meta, f, ensure_ascii=False, indent=2)
    print("Created crimes.json")

    with open(os.path.join(OUTPUT_DIR, 'categories.json'), 'w', encoding='utf-8') as f:
        json.dump(CRIME_CATEGORIES, f, ensure_ascii=False, indent=2)
    print("Created categories.json")

def create_map_data(df):
    map_data = {}

    years = sorted(df['year'].unique())
    crimes = df['iccs'].unique()

    for year in years:
        map_data[str(year)] = {}
        year_df = df[df['year'] == year]

        for crime in crimes:
            crime_df = year_df[year_df['iccs'] == crime]
            map_data[str(year)][crime] = {
                'per100k': {},
                'absolute': {}
            }

            for _, row in crime_df.iterrows():
                if pd.notna(row['value']):
                    unit_key = 'per100k' if row['unit'] == 'P_HTHAB' else 'absolute'
                    map_data[str(year)][crime][unit_key][row['geo']] = round(row['value'], 2)

    with open(os.path.join(OUTPUT_DIR, 'map-data.json'), 'w', encoding='utf-8') as f:
        json.dump(map_data, f)
    print("Created map-data.json")

def main():
    print("Processing crime data for web platform...")
    print(f"Data directory: {DATA_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    print("Loading crime data...")
    df = load_crime_data()
    print(f"Loaded {len(df)} records")
    print(f"Countries: {df['geo'].nunique()}")
    print(f"Crime types: {df['iccs'].nunique()}")
    print(f"Years: {df['year'].min()} - {df['year'].max()}")
    print()

    print("Creating metadata files...")
    create_metadata()
    print()

    print("Creating map data...")
    create_map_data(df)
    print()

    print("Creating country files...")
    create_country_data(df)
    print()

    print("Creating crime type files...")
    create_crime_data(df)
    print()

    print("Done!")

if __name__ == '__main__':
    main()
