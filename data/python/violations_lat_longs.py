import pandas as pd
import numpy as np
from sodapy import Socrata
import googlemaps
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
    

# ----- data read-in -----

sparse_df = pd.read_csv('../processed/school_zone_violations_sparse.csv')

# ---- sample ----- 

sample_plates = sparse_df[sparse_df.row_pct >= 0.99].plate_id.sample(10).tolist()

# add two outliers manually
sample_plates = list(set((
    sample_plates + ['LCM8254', 'TRK8026']
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
            client.get("pvqr-7yc4", plate_id=sample_plate, violation_code='36')
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

# correct date
results['issue_dt'] = pd.to_datetime(results.issue_date)

# ---- output ----- 
results.to_csv('../processed/repeat_offenders_lat_long_sample.csv', index = False)
results.to_csv('../../static/data/repeat_offenders_lat_long_sample.csv', index = False)