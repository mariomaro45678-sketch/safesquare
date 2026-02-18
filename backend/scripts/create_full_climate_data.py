import sys
import os
import random
import pandas as pd
from app.core.database import SessionLocal
from app.models.geography import Municipality, Province, Region

def generate_full_climate_data():
    db = SessionLocal()
    try:
        # Get all municipalities
        municipalities = db.query(Municipality).all()
        
        print(f"Found {len(municipalities)} municipalities.")
        
        data = []
        for mun in municipalities:
            province_code = mun.province.code if mun.province else ""
            
            # Coastal cities might have sea level rise
            is_coastal = province_code in ["010", "011", "045", "046", "047", "048", "049", "050", "053", "058", "059", "060", "063", "064", "065"] # Simple approximation
            
            # Target 2050 - RCP 8.5
            temp_change = 1.5 + random.uniform(0.5, 1.5)
            rainfall_incr = 10 + random.uniform(5, 15)
            slr = random.uniform(20, 40) if is_coastal else 0
            
            data.append([
                mun.code,
                "RCP8.5",
                2050,
                round(temp_change, 1),
                round(temp_change + 1.2, 1),
                random.randint(20, 45),
                round(random.uniform(-10, 5), 1),
                round(rainfall_incr, 1),
                round(random.uniform(10, 30), 1),
                round(slr, 1),
                round(1.0 + (rainfall_incr / 100), 2)
            ])
            
        df = pd.DataFrame(data, columns=[
            "Codice_Comune", "Scenario", "Target_Year", "Avg_Temp_Change", "Max_Temp_Change", 
            "Heatwave_Days_Increase", "Avg_Precipitation_Change", "Extreme_Rainfall_Increase", 
            "Drought_Risk_Increase", "Sea_Level_Rise_Cm", "Flood_Risk_Multiplier"
        ])
        
        data_dir = "data/raw"
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, "climate_full_mvp_regions.xlsx")
        df.to_excel(file_path, index=False)
        print(f"Full climate data created at: {file_path} with {len(df)} rows.")
        
    finally:
        db.close()

if __name__ == "__main__":
    generate_full_climate_data()
