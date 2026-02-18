import sys
import os
from app.core.database import SessionLocal
from app.data_pipeline.ingestion.omi import OMIIngestor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run():
    db = SessionLocal()
    try:
        source_path = "data/raw/omi_full_mvp_regions_2021_2023.xlsx"
        if not os.path.exists(source_path):
            source_path = os.path.join(os.getcwd(), "data", "raw", "omi_full_mvp_regions_2021_2023.xlsx")
            
        if not os.path.exists(source_path):
            logger.error(f"Source file not found: {source_path}")
            sys.exit(1)
            
        ingestor = OMIIngestor(db)
        logger.info(f"Starting OMI Expansion from {source_path}...")
        
        raw_data = ingestor.fetch(source_path)
        transformed_data = ingestor.transform(raw_data)
        count = ingestor.load(transformed_data)
        
        logger.info(f"OMI expansion finished successfully. Records processed: {count}")
    except Exception as e:
        logger.error(f"OMI expansion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run()
