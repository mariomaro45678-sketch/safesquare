
import logging
from sqlalchemy import text
from app.core.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_fallback_broadband():
    db = SessionLocal()
    try:
        logger.info("Populating fallback broadband coverage based on population...")
        
        # SQL to update broadband coverage based on population buckets if NULL or 0
        sql = """
        UPDATE municipalities
        SET broadband_ftth_coverage = CASE
            WHEN population >= 500000 THEN 95.0
            WHEN population >= 100000 THEN 85.0
            WHEN population >= 50000 THEN 70.0
            WHEN population >= 20000 THEN 50.0
            WHEN population >= 5000 THEN 30.0
            ELSE 15.0
        END,
        broadband_speed_100mbps = CASE
            WHEN population >= 100000 THEN 100.0
            WHEN population >= 20000 THEN 80.0
            ELSE 50.0
        END
        WHERE (broadband_ftth_coverage IS NULL OR broadband_ftth_coverage = 0);
        """
        
        result = db.execute(text(sql))
        db.commit()
        logger.info(f"Fallback complete. Updated {result.rowcount} municipalities.")
        
    except Exception as e:
        logger.error(f"Fallback failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_fallback_broadband()
