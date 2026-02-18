
import sys
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Setup environment
load_dotenv()
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.config import settings
from app.data_pipeline.ingestion.air_quality import AirQualityIngestor
from app.models.geography import Municipality
from app.models.risk import AirQuality

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_air_quality_ingestion():
    print("Starting Air Quality Verification...")
    
    # 1. Initialize DB & Ingestor
    db_url = str(settings.DATABASE_URL).replace("database", "localhost")
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    ingestor = AirQualityIngestor(db=db, data_dir="backend/data")
    
    # 2. Mock Fetch Data (Load the synthetic station data we created)
    station_file = "backend/data/raw/air_quality_station_data.xlsx"
    if not os.path.exists(station_file):
        print(f"Error: Station data file not found at {station_file}")
        return
        
    print(f"Fetching data from {station_file}...")
    df = ingestor.fetch(station_file)
    print(f"Fetched {len(df)} station records.")
    
    # 3. Transform Data (This uses the mapping_comuni_arpa.json)
    print("Transforming data using station mapping...")
    transformed = ingestor.transform(df)
    print(f"Transformed into {len(transformed)} municipality records.")
    
    if len(transformed) > 0:
        print(f"Sample Record: {transformed[0]}")
        
    # 4. Load Data (Persist to DB)
    
    print("Loading data into database...")
    try:
        count = ingestor.load(transformed)
        print(f"Successfully loaded {count} records into 'air_quality' table.")
        
        # 5. Verify DB Content
        sample = db.query(AirQuality).first()
        if sample:
            print("\nVerification Succcessful!")
            print(f"DB Record ID: {sample.id}")
            print(f"Municipality ID: {sample.municipality_id}")
            print(f"PM2.5: {sample.pm25_avg}")
            print(f"AQI: {sample.aqi_index}")
            print(f"Risk Level: {sample.health_risk_level}")
            print(f"Data Source: {sample.data_source}")
        else:
            print("\nWarning: No records found in DB after load.")
            
    except Exception as e:
        print(f"Error during load: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_air_quality_ingestion()
