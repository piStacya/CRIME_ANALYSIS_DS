import pandas as pd
import os
import shutil

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


def process_all_files(source_directory, destination_directory):
    # kõikide .tsv failide töötlemine ühes kaustas
    # kui failis on geo veerg siis toimuvad asendused
    # kui mitte - siis läheb fail muutmata kujul sihtkausta
    os.makedirs(destination_directory, exist_ok=True)

    for filename in os.listdir(source_directory):
        if not filename.lower().endswith('.tsv'):
            continue

        input_path = os.path.join(source_directory, filename)
        output_path = os.path.join(destination_directory, filename)

        print(f"\n--- Faili töötlemine: {filename} ---")

        try:
            df = pd.read_csv(input_path, sep='\t', dtype={'geo': str}, low_memory=False)

            if 'geo' in df.columns:
                print(f"'geo' veerg leitud. Riigikoodide asendamine algab...")
                df['geo'] = df['geo'].apply(get_country_name)
                df.to_csv(output_path, sep='\t', index=False)
                print(f"Muudetud fail on salvestatud asukohta: {output_path}")
            else:
                print(f"Veergu 'geo' ei leitud. Fail kopeeritakse muutmata kujul...")
                shutil.copy(input_path, output_path)
                print(f"Fail on kopeeritud asukohta: {output_path}")

        except Exception as e:
            print(f"Tekkis viga faili {filename} töötlemisel: {e}")
            print("Järgmine fail.")


# käivitamine
if __name__ == "__main__":
    source_dir = '../data/cleanedDatasets/nan_rows'
    destination_dir = '../data/cleanedDatasets/nan_rows/country_names_changed'

    process_all_files(source_dir, destination_dir)