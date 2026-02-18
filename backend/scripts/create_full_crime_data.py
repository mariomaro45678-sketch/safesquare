import sys
import os
import random
import pandas as pd
from app.core.database import SessionLocal
from app.models.geography import Municipality, Province, Region

def generate_full_crime_data():
    db = SessionLocal()
    try:
        # Get all municipalities
        municipalities = db.query(Municipality).all()
        
        print(f"Found {len(municipalities)} municipalities.")
        
        data = []
        for mun in municipalities:
            # Randomly generate some realistic crime data
            # Cities generally have higher crime rates
            base_rate = 30 + random.uniform(0, 40) if mun.population and mun.population > 50000 else 10 + random.uniform(0, 20)
            
            total = base_rate + random.uniform(-5, 5)
            violent = total * random.uniform(0.05, 0.15)
            property_crimes = total * random.uniform(0.5, 0.7)
            
            # Granular real estate sensitive crimes
            burglary = property_crimes * random.uniform(0.2, 0.4)
            vandalism = property_crimes * random.uniform(0.1, 0.2)
            theft = property_crimes * random.uniform(0.4, 0.6)
            
            data.append([
                mun.code,
                2022,
                round(total, 2),
                round(violent, 2),
                round(property_crimes, 2),
                round(burglary, 2),
                round(vandalism, 2),
                round(theft, 2)
            ])
            
        df = pd.DataFrame(data, columns=[
            "Codice_Comune", "Anno", "Total_Crimes_Per_1000", "Violent_Crimes_Per_1000", 
            "Property_Crimes_Per_1000", "Burglary_Rate", "Vandalism_Rate", "Theft_Rate"
        ])
        
        data_dir = "data/raw"
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, "crime_full_mvp_regions.xlsx")
        df.to_excel(file_path, index=False)
        print(f"Full crime data created at: {file_path} with {len(df)} rows.")
        
    finally:
        db.close()

if __name__ == "__main__":
    generate_full_crime_data()
