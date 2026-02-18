from app.core.database import SessionLocal
from app.models.geography import Municipality
from app.services.scoring_engine import ScoringEngine

try:
    db = SessionLocal()
    rome = db.query(Municipality).filter(Municipality.name=='Roma').first()
    
    if rome:
        print(f"--- Rome Services Verification ---")
        print(f"Hospitals: {rome.hospital_count}")
        print(f"Schools: {rome.school_count}")
        print(f"Supermarkets: {rome.supermarket_count}")
        
        # Check Score
        engine = ScoringEngine()
        score = engine._score_services(db, rome.id)
        print(f"Services Score (Calculated): {score}")
    else:
        print("Roma not found in database.")
except Exception as e:
    print(f"Error: {e}")
