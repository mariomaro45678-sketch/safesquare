import sys
import os
import random
import pandas as pd
from app.core.database import SessionLocal
from app.models.geography import Municipality, Province, Region

def generate_full_risk_data():
    db = SessionLocal()
    try:
        # Get all municipalities
        municipalities = db.query(Municipality).all()
        
        print(f"Found {len(municipalities)} municipalities in target regions.")
        
        data = []
        for mun in municipalities:
            # Randomly generate some realistic risk levels
            reg_code = mun.province.region.code
            
            # Risk weights by region
            # Campania (15) has higher seismic risk
            # Emilia-Romagna (08) has higher flood risk
            seismic_base = 60 if reg_code == "15" else 20
            flood_base = 50 if reg_code == "08" else 20
            
            seismic_score = min(100, seismic_base + random.uniform(0, 40))
            flood_score = min(100, flood_base + random.uniform(0, 40))
            landslide_score = random.uniform(5, 60)
            
            # Record for Seismic
            data.append([mun.code, "seismic", "Medium" if seismic_score < 70 else "High", seismic_score, 0.15, 0])
            # Record for Flood
            data.append([mun.code, "flood", "Low" if flood_score < 40 else "Medium", flood_score, 0, flood_score/5])
            # Record for Landslide
            data.append([mun.code, "landslide", "Low" if landslide_score < 30 else "Medium", landslide_score, 0, landslide_score/4])
            
        df = pd.DataFrame(data, columns=[
            "Codice_Comune", "Tipo_Rischio", "Livello", "Score", "PGA", "Area_Pct"
        ])
        
        data_dir = "data/raw"
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, "risks_full_mvp_regions.xlsx")
        df.to_excel(file_path, index=False)
        print(f"Full risk data created at: {file_path} with {len(df)} rows.")
        
    finally:
        db.close()

if __name__ == "__main__":
    generate_full_risk_data()
