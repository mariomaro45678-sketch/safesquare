import csv
import os
from app.core.database import SessionLocal
from app.models.geography import Municipality
from app.models.risk import FloodRisk, LandslideRisk
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ispra_risk_sample.csv")

def ingest_ispra():
    db = SessionLocal()
    try:
        if not os.path.exists(DATA_PATH):
            logger.error(f"File not found: {DATA_PATH}")
            return

        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                name = row['Municipality']
                # Fuzzy match isn't needed if names are exact, but be careful
                mun = db.query(Municipality).filter(func.lower(Municipality.name) == name.lower()).first()
                
                if mun:
                    # Parse Data
                    flood_pct = float(row.get('Flood_High_Pct', 0))
                    landslide_pct = float(row.get('Landslide_P3_P4_Pct', 0))
                    
                    # 1. FLOOD RISK
                    f_risk = db.query(FloodRisk).filter(FloodRisk.municipality_id == mun.id).first()
                    if not f_risk:
                        f_risk = FloodRisk(municipality_id=mun.id)
                        db.add(f_risk)
                    
                    f_risk.high_hazard_area_pct = flood_pct
                    f_risk.risk_score = min(100.0, flood_pct * 1.5) # Scale up: 66% area = 100 score
                    f_risk.risk_level = "High" if flood_pct > 20 else "Medium"
                    
                    # 2. LANDSLIDE RISK
                    l_risk = db.query(LandslideRisk).filter(LandslideRisk.municipality_id == mun.id).first()
                    if not l_risk:
                        l_risk = LandslideRisk(municipality_id=mun.id)
                        db.add(l_risk)
                        
                    l_risk.high_hazard_area_pct = landslide_pct
                    l_risk.risk_score = min(100.0, landslide_pct * 1.5)
                    l_risk.risk_level = "High" if landslide_pct > 20 else "Medium"
                    
                    count += 1
                else:
                    logger.warning(f"Municipality not found: {name}")
            
            db.commit()
            logger.info(f"ISPRA Ingestion Complete. Updated {count} municipalities.")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ingest_ispra()
