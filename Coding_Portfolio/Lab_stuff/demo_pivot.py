import pandas as pd

# Load data
df = pd.read_csv("demographics.csv")

# Clean and normalize columns
for col in ['Sex', 'Race', 'EthnicityRaw']:
    df[col] = df[col].fillna('Unknown').str.strip()

race_map = {
    'AI/AN': 'American Indian/Alaska Native',
    'A': 'Asian',
    'NH/PI': 'Native Hawaiian or Other Pacific Islander',
    'B/AA': 'Black or African American',
    'W': 'White',
    'MR': 'More than One Race',
    'B/AA+W': 'More than One Race',
    'Asian+W': 'More than One Race',
    'Other': 'Other',
    'Unknown': 'Unknown',
    'Black or African American': 'Black or African American',
}
df['Race'] = df['Race'].replace(race_map)

ethnicity_map = {
    'N': 'Not Hispanic or Latino',
    'Y': 'Hispanic or Latino',
    'Unknown': 'Unknown'
}
df['Ethnicity'] = df['EthnicityRaw'].map(ethnicity_map).fillna('Unknown')

# Create pivot table
pivot = pd.pivot_table(
    df,
    index='Race',
    columns=['Ethnicity', 'Sex'],
    values='RecordID',
    aggfunc='count',
    fill_value=0
)

# Add totals
pivot[('Total', 'Total')] = pivot.sum(axis=1)
pivot.loc['Total'] = pivot.sum()

# Reorder rows and columns
preferred_order = [
    'American Indian/Alaska Native',
    'Asian',
    'Native Hawaiian or Other Pacific Islander',
    'Black or African American',
    'White',
    'More than One Race',
    'Other',
    'Unknown',
    'Total'
]
pivot = pivot.reindex(preferred_order)

cols = list(pivot.columns)
cols_no_total = [c for c in cols if c != ('Total', 'Total')]
cols_no_total_sorted = sorted(cols_no_total)
ordered_columns = cols_no_total_sorted + [('Total', 'Total')]
pivot = pivot[ordered_columns]

pivot.to_csv("demographics_summary.csv")

# Check totals
print(f"Total records: {len(df)}")
print(f"Pivot total: {pivot.loc['Total', ('Total', 'Total')]}")


