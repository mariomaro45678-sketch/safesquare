from app.core.database import SessionLocal
from app.models.geography import Municipality
from app.services.scoring_engine import ScoringEngine
from sqlalchemy import func

def verify_seismic():
    db = SessionLocal()
    engine = ScoringEngine()
    
    cities = ["Roma", "Milano", "L'Aquila", "Catania", "Torino"]
    
    print("-" * 60)
    print(f"{'CITY':<15} | {'PGA (g)':<10} | {'RISK (0-100)':<15} | {'SCORE (1-10)':<10}")
    print("-" * 60)
    
    for city_name in cities:
        mun = db.query(Municipality).filter(func.lower(Municipality.name) == city_name.lower()).first()
        if mun:
            # Manually fetch risk to show debug info
            # The engine call just returns the float score
            risk_obj = mun.seismic_risks[0] if mun.seismic_risks else None
            score = engine._score_seismic_risk(db, mun.id)
            
            pga = f"{risk_obj.peak_ground_acceleration:.3f}" if risk_obj else "N/A"
            risk_val = f"{risk_obj.risk_score:.1f}" if risk_obj else "N/A"
            
            print(f"{city_name:<15} | {pga:<10} | {risk_val:<15} | {score:<10.2f}")
        else:
            print(f"{city_name:<15} | NOT FOUND")

if __name__ == "__main__":
    verify_seismic()
