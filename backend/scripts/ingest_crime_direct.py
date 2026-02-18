"""
Direct ingestion of municipality-level crime data.
The crime_full_mvp_regions.xlsx contains pre-aggregated data per municipality.
"""
import sys
import pandas as pd
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.geography import Municipality
from app.models.demographics import CrimeStatistics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        source_path = "data/raw/crime_full_mvp_regions.xlsx"
        logger.info(f"Loading crime data from {source_path}...")

        df = pd.read_excel(source_path)
        logger.info(f"Loaded {len(df)} records")

        # Build municipality code -> id mapping
        mun_map = {m.code: m.id for m in db.query(Municipality.code, Municipality.id).all()}
        logger.info(f"Found {len(mun_map)} municipalities in DB")

        count = 0
        updated = 0
        skipped = 0

        for _, row in df.iterrows():
            # Handle float/int code - convert to int first, then to zero-padded string
            mun_code = str(int(row['Codice_Comune'])).zfill(6)

            if mun_code not in mun_map:
                skipped += 1
                continue

            mun_id = mun_map[mun_code]
            year = int(row.get('Anno', 2022))

            total_crimes = float(row.get('Total_Crimes_Per_1000', 0))
            violent_crimes = float(row.get('Violent_Crimes_Per_1000', 0))
            property_crimes = float(row.get('Property_Crimes_Per_1000', 0))

            # Calculate crime_index (0-100 scale where 100 = high crime)
            # National average ~ 40 crimes/1000, max ~ 100
            # Normalize: index = (total_crimes / 100) * 100, capped at 100
            crime_index = min(100.0, total_crimes)

            # Check for existing record
            existing = db.query(CrimeStatistics).filter(
                CrimeStatistics.municipality_id == mun_id,
                CrimeStatistics.year == year,
                CrimeStatistics.granularity_level == 'municipality'
            ).first()

            if existing:
                existing.total_crimes_per_1000 = total_crimes
                existing.violent_crimes_per_1000 = violent_crimes
                existing.property_crimes_per_1000 = property_crimes
                existing.crime_index = crime_index
                updated += 1
            else:
                crime = CrimeStatistics(
                    municipality_id=mun_id,
                    year=year,
                    granularity_level='municipality',
                    sub_municipal_area=None,
                    total_crimes_per_1000=total_crimes,
                    violent_crimes_per_1000=violent_crimes,
                    property_crimes_per_1000=property_crimes,
                    crime_index=crime_index
                )
                db.add(crime)
                count += 1

        db.commit()
        logger.info(f"Crime ingestion complete. Added: {count}, Updated: {updated}, Skipped: {skipped}")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run()
