from app.core.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_schema():
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # Add min_rent
        try:
            conn.execute(text("ALTER TABLE property_prices ADD COLUMN min_rent FLOAT"))
            logger.info("Added min_rent")
        except Exception as e:
            logger.warning(f"min_rent likely exists: {e}")

        # Add max_rent
        try:
            conn.execute(text("ALTER TABLE property_prices ADD COLUMN max_rent FLOAT"))
            logger.info("Added max_rent")
        except Exception as e:
            logger.warning(f"max_rent likely exists: {e}")

        # Add avg_rent
        try:
            conn.execute(text("ALTER TABLE property_prices ADD COLUMN avg_rent FLOAT"))
            logger.info("Added avg_rent")
        except Exception as e:
            logger.warning(f"avg_rent likely exists: {e}")

if __name__ == "__main__":
    update_schema()
