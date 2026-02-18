import pandas as pd
import os

path = "data/raw/omi_full_mvp_regions_2021_2023.xlsx"
if not os.path.exists(path):
    print(f"File not found: {path}")
    exit(1)

print(f"Loading {path}...")
df = pd.read_excel(path)
print(f"Columns: {df.columns.tolist()}")

# Check for Transaction Type column
possible_cols = [c for c in df.columns if "stato" in c.lower() or "mercato" in c.lower() or "us" in c.lower()]
print(f"Possible Market Columns: {possible_cols}")

for col in possible_cols:
    print(f"Unique values in {col}: {df[col].unique()}")

# Check sample row
print("Sample Row:")
print(df.iloc[0].to_dict())
