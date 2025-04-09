import pandas as pd
import numpy as np
from sodapy import Socrata
import googlemaps
import geopandas as gpd
from shapely.geometry import Point
# import API key from uncommited file
from constants import google_maps_api_key

# ----- functions -----

def get_lat_long(row):

    try:
        address = (
            row['street_name'] + 
            str(row['intersecting_street']).replace('nan', '') + ' ' + 
            row['violation_county']
        ).replace('@', '&')

        print(address)

        geocode_result = gmaps.geocode(address)

        return (
            str(geocode_result[0]['geometry']['location']['lat']) + 
            ',' + 
            str(geocode_result[0]['geometry']['location']['lng'])
        )
    except:
        print('none found')
        return 'null'
    
def clean_lat_longs(df, borough_boundaries):
    # remove rows where lat longs don't fall within any borough boundaries
    
    # Convert lat/long columns to numeric, replacing 'null' with NaN
    df['lat'] = pd.to_numeric(df['lat'].replace('null', np.nan), errors='coerce')
    df['long'] = pd.to_numeric(df['long'].replace('null', np.nan), errors='coerce')
    
    # Drop rows with NaN coordinates
    df = df.dropna(subset=['lat', 'long'])
    
    # Create a GeoDataFrame with Point geometry from lat/long columns
    geometry = [Point(xy) for xy in zip(df['long'], df['lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    # Ensure borough_boundaries has the same CRS
    borough_boundaries = borough_boundaries.to_crs("EPSG:4326")
    
    # Create a spatial join to find points within borough boundaries
    joined = gpd.sjoin(gdf, borough_boundaries, how="inner", predicate="within")
    
    # Return the original dataframe filtered to only include points within boroughs
    return df[df.index.isin(joined.index)]

# ----- data read-in -----

# Read borough boundaries
borough_boundaries = gpd.read_file('../raw/Borough Boundaries.geojson')

sparse_df = pd.read_csv('../processed/school_zone_violations_sparse.csv')

full_df = pd.read_csv('../processed/school_zone_violations.csv')


# ---- sample ----- 

sample_plates = sparse_df[sparse_df.row_pct >= 0.99].plate_id.sample(10).tolist()

# add two outliers manually
sample_plates = list(set((
    sample_plates + ['LCM8254', 'HSU6447']
)))

# ---- plate lookup ----- 

# resources:
# - https://github.com/xmunoz/sodapy?tab=readme-ov-file#getdataset_identifier-content_typejson-kwargs
# - https://dev.socrata.com/foundry/data.cityofnewyork.us/pvqr-7yc4

gmaps = googlemaps.Client(key=google_maps_api_key)
client = Socrata("data.cityofnewyork.us", None)

# grab records
results = pd.concat(
    [
        pd.DataFrame.from_records(
            client.get("pvqr-7yc4", plate_id=sample_plate, 
            where='date_trunc_ymd(issue_date) BETWEEN "2024-01-01" AND "2024-12-31"',
            violation_code='36')
        )
        for sample_plate in sample_plates
    ],
    ignore_index=True
)
# clean counties
results['violation_county'] = results['violation_county'].replace(
                {'BK': 'Brooklyn, New York', 
                 'BX': 'Bronx, New York', 
                 'QN': 'Queens, New York', 
                 'MN': 'Manhattan, New York', 
                 'ST': 'Staten Island, New York', 
                 })


# get their lat long coordinates 
results['lat_long'] = results.apply(get_lat_long, axis = 1)
results['lat'] = results.lat_long.str.split(',', expand=True)[0]
results['long'] = results.lat_long.str.split(',', expand=True)[1]

# remove rows where lat longs don't fall within any borough boundaries
results = clean_lat_longs(results, borough_boundaries)

# correct date
results['issue_dt'] = pd.to_datetime(results.issue_date)

# ---- output ----- 
results.to_csv('../../static/data/repeat_offenders_lat_long_sample.csv', index = False)