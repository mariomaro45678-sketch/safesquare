from app.core.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_schema():
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        try:
            conn.execute(text("ALTER TABLE provinces ADD COLUMN avg_rent_sqm FLOAT"))
            logger.info("Added avg_rent_sqm column to provinces")
        except Exception as e:
            logger.warning(f"avg_rent_sqm column likely exists: {e}")

if __name__ == "__main__":
    update_schema()
