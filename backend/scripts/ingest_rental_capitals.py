import pandas as pd
import logging
from app.core.database import SessionLocal
from app.models.geography import Municipality
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
CSV_PATH = "/app/data/raw/Dati_locazioni_capoluoghi_2018_2024.csv"
if not os.path.exists(CSV_PATH):
    CSV_PATH = "backend/data/raw/Dati_locazioni_capoluoghi_2018_2024.csv"

def ingest_capitals():
    db = SessionLocal()
    try:
        logger.info(f"Reading {CSV_PATH}...")
        df = pd.read_csv(CSV_PATH, sep=';', encoding='latin1')
        
        # Filter for latest year (2023 seems to be latest full year based on inspection)
        latest_year = df['ANNO'].max()
        logger.info(f"Latest year in dataset: {latest_year}")
        df = df[df['ANNO'] == latest_year]
        
        updates = 0
        not_found = []
        
        for _, row in df.iterrows():
            comune_name = str(row['Comune']).strip().upper()
            
            # Helper to parse Italian formatted numbers "1.234,56"
            def parse_ita_float(val):
                if pd.isna(val): return 0.0
                return float(str(val).replace('.', '').replace(',', '.'))
            
            try:
                annual_rent = parse_ita_float(row['Canone annuo in euro  delle abitazioni locate (per le unit\x85 B)'])
                surface = parse_ita_float(row['Superficie in mq delle abitazioni locate (per le unit\x85 B)'])
                
                if surface <= 0: continue
                
                avg_rent_annual = annual_rent / surface
                
                # Update DB
                # Case-insensitive search for municipality
                mun = db.query(Municipality).filter(func.upper(Municipality.name) == comune_name).first()
                if mun:
                    mun.avg_rent_sqm = avg_rent_annual
                    updates += 1
                else:
                    not_found.append(comune_name)
                    
            except Exception as e:
                logger.warning(f"Error processing {comune_name}: {e}")
                
        db.commit()
        logger.info(f"Ingestion complete. Updated {updates} municipalities.")
        if not_found:
            logger.warning(f"Municipalities not found ({len(not_found)}): {not_found[:10]}...")
            
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ingest_capitals()
