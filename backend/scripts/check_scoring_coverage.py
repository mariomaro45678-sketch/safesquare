
import os
from sqlalchemy import create_engine, text
from app.core.config import settings

def check_coverage():
    engine = create_engine(str(settings.DATABASE_URL))
    with engine.connect() as conn:
        # Check municipalities
        m_query = text("""
            SELECT COUNT(*) 
            FROM municipalities m 
            LEFT JOIN investment_scores s ON m.id = s.municipality_id 
                AND s.calculation_date = CURRENT_DATE 
                AND s.omi_zone_id IS NULL 
            WHERE s.id IS NULL
        """)
        missing_m = conn.execute(m_query).scalar()
        
        # Check OMI zones
        z_query = text("""
            SELECT COUNT(*) 
            FROM omi_zones z 
            LEFT JOIN investment_scores s ON z.id = s.omi_zone_id 
                AND s.calculation_date = CURRENT_DATE 
            WHERE s.id IS NULL
        """)
        missing_z = conn.execute(z_query).scalar()
        
        # Total counts
        total_m = conn.execute(text("SELECT COUNT(*) FROM municipalities")).scalar()
        total_z = conn.execute(text("SELECT COUNT(*) FROM omi_zones")).scalar()
        
        print(f"Municipalities: {total_m - missing_m}/{total_m} (Missing: {missing_m})")
        print(f"OMI Zones: {total_z - missing_z}/{total_z} (Missing: {missing_z})")
        
        if missing_m > 0 or missing_z > 0:
            print("STATUS: INCOMPLETE")
        else:
            print("STATUS: COMPLETE")

if __name__ == "__main__":
    check_coverage()
