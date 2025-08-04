import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder

# Load and clean data
leads = pd.read_csv("lead_data.csv")
lead_opps = pd.read_csv("lead_opportunity_data.csv", low_memory=False)

lead_opps.drop_duplicates(inplace=True)
leads.drop_duplicates(subset=['Lead_ID'], inplace=True)

lead_opps['Lead_Date'] = pd.to_datetime(lead_opps['Lead_Date'], errors='coerce')
leads['Lead_Date'] = pd.to_datetime(leads['Lead_Date'], errors='coerce')

# Keep latest opportunity per lead
lead_opps = lead_opps.sort_values(['Lead_ID', 'Opportunity_ID', 'Lead_Date'], ascending=[True, True, False])
lead_opps = lead_opps.drop_duplicates(subset=['Lead_ID', 'Opportunity_ID'], keep='first')

# Merge datasets and prepare target
merged = lead_opps.merge(
    leads[['Lead_ID', 'Lead_Source', 'Lead_Date']],
    on='Lead_ID', how='left', suffixes=('_opp', '_lead')
)
merged['Lead_Source'] = merged['Lead_Source_lead'].combine_first(merged['Lead_Source_opp'])
merged['Lead_Date'] = pd.to_datetime(merged['Lead_Date_lead'].combine_first(merged['Lead_Date_opp']), errors='coerce')
merged.drop_duplicates(subset=['Lead_ID', 'Opportunity_ID'], inplace=True)
merged['target'] = (merged.get('Sales_Stage_Status') == 'Won').astype(np.int8)

# Define product groups and count product presence
product_groups = {
    "Category_A": ["Product_1", "Product_2", "Product_3"],
    "Category_B": ["Product_4", "Product_5"],
}
for group, products in product_groups.items():
    valid = [p for p in products if p in merged.columns]
    merged[group + "_count"] = merged[valid].notna().sum(axis=1).astype(np.int16)
count_cols = [g + "_count" for g in product_groups]
merged['num_product_categories'] = (merged[count_cols] > 0).sum(axis=1).astype(np.int8)

# Create feature dataframe
features = pd.DataFrame(index=merged.index)
features['lead_month'] = merged['Lead_Date'].dt.month.fillna(0).astype(np.int8)
features['lead_quarter'] = merged['Lead_Date'].dt.quarter.fillna(0).astype(np.int8)
features['lead_weekday'] = merged['Lead_Date'].dt.weekday.fillna(-1).astype(np.int8)
features['lead_is_weekend'] = features['lead_weekday'].isin([5, 6]).astype(np.int8)

for group in product_groups:
    valid = [p for p in product_groups[group] if p in merged.columns]
    features[group] = merged[valid].apply(pd.to_numeric, errors='coerce').notna().any(axis=1).astype(np.int8) if valid else 0

features['num_product_categories'] = merged['num_product_categories']
features['lead_source_combined'] = merged['Lead_Source']

# One-hot encode categorical features
def encode_feature(df, col):
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=True, dtype=np.int8)
    encoded = encoder.fit_transform(df[[col]])
    return pd.DataFrame.sparse.from_spmatrix(encoded, columns=encoder.get_feature_names_out([col]), index=df.index)

encoded_lead_source = encode_feature(features, 'lead_source_combined')
encoded_month = encode_feature(features, 'lead_month')
encoded_quarter = encode_feature(features, 'lead_quarter')
encoded_weekday = encode_feature(features, 'lead_weekday')

# Include IDs if present
id_cols = merged[['Lead_ID', 'Opportunity_ID']] if all(c in merged.columns for c in ['Lead_ID', 'Opportunity_ID']) else pd.DataFrame(index=merged.index)

# Drop encoded raw columns and combine all features
features = features.drop(columns=['lead_source_combined', 'lead_month', 'lead_quarter', 'lead_weekday'], errors='ignore')

final_features = pd.concat([
    encoded_lead_source,
    encoded_month,
    encoded_quarter,
    encoded_weekday,
    features,
    id_cols,
    merged[['target']]
], axis=1)

final_features = final_features.loc[:, ~final_features.columns.duplicated()]
final_features.to_pickle("final_features.pkl")

