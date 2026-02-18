import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_investment_scores():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        cols = [
            "digital_connectivity_score",
            "confidence_score"
        ]
        
        for col in cols:
            try:
                conn.execute(text(f"ALTER TABLE investment_scores ADD COLUMN {col} FLOAT"))
                logger.info(f"Added {col} to investment_scores")
            except Exception as e:
                logger.info(f"Column {col} likely exists: {e}")

if __name__ == "__main__":
    fix_investment_scores()
