from app.core.database import SessionLocal
from app.models.geography import Municipality
from app.services.scoring_engine import ScoringEngine
from sqlalchemy import func

def verify_all_risks():
    db = SessionLocal()
    engine = ScoringEngine()
    
    cities = ["Faenza", "Genova", "Venezia", "Roma", "Milano", "L'Aquila"]
    
    print("-" * 100)
    print(f"{'CITY':<12} | {'FLOOD (1-10)':<12} | {'LANDSLIDE (1-10)':<18} | {'SEISMIC (1-10)':<15}")
    print("-" * 100)
    
    for city_name in cities:
        mun = db.query(Municipality).filter(func.lower(Municipality.name) == city_name.lower()).first()
        if mun:
            s_flood = engine._score_flood_risk(db, mun.id)
            s_land = engine._score_landslide_risk(db, mun.id)
            s_seis = engine._score_seismic_risk(db, mun.id)
            
            print(f"{city_name:<12} | {s_flood:<12.2f} | {s_land:<18.2f} | {s_seis:<15.2f}")
        else:
            print(f"{city_name:<12} | NOT FOUND")

if __name__ == "__main__":
    verify_all_risks()
