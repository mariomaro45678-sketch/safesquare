import logging
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.base import Base
from app.models.infrastructure import TransportNode  # Register model
from app.models.geography import Municipality
from app.models.score import InvestmentScore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_schema():
    engine = create_engine(settings.DATABASE_URL)
    
    logger.info("Creating new tables (TransportNode)...")
    Base.metadata.create_all(bind=engine)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # Add columns to Municipality
        logger.info("Checking Municipality columns...")
        try:
            conn.execute(text("ALTER TABLE municipalities ADD COLUMN dist_train_station_km FLOAT"))
            logger.info("Added dist_train_station_km")
        except Exception as e:
            logger.info(f"Column dist_train_station_km likely exists: {e}")
            
        try:
            conn.execute(text("ALTER TABLE municipalities ADD COLUMN dist_highway_exit_km FLOAT"))
            logger.info("Added dist_highway_exit_km")
        except Exception as e:
            logger.info(f"Column dist_highway_exit_km likely exists: {e}")

        # Add columns to InvestmentScore
        logger.info("Checking InvestmentScore columns...")
        try:
            conn.execute(text("ALTER TABLE investment_scores ADD COLUMN connectivity_score FLOAT"))
            logger.info("Added connectivity_score")
        except Exception as e:
            logger.info(f"Column connectivity_score likely exists: {e}")

        try:
            conn.execute(text("ALTER TABLE investment_scores ADD COLUMN air_quality_score FLOAT"))
            logger.info("Added air_quality_score")
        except Exception as e:
            logger.info(f"Column air_quality_score likely exists: {e}")

    logger.info("Schema update complete.")

if __name__ == "__main__":
    update_schema()
