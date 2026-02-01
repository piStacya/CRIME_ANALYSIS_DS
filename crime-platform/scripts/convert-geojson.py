import geopandas as gpd
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'assets')
OUTPUT_DIR = os.path.join(BASE_DIR, 'public', 'data', 'geo')

os.makedirs(OUTPUT_DIR, exist_ok=True)

EUROPEAN_COUNTRIES = [
    'AL', 'AT', 'BA', 'BE', 'BG', 'CH', 'CY', 'CZ', 'DE', 'DK',
    'EE', 'EL', 'ES', 'FI', 'FR', 'HR', 'HU', 'IE', 'IS', 'IT',
    'LI', 'LT', 'LU', 'LV', 'ME', 'MK', 'MT', 'NL', 'NO', 'PL',
    'PT', 'RO', 'RS', 'SE', 'SI', 'SK', 'TR', 'XK',
    'UK'
]

def convert_nuts_to_geojson():
    gpkg_path = os.path.join(ASSETS_DIR, 'NUTS_RG_20M_2024_3035.gpkg')

    print(f"Loading {gpkg_path}...")
    gdf = gpd.read_file(gpkg_path)

    print(f"Original CRS: {gdf.crs}")
    print(f"Total features: {len(gdf)}")

    gdf = gdf.to_crs(epsg=4326)

    print(f"Columns: {gdf.columns.tolist()}")

    if 'LEVL_CODE' in gdf.columns:
        gdf_countries = gdf[gdf['LEVL_CODE'] == 0].copy()
    else:
        print("Warning: LEVL_CODE not found, trying to filter by other means...")
        gdf_countries = gdf.copy()

    print(f"Country-level features: {len(gdf_countries)}")

    if 'CNTR_CODE' in gdf_countries.columns:
        code_col = 'CNTR_CODE'
    elif 'NUTS_ID' in gdf_countries.columns:
        code_col = 'NUTS_ID'
    else:
        code_col = gdf_countries.columns[0]
        print(f"Warning: Using {code_col} as country code column")

    gdf_filtered = gdf_countries[gdf_countries[code_col].isin(EUROPEAN_COUNTRIES)].copy()
    print(f"Filtered to {len(gdf_filtered)} European countries")

    gdf_simplified = gdf_filtered.copy()
    gdf_simplified['geometry'] = gdf_simplified['geometry'].simplify(tolerance=0.01, preserve_topology=True)

    keep_cols = ['geometry']
    if 'NUTS_ID' in gdf_simplified.columns:
        keep_cols.append('NUTS_ID')
        gdf_simplified = gdf_simplified.rename(columns={'NUTS_ID': 'id'})
        keep_cols = ['geometry', 'id']
    if 'CNTR_CODE' in gdf_simplified.columns:
        keep_cols.append('CNTR_CODE')
        gdf_simplified = gdf_simplified.rename(columns={'CNTR_CODE': 'code'})
        keep_cols = ['geometry', 'id', 'code'] if 'id' in gdf_simplified.columns else ['geometry', 'code']
    if 'NAME_LATN' in gdf_simplified.columns:
        gdf_simplified = gdf_simplified.rename(columns={'NAME_LATN': 'name'})
        keep_cols.append('name')

    gdf_final = gdf_simplified[keep_cols]

    output_path = os.path.join(OUTPUT_DIR, 'europe-countries.geojson')
    gdf_final.to_file(output_path, driver='GeoJSON')
    print(f"Saved to {output_path}")

    with open(output_path, 'r') as f:
        geojson = json.load(f)

    def round_coords(coords):
        if isinstance(coords[0], (list, tuple)):
            return [round_coords(c) for c in coords]
        else:
            return [round(c, 3) for c in coords]

    for feature in geojson['features']:
        geom = feature['geometry']
        if geom['type'] == 'Polygon':
            geom['coordinates'] = round_coords(geom['coordinates'])
        elif geom['type'] == 'MultiPolygon':
            geom['coordinates'] = round_coords(geom['coordinates'])

    minified_path = os.path.join(OUTPUT_DIR, 'europe-countries.min.json')
    with open(minified_path, 'w') as f:
        json.dump(geojson, f, separators=(',', ':'))
    print(f"Saved minified version to {minified_path}")

    original_size = os.path.getsize(output_path) / 1024
    minified_size = os.path.getsize(minified_path) / 1024
    print(f"Original size: {original_size:.1f} KB")
    print(f"Minified size: {minified_size:.1f} KB")

def convert_country_boundaries():
    gpkg_path = os.path.join(ASSETS_DIR, 'CNTR_RG_10M_2024_3035.gpkg')

    if not os.path.exists(gpkg_path):
        print(f"Country boundaries file not found: {gpkg_path}")
        return

    print(f"\nLoading country boundaries from {gpkg_path}...")
    gdf = gpd.read_file(gpkg_path)

    print(f"Original CRS: {gdf.crs}")
    print(f"Columns: {gdf.columns.tolist()}")
    print(f"Total features: {len(gdf)}")

    gdf = gdf.to_crs(epsg=4326)

    if 'CNTR_ID' in gdf.columns:
        code_col = 'CNTR_ID'
    elif 'ISO3_CODE' in gdf.columns:
        code_col = 'ISO3_CODE'
    else:
        code_col = gdf.columns[0]

    print(f"Using {code_col} as country identifier")
    print(f"Available countries: {gdf[code_col].unique().tolist()}")

    gdf_filtered = gdf[gdf[code_col].isin(EUROPEAN_COUNTRIES)].copy()
    print(f"Filtered to {len(gdf_filtered)} countries")

    gdf_filtered['geometry'] = gdf_filtered['geometry'].simplify(tolerance=0.01, preserve_topology=True)

    gdf_filtered = gdf_filtered.rename(columns={code_col: 'id'})
    if 'NAME_ENGL' in gdf_filtered.columns:
        gdf_filtered = gdf_filtered.rename(columns={'NAME_ENGL': 'name'})

    keep_cols = ['id', 'geometry']
    if 'name' in gdf_filtered.columns:
        keep_cols.append('name')

    gdf_final = gdf_filtered[keep_cols]

    output_path = os.path.join(OUTPUT_DIR, 'europe-countries-alt.geojson')
    gdf_final.to_file(output_path, driver='GeoJSON')
    print(f"Saved to {output_path}")

def main():
    print("Converting GeoPackage files to GeoJSON...")
    print()

    try:
        convert_nuts_to_geojson()
    except Exception as e:
        print(f"Error converting NUTS: {e}")

    print()

    try:
        convert_country_boundaries()
    except Exception as e:
        print(f"Error converting country boundaries: {e}")

    print("\nDone!")

if __name__ == '__main__':
    main()
