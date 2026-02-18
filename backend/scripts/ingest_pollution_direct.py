"""
Direct ingestion of municipality-level pollution data.
The pollution_full_national.xlsx already contains pre-aggregated data per municipality.
"""
import sys
import pandas as pd
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.geography import Municipality
from app.models.risk import AirQuality

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        source_path = "data/raw/pollution_full_national.xlsx"
        logger.info(f"Loading pollution data from {source_path}...")

        df = pd.read_excel(source_path)
        logger.info(f"Loaded {len(df)} records")

        # Build municipality code -> id mapping
        mun_map = {m.code: m.id for m in db.query(Municipality.code, Municipality.id).all()}
        logger.info(f"Found {len(mun_map)} municipalities in DB")

        count = 0
        skipped = 0

        for _, row in df.iterrows():
            mun_code = str(row['Codice_Comune']).zfill(6)  # Pad to 6 digits

            if mun_code not in mun_map:
                skipped += 1
                continue

            mun_id = mun_map[mun_code]
            year = int(row.get('Anno', 2023))

            # Check for existing record
            existing = db.query(AirQuality).filter(
                AirQuality.municipality_id == mun_id,
                AirQuality.year == year
            ).first()

            pm25 = float(row.get('PM2.5_Avg', 0))
            pm10 = float(row.get('PM10_Avg', 0))
            no2 = float(row.get('NO2_Avg', 0))
            aqi = float(row.get('AQI_Index', 0))
            risk = str(row.get('Risk_Level', 'Moderate'))

            if existing:
                existing.pm25_avg = pm25
                existing.pm10_avg = pm10
                existing.no2_avg = no2
                existing.aqi_index = aqi
                existing.health_risk_level = risk
                existing.data_source = "pollution_full_national.xlsx"
            else:
                aq = AirQuality(
                    municipality_id=mun_id,
                    pm25_avg=pm25,
                    pm10_avg=pm10,
                    no2_avg=no2,
                    aqi_index=aqi,
                    health_risk_level=risk,
                    year=year,
                    station_count=1,
                    data_source="pollution_full_national.xlsx"
                )
                db.add(aq)
                count += 1

        db.commit()
        logger.info(f"Air quality ingestion complete. Added: {count}, Skipped (no match): {skipped}")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run()
