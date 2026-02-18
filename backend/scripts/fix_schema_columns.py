import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_schema():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        cols = [
            ("dist_train_station_km", "FLOAT"),
            ("dist_highway_exit_km", "FLOAT"),
            ("hospital_count", "INTEGER DEFAULT 0"),
            ("school_count", "INTEGER DEFAULT 0"),
            ("supermarket_count", "INTEGER DEFAULT 0")
        ]
        
        for col_name, col_type in cols:
            try:
                conn.execute(text(f"ALTER TABLE municipalities ADD COLUMN {col_name} {col_type}"))
                logger.info(f"Added {col_name}")
            except Exception as e:
                logger.info(f"Column {col_name} likely exists (Error: {e})")

if __name__ == "__main__":
    fix_schema()
