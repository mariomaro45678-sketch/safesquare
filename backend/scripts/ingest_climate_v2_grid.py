
import sys
import os
import time
import logging
from typing import List, Dict
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.geography import Municipality
from app.data_pipeline.ingestion.open_meteo_climate import OpenMeteoClimateIngestor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def run_grid_ingestion():
    db = SessionLocal()
    ingestor = OpenMeteoClimateIngestor(db)
    
    try:
        # 1. Fetch all municipalities with centroids
        # We use centroids for the 10km grid mapping
        query = db.query(
            Municipality.id,
            Municipality.name,
            func.ST_X(Municipality.centroid).label('lon'),
            func.ST_Y(Municipality.centroid).label('lat')
        ).filter(Municipality.centroid != None)
        
        municipalities = query.all()
        logger.info(f"Found {len(municipalities)} municipalities with valid centroids.")
        
        # 2. Process in batches of 50 (Open-Meteo limit)
        batch_size = 50
        total_batches = (len(municipalities) + batch_size - 1) // batch_size
        
        for i, batch in enumerate(chunk_list(municipalities, batch_size)):
            logger.info(f"Processing batch {i+1}/{total_batches}...")
            
            coords = [{"lat": m.lat, "lon": m.lon, "mun_id": m.id} for m in batch]
            
            # Fetch
            raw_data = ingestor.fetch(coords)
            if not raw_data:
                logger.warning(f"Batch {i+1} returned no data.")
                continue
                
            # Transform
            transformed = ingestor.transform(raw_data)
            
            # Load
            count = ingestor.load(transformed)
            logger.info(f"Loaded {count} climate projections in batch {i+1}.")
            
            # Respect API limits (Open-Meteo is generous but let's be safe)
            time.sleep(1) 
            
    except Exception as e:
        logger.error(f"Grid ingestion failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_grid_ingestion()
