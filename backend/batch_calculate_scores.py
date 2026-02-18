import os
import sys
import logging
from datetime import date

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.geography import Municipality
from app.services.scoring_engine import ScoringEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_calculate():
    db = SessionLocal()
    engine = ScoringEngine()
    
    # Fetch all municipalities
    municipalities = db.query(Municipality).all()
    total = len(municipalities)
    logger.info(f"Starting batch calculation for {total} municipalities...")
    
    count = 0
    success = 0
    for m in municipalities:
        try:
            # We calculate and save the score
            # engine.save_score now handles UPSERT logic
            result = engine.calculate_score(db, municipality_id=m.id)
            engine.save_score(db, result)
            
            # Throttle CPU usage to prevent system overload
            import time
            # Sleep to allow CPU/DB to breath
            time.sleep(0.1)
            
            success += 1
            count += 1
            
            # Commit and log progress
            if count % 100 == 0:
                # db.commit() is already called in save_score, but we keep this for consistency
                logger.info(f"Processed {count}/{total} municipalities...")
                
        except Exception as e:
            logger.error(f"Could not calculate score for {m.name} (ID: {m.id}): {e}")
            db.rollback()
            count += 1
            continue
            
    logger.info(f"Batch calculation complete. Successfully scored: {success}/{total}")
    db.close()

if __name__ == "__main__":
    batch_calculate()
