
from app.core.database import SessionLocal
from app.models.geography import Municipality
from app.services.scoring_engine import ScoringEngine
import sys
import logging

# Silence noisy logs
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

def simulate():
    engine = ScoringEngine()
    results = []
    print(f"Stats loaded: {engine.stats is not None}")
    
    # Pre-fetch IDs to avoid session conflict (South Italy sample)
    db_main = SessionLocal()
    muni_ids = [m.id for m in db_main.query(Municipality).offset(6000).limit(100).all()]
    db_main.close()
    
    for mid in muni_ids:
        db = SessionLocal()
        try:
            score_data = engine.calculate_score(db, mid)
            results.append(score_data['overall_score'])
            if len(results) == 1:
                 print(f"DEBUG SAMPLE {mid}: {score_data}")
        except Exception as e:
            print(f"Err for {mid}: {e}")
            db.rollback()
        finally:
            db.close()
            
    buckets = {}
    for s in results:
        b = int(s)
        buckets[b] = buckets.get(b, 0) + 1
        
    print("Score Distribution:")
    for b in sorted(buckets.keys(), reverse=True):
        print(f"{b}.x: {buckets[b]}")

if __name__ == "__main__":
    simulate()
