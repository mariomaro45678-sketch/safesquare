import sys
import os
import random
import pandas as pd
from app.core.database import SessionLocal
from app.models.geography import Municipality, Province, Region

def generate_full_pollution_data():
    db = SessionLocal()
    try:
        # Get all municipalities
        municipalities = db.query(Municipality).all()
        
        print(f"Found {len(municipalities)} municipalities.")
        
        data = []
        for mun in municipalities:
            # Randomly generate some realistic pollution data
            # Northern Italy (Po Valley) has higher pollution
            region_code = mun.province.region.code
            is_northern = region_code in ["01", "03", "05", "06", "08"] # Piemonte, Lombardia, Veneto, Friuli, ER
            
            # Po Valley bonus
            po_valley_bonus = 15 if is_northern else 0
            
            pm25 = 10 + po_valley_bonus + random.uniform(0, 10)
            pm10 = pm25 * 1.4 + random.uniform(0, 5)
            no2 = 25 + random.uniform(0, 20) if (mun.population and mun.population > 50000) else 10 + random.uniform(0, 10)
            
            # Simplified AQI (0-100)
            aqi = min(100, (pm25 / 25 * 40) + (no2 / 40 * 40) + (pm10 / 50 * 20))
            
            level = "Low"
            if aqi > 70: level = "High"
            elif aqi > 40: level = "Moderate"
            
            data.append([
                mun.code,
                round(pm25, 2),
                round(pm10, 2),
                round(no2, 2),
                round(aqi, 2),
                level,
                2023
            ])
            
        df = pd.DataFrame(data, columns=[
            "Codice_Comune", "PM2.5_Avg", "PM10_Avg", "NO2_Avg", "AQI_Index", "Risk_Level", "Anno"
        ])
        
        data_dir = "data/raw"
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, "pollution_full_national.xlsx")
        df.to_excel(file_path, index=False)
        print(f"Full pollution data created at: {file_path} with {len(df)} rows.")
        
    finally:
        db.close()

if __name__ == "__main__":
    generate_full_pollution_data()
