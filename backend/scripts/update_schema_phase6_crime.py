from app.core.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_schema():
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        try:
            conn.execute(text("ALTER TABLE crime_statistics ADD COLUMN granularity_level VARCHAR(50) DEFAULT 'municipality'"))
            conn.execute(text("ALTER TABLE crime_statistics ADD COLUMN sub_municipal_area VARCHAR(100)"))
            logger.info("Added granular columns to crime_statistics")
        except Exception as e:
            logger.warning(f"Columns likely exist: {e}")

if __name__ == "__main__":
    update_schema()
