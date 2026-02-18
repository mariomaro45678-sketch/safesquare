import sys
from app.core.database import SessionLocal
from app.data_pipeline.ingestion.istat_geography import ISTATGeographyIngestor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run():
    db = SessionLocal()
    try:
        ingestor = ISTATGeographyIngestor(db)
        logger.info("Starting Geography Baseline Ingestion (ISTAT)...")
        
        # Execute ETL
        raw_data = ingestor.fetch()
        transformed_data = ingestor.transform(raw_data)
        count = ingestor.load(transformed_data)
        
        logger.info(f"Geography ingestion finished successfully. Records added: {count}")
    except Exception as e:
        logger.error(f"Geography ingestion failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run()
