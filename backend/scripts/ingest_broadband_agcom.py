import logging
import requests
import csv
import io
import codecs
from sqlalchemy import create_engine, text
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AGCOM_CSV_URL = "https://geo.agcom.it/arcgis/sharing/rest/content/items/6c0b48a9a06c44059656b987d85acb63/data"

def ingest_broadband():
    engine = create_engine(settings.DATABASE_URL)
    
    logger.info("Streaming AGCOM Broadband Data...")
    try:
        # Stream response
        response = requests.get(AGCOM_CSV_URL, stream=True, verify=False)
        response.raise_for_status()
        
        # Use a generator to decode lines on the fly
        lines = (line.decode('utf-8', errors='ignore') for line in response.iter_lines())
        
        # Parse CSV from generator
        csv_reader = csv.DictReader(lines, delimiter=';')
        
        updates = 0
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            
            for row in csv_reader:
                try:
                    # 1. Extract ISTAT Code (pro_com) - Ensure lowercase key from debug
                    istat_input = row.get('pro_com', '').strip()
                    if not istat_input: continue
                    istat_code = istat_input.zfill(6)
                    
                    # 2. Extract FTTH Coverage
                    # Format is "73%", "1%", "0%"
                    ftth_str = row.get('Copertura FTTH DESI', '0%').replace('%', '').strip()
                    try:
                        ftth_val = float(ftth_str)
                    except (ValueError, TypeError):
                        ftth_val = 0.0
                    
                    # Update Database
                    stmt = text("""
                        UPDATE municipalities 
                        SET broadband_ftth_coverage = :val, 
                            broadband_speed_100mbps = :val 
                        WHERE code = :code
                    """)
                    
                    res = conn.execute(stmt, {'val': ftth_val, 'code': istat_code})
                    updates += res.rowcount
                    
                    if updates > 0 and updates % 1000 == 0:
                        logger.info(f"Updated {updates} municipalities...")
                        
                except Exception as e:
                    pass # Skip errors to keep stream moving
                    
        logger.info(f"Broadband ingestion complete. Updated {updates} municipalities.")

    except Exception as e:
        logger.error(f"Failed to ingest CSV: {e}")

if __name__ == "__main__":
    ingest_broadband()
