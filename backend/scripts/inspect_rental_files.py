import pandas as pd
import os

files = [
    "/app/data/raw/Dati_locazioni_capoluoghi_2018_2024.csv",
    "/app/data/raw/Locazioni_Res_Trimestrali_04122025.csv"
]

for f in files:
    print(f"\n--- Checking {os.path.basename(f)} ---")
    if not os.path.exists(f):
        print("File not found.")
        continue
    
    try:
        # Try finding delimiter automatically or assume standard
        try:
            df = pd.read_csv(f, sep=';', nrows=5, encoding='latin1')
        except (pd.errors.ParserError, UnicodeDecodeError):
            df = pd.read_csv(f, sep=',', nrows=5, encoding='latin1')
            
        print(f"Columns: {df.columns.tolist()}")
        for i, row in df.iterrows():
            print(f"Row {i}: {row.to_dict()}")
    except Exception as e:
        print(f"Error reading file: {e}")
