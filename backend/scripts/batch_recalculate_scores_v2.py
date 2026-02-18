
import os
import sys
import logging
import time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.geography import Municipality, OMIZone
from app.services.scoring_engine import ScoringEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def recalculate_all_scores():
    db = SessionLocal()
    engine = ScoringEngine()
    
    try:
        # Get already calculated IDs to skip
        from app.models.score import InvestmentScore
        from datetime import date
        today = date.today()
        
        done_mun_ids = {r[0] for r in db.query(InvestmentScore.municipality_id).filter(
            InvestmentScore.calculation_date == today,
            InvestmentScore.omi_zone_id == None
        ).all()}
        
        done_zone_ids = {r[0] for r in db.query(InvestmentScore.omi_zone_id).filter(
            InvestmentScore.calculation_date == today,
            InvestmentScore.omi_zone_id != None
        ).all()}
        
        # OPTIMIZATION: Fetch IDs only first to save memory (avoid loading 8000 geometries)
        mun_ids = [r[0] for r in db.query(Municipality.id).all()]
        logger.info(f"Resuming: {len(done_mun_ids)} mun and {len(done_zone_ids)} zones already done today. Total cities: {len(mun_ids)}")
        
        total_count = 0
        
        for mun_id in mun_ids:
            try:
                # 2. Municipality Score
                if mun_id not in done_mun_ids:
                    # Fetch fresh object
                    # mun = db.query(Municipality).get(mun_id) # Legacy
                    mun = db.query(Municipality).filter(Municipality.id == mun_id).first()
                    if not mun: continue
                    

                    res = engine.calculate_score(db, municipality_id=mun.id)
                    engine.save_score(db, res)
                    total_count += 1
                
                # 3. OMI Zones
                zones = db.query(OMIZone).filter(OMIZone.municipality_id == mun_id).all()
                for zone in zones:
                    if zone.id not in done_zone_ids:
                        res_z = engine.calculate_score(db, omi_zone_id=zone.id)
                        engine.save_score(db, res_z)
                        total_count += 1
                
                # Resource Safety Delay
                time.sleep(0.1) 

                if total_count > 0 and total_count % 100 == 0:
                    logger.info(f"Progress: {total_count} NEW scores updated...")
                    db.commit()
                    
            except Exception as e:
                logger.error(f"Failed for mun {mun_id}: {e}")
                db.rollback()
        
        db.commit()
        logger.info(f"Finished! Total scores recalculated: {total_count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    recalculate_all_scores()
