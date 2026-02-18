from app.core.database import SessionLocal
from app.models.geography import Municipality, Province
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def propagate_rents():
    db = SessionLocal()
    try:
        # Fetch all municipalities with rental data (The 103 Capitals)
        capitals = db.query(Municipality).filter(Municipality.avg_rent_sqm > 0).all()
        logger.info(f"Found {len(capitals)} capitals with rental data.")
        
        updates = 0
        for cap in capitals:
            prov = db.query(Province).filter(Province.id == cap.province_id).first()
            if prov:
                prov.avg_rent_sqm = cap.avg_rent_sqm
                updates += 1
                # logger.info(f"Set Province {prov.name} baseline to {cap.avg_rent_sqm}")
        
        db.commit()
        logger.info(f"Propagation complete. Updated {updates} provinces.")
        
    except Exception as e:
        logger.error(f"Propagation failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    propagate_rents()
