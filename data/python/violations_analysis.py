import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sodapy import Socrata
import googlemaps

# ----- functions -----
def generate_shares(df, violation_code):
    sub_df = df[df.violation_code == violation_code].reset_index()
    sub_df = sub_df.sort_values('violations')

    sub_df['row_num'] = range(len(sub_df))
    sub_df['row_pct'] = sub_df.row_num / sub_df.shape[0]

    sub_df['cum_share'] = sub_df.violations.cumsum() / sub_df.violations.sum()

    return sub_df

def visualize_distribution(df, violation_code) :

    sub_df = generate_shares(df, violation_code)

    violation_desc = sub_df.iloc[0].violation_description

    sub_df.plot(x = 'row_pct', y = 'cum_share')
    plt.title(f'violation code: {violation_desc}')

def bin_violations(violations):
    match violations:
        case _ if violations <=1 :
            return '1'
        case _ if 1 < violations <= 5:
            return '1-5'
        case _ if 5 < violations <= 10:
            return '6-10'
        case _ if 10 < violations <= 15:
            return '11-15'
        case _ if  15 < violations <= 50:
            return '16-50'
        case _ if  violations > 50:
            return '51+'


# Define a function to calculate step size with quadratic interpolation
def decreasing_step_quadratic(index, total_rows, max_step=500, min_step=100):
    """
    Calculate step size based on the index using a quadratic scale.
    Starts with `max_step` and decreases to `min_step`, accelerating towards the end.
    
    Parameters:
        index (int): Current row index.
        total_rows (int): Total number of rows in the DataFrame.
        max_step (int): Maximum step size (start of the DataFrame).
        min_step (int): Minimum step size (end of the DataFrame).
    
    Returns:
        int: Step size at the given index.
    """
    # Normalize the index to a range of 0 to 1
    progress = index / total_rows
    
    # Apply quadratic interpolation: (1 - progress^2) decreases slowly at first, then faster
    step = max_step - (max_step - min_step) * (progress ** 4)
    
    return int(step)

def stat_report(df, name):

    print(f'report for {name}')

    print(f"""
        share of violations: 
        {round(1 - df.cum_share.min(), 2)}
        """)
    
    print(f"""
        school hour rate: 
        {round(df.school_zone_school_hour_violations.sum() / df.school_zone_violations.sum(), 2)}
        """)

    print(f"""
        minimum violations: 
        {df.school_zone_violations.min()}
        """)
    
    print(f"""
        average violations: 
        {df.school_zone_violations.mean()}
        """)
    
    print(f"""
        median violations: 
        {df.school_zone_violations.median()}
        """)

    print(f"""
        total drivers: 
        {df.plate_id.nunique()}
        """)

    print(f"""
        total violations%: 
        {df.school_zone_violations.sum()}
        """)


# ----- data read-in -----

violations_agg = pd.read_csv('../processed/parking_violations_agg.csv')

# ---- categorize ----- 
red_light_agg = generate_shares(violations_agg, 7).rename(
    columns = {
        'violations':'red_light_violations',
        'school_hour_violations':'red_light_school_hour_violations'}
)
school_zone_agg = generate_shares(violations_agg, 36).rename(
    columns = {
        'violations':'school_zone_violations',
        'school_hour_violations':'school_zone_school_hour_violations'}   
)

school_zone_agg['school_zone_violations_binned'] = school_zone_agg.school_zone_violations.apply(bin_violations)

# ---- merge ----- 

merged = school_zone_agg.merge(
    red_light_agg[['plate_id', 'red_light_violations']], 
    how = 'left', 
    on = 'plate_id')
merged['red_light_violations'] = merged.red_light_violations.fillna(0)

# ----- save output -----

merged.to_csv('../processed/school_zone_violations.csv', index = False)

merged.iloc[::1000, :].to_csv('../processed/school_zone_violations_sparse.csv', index = False)

# Initialize variables
selected_indices = []
i = 0

# Iterate to select rows
while i < len(merged):
    selected_indices.append(i)
    step = decreasing_step_quadratic(i, len(merged), max_step=10000, min_step=1000)
    i += step

# add in one tail end obs
selected_indices.append(merged.iloc[-1].name)

# Select rows based on calculated indices
sparse_gradual_merged = merged.iloc[selected_indices]

# Show the result
sparse_gradual_merged.to_csv('../processed/school_zone_violations_sparser.csv', index = False)

# ----- visualize -----

visualize_distribution(violations_agg, 7)
visualize_distribution(violations_agg, 36)

# ----- mean comparison -----

merged.red_light_violations.mean()

merged.groupby('school_zone_violations_binned').agg(
    red_light_violations = ('red_light_violations', 'mean'), 
    n = ('plate_id', 'count')).reset_index()

# ----- all stats -----

stat_report(school_zone_agg, 'all drivers')

# ----- top stats -----

stat_report(school_zone_agg[school_zone_agg.row_pct >= 0.95], 'top 5% of drivers')

stat_report(school_zone_agg[school_zone_agg.row_pct >= 0.98], 'top 2% of drivers')

stat_report(school_zone_agg[school_zone_agg.row_pct >= 0.99], 'top 1% of drivers')

# ----- borough breakdown -----


print(f"""
      boroughs for all drivers
      {school_zone_agg.violation_borough.value_counts(normalize=True)}
      """)


print(f"""
      boroughs for top 5%
      {school_zone_agg[school_zone_agg.row_pct >= 0.95].violation_borough.value_counts(normalize=True)}
      """)

print(f"""
      boroughs for top 1%
      {school_zone_agg[school_zone_agg.row_pct >= 0.99].violation_borough.value_counts(normalize=True)}
      """)