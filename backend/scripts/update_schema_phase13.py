import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_schema():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        cols = [
            ("mobile_tower_count", "INTEGER DEFAULT 0"),
            ("broadband_ftth_coverage", "FLOAT DEFAULT 0.0"),
            ("broadband_speed_100mbps", "FLOAT DEFAULT 0.0")
        ]
        
        for col_name, col_type in cols:
            try:
                # Check if column exists
                check_sql = text(f"SELECT column_name FROM information_schema.columns WHERE table_name='municipalities' AND column_name='{col_name}'")
                if not conn.execute(check_sql).fetchone():
                    logger.info(f"Adding column {col_name}...")
                    conn.execute(text(f"ALTER TABLE municipalities ADD COLUMN {col_name} {col_type}"))
                else:
                    logger.info(f"Column {col_name} already exists.")
            except Exception as e:
                logger.error(f"Error adding {col_name}: {e}")

if __name__ == "__main__":
    update_schema()
