import sys
import os
import random
import pandas as pd
from app.core.database import SessionLocal
from app.models.geography import Municipality, Province, Region

def generate_full_demography_data():
    db = SessionLocal()
    try:
        # Get all municipalities
        municipalities = db.query(Municipality).all()
        
        print(f"Found {len(municipalities)} municipalities.")
        
        data = []
        for mun in municipalities:
            # Base income (Milan/Rome higher)
            reg_bonus = 5000 if mun.province.region.code in ["03", "12"] else 0
            avg_income = 18000 + reg_bonus + random.uniform(0, 15000)
            
            pop = mun.population if mun.population else random.randint(1000, 50000)
            
            data.append([
                mun.code,
                pop,
                round(avg_income, 2)
            ])
            
        df = pd.DataFrame(data, columns=[
            "Codice_Comune", "Popolazione", "Reddito_Medio"
        ])
        
        data_dir = "data/raw"
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, "demographics_full_mvp_regions.xlsx")
        df.to_excel(file_path, index=False)
        print(f"Full demography data created at: {file_path} with {len(df)} rows.")
        
    finally:
        db.close()

if __name__ == "__main__":
    generate_full_demography_data()
