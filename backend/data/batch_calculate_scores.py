import os
import sys
import logging
import time
from datetime import date

# Add /app to path since we are in /app/data
sys.path.append('/app')

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
    for m in municipalities:
        try:
            # We calculate and save the score
            result = engine.calculate_score(db, municipality_id=m.id)
            
            # Create the record without committing inside save_score
            # Actually save_score has db.commit() inside. We should avoid that for batch.
            # Let's manually create it here or modify save_score.
            # To avoid modifying ScoringEngine now, we'll keep it but it's slow.
            # But wait, I can just do a single commit if I use a different method.
            
            engine.save_score(db, result)
            count += 1
            if count % 100 == 0:
                logger.info(f"Processed {count}/{total} municipalities...")
            
            # Throttle to keep CPU/DB healthy
            time.sleep(0.05)
        except Exception as e:
            logger.error(f"Error for {m.name} (ID: {m.id}): {e}")
            db.rollback()
            continue
            
    logger.info(f"Batch calculation complete. Total scored: {count}")
    db.close()

if __name__ == "__main__":
    batch_calculate()
