
import logging
from sqlalchemy import text
from app.core.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_population():
    db = SessionLocal()
    try:
        logger.info("Syncing population from Demographics table to Municipalities table...")
        
        # SQL to update municipalities.population with the latest Demographics.total_population
        sql = """
        UPDATE municipalities m
        SET population = d.total_population
        FROM (
            SELECT DISTINCT ON (municipality_id) municipality_id, total_population
            FROM demographics
            ORDER BY municipality_id, year DESC, reference_date DESC
        ) d
        WHERE m.id = d.municipality_id;
        """
        
        result = db.execute(text(sql))
        db.commit()
        logger.info(f"Sync complete. Updated {result.rowcount} municipalities.")
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_population()
