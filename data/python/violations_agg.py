import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ----- functions -----
def clean_cols(df):
   df.columns  = [c.lower().replace(' ', '_') for c in df.columns]
   
   return df 

def clean_times(df):
    
    df['violation_time'] = df['violation_time'].str.replace('A', 'AM').str.replace('P', 'PM')
    

    df['violation_time'] = df['violation_time'].str.replace(r'^00', '12', regex=True)

    df['violation_time'] = pd.to_datetime(df['violation_time'], format='%I%M%p', errors = 'coerce')
    
    df['school_hours'] = (
       (df['violation_time'] >= pd.to_datetime('0730AM', format='%I%M%p')) & 
       (df['violation_time'] <= pd.to_datetime('0430PM', format='%I%M%p'))
     )
    
    return df 


# ----- data read-in -----

# violation codes
violation_codes = pd.read_excel('../raw/ParkingViolationCodes_January2020.xlsx')
violation_codes = clean_cols(violation_codes)
violation_codes = violation_codes.rename(columns = {
    'manhattan__96th_st._&_below\n(fine_amount_$)':'manhattan_96_below_fine', 
    'all_other_areas\n(fine_amount_$)' : 'all_other_fine'
})

# parking violations - in chunks
chunk_size = 500_000
all_chunks = pd.DataFrame()
for chunk in pd.read_csv('../raw/Parking_Violations_Issued_-_Fiscal_Year_2024_20250115.csv', chunksize=chunk_size):
    
    # clean up chunk columns and filter out blanks
    chunk = clean_cols(chunk)
    chunk = clean_times(chunk)
    chunk = chunk[chunk.plate_id != 'BLANKPLATE']

    # aggregate
    agg_chunk = chunk.groupby(
        ['plate_id', 'registration_state', 'plate_type', 'violation_code', 'violation_county']).agg( 
        violations = ('summons_number', 'count'),
        school_hour_violations = ('school_hours', 'sum')
    ).reset_index()
    
    # add to master df
    all_chunks = pd.concat([agg_chunk, all_chunks])

# ----- data cleaning -----

borough_county_mapping = {
    'Brooklyn': ['BK', 'K', 'KINGS'], 
    'Manhattan': ['NY', 'MN', 'KNGS'], 
    'Queens': ['QN', 'Q', 'QNS', 'QUEEN'],
    'Bronx': ['BX', 'Bronx', 'BRONX'],
    'Staten Island': ['ST', 'R', 'Rich', 'RICH']
}

# Invert the mapping to get county to borough
county_to_borough = {
    county.upper(): borough  # Using uppercase to ensure case-insensitive matching
    for borough, counties in borough_county_mapping.items()
    for county in counties
}

def map_county_to_borough(county):
    return county_to_borough.get(county.upper(), 'Unknown')  # 'Unknown' for unmapped counties

all_chunks['violation_borough'] = all_chunks.violation_county.apply(map_county_to_borough)

# ----- aggregation -----

# group things together at the plate/borough level first
all_chunks = all_chunks.groupby(
    ['plate_id', 'registration_state', 'plate_type', 'violation_code', 'violation_borough']).agg(
        violations = ('violations', 'sum'), 
        school_hour_violations = ('school_hour_violations', 'sum')
).reset_index()

# now add in which borough they commit most violations in
borough_maxes = all_chunks.loc[all_chunks.groupby(
    ['plate_id', 'registration_state', 'plate_type', 'violation_code'])['violations'].idxmax()][['plate_id', 'registration_state', 'plate_type', 'violation_code', 'violation_borough']]

all_chunks_boroughed = all_chunks.groupby(
    ['plate_id', 'registration_state', 'plate_type', 'violation_code']).agg(
        violations = ('violations', 'sum'),
        school_hour_violations = ('school_hour_violations', 'sum')
        ).reset_index().merge(
    borough_maxes, 
    how = 'left', 
    on = ['plate_id', 'registration_state', 'plate_type', 'violation_code'])

# add in code information
all_chunks_boroughed = all_chunks_boroughed.merge(violation_codes, how = 'left', on = 'violation_code')

# ----- compute fines paid -----

# red lights and school zones get $50 fines wherever they are in the city
all_chunks_boroughed['fines'] = np.where(
    all_chunks_boroughed.violation_code.isin([36,7]), 
    all_chunks_boroughed.all_other_fine * all_chunks_boroughed.violations,
    np.nan
)

# ----- save output -----

all_chunks_boroughed.to_csv('../processed/parking_violations_agg.csv', index = False)


