import logging
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.base import Base
from app.models.services import ServiceNode  # Register model

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_schema():
    engine = create_engine(settings.DATABASE_URL)
    
    logger.info("Creating new tables (ServiceNode)...")
    Base.metadata.create_all(bind=engine)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # Add columns to Municipality for counts
        logger.info("Checking Municipality columns...")
        cols = ["hospital_count", "school_count", "supermarket_count"]
        for col in cols:
            try:
                conn.execute(text(f"ALTER TABLE municipalities ADD COLUMN {col} INTEGER DEFAULT 0"))
                logger.info(f"Added {col}")
            except Exception as e:
                logger.info(f"Column {col} likely exists: {e}")

        # Add columns to InvestmentScore for component
        logger.info("Checking InvestmentScore columns...")
        try:
            conn.execute(text("ALTER TABLE investment_scores ADD COLUMN services_score FLOAT"))
            logger.info("Added services_score")
        except Exception as e:
            logger.info(f"Column services_score likely exists: {e}")

    logger.info("Schema update complete.")

if __name__ == "__main__":
    update_schema()
