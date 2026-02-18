import sys
import os
import random
import pandas as pd
from datetime import date
from app.core.database import SessionLocal
from app.models.geography import Municipality, Province, Region

def generate_full_omi_data():
    db = SessionLocal()
    try:
        # Get all municipalities
        municipalities = db.query(Municipality).all()
        
        print(f"Found {len(municipalities)} municipalities.")
        
        data = []
        # Semesters to generate
        semesters = [
            (2021, 1), (2021, 2),
            (2022, 1), (2022, 2),
            (2023, 1)
        ]
        
        for mun in municipalities:
            # Create a zone code based on municipality code
            zone_code = f"{mun.code}_Z1"
            
            # Base price for the municipality (randomly assigned based on population/region)
            # higher for Milan/Rome regions
            reg_bonus = 1000 if mun.province.region.code in ["03", "12"] else 0
            base_price = 1500 + reg_bonus + random.uniform(0, 2000)
            
            # Historical trend (simulating growth)
            current_price = base_price
            for year, sem in semesters:
                # Add some growth/noise
                growth = random.uniform(-0.02, 0.05)
                current_price = current_price * (1 + growth)
                
                data.append([
                    mun.code,
                    mun.name,
                    zone_code,
                    "Residenziale",
                    year,
                    sem,
                    round(current_price * 0.8, 2),
                    round(current_price * 1.2, 2),
                    round(current_price, 2)
                ])
            
        df = pd.DataFrame(data, columns=[
            "Codice_Comune", "Comune", "Zona_OMI", "Tipo", "Anno", "Semestre", "Min", "Max", "Medio"
        ])
        
        data_dir = "data/raw"
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, "omi_full_mvp_regions_2021_2023.xlsx")
        df.to_excel(file_path, index=False)
        print(f"Full OMI data created at: {file_path} with {len(df)} rows.")
        
    finally:
        db.close()

if __name__ == "__main__":
    generate_full_omi_data()
