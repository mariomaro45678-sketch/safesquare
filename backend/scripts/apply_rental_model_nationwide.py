import logging
from app.core.database import SessionLocal
from app.models.geography import Municipality, Province, OMIZone
from app.models.property import PropertyPrice
from sqlalchemy import func
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_rental_model():
    db = SessionLocal()
    try:
        # 1. Get average sale prices for all municipalities (latest year/semester)
        logger.info("Calculating average sale prices per municipality...")
        latest_prices = db.query(
            OMIZone.municipality_id,
            func.avg(PropertyPrice.avg_price).label('avg_price')
        ).join(PropertyPrice, OMIZone.id == PropertyPrice.omi_zone_id)\
         .filter(PropertyPrice.year == 2023).group_by(OMIZone.municipality_id).all()
        
        price_map = {p.municipality_id: p.avg_price for p in latest_prices}
        
        # 2. Get provinces and their capital's rent baseline
        provinces = db.query(Province).all()
        
        total_updated = 0
        
        for prov in provinces:
            # Baseline from province (previously propagated from capital)
            baseline_rent = prov.avg_rent_sqm
            if not baseline_rent or baseline_rent <= 0:
                # Fallback to macro-area baseline if needed (simplified for now)
                baseline_rent = 8.5 # Italy average estimate
                
            # Get Capital's sale price as baseline
            capital = db.query(Municipality).filter(
                Municipality.province_id == prov.id,
                func.upper(Municipality.name) == func.upper(prov.name) # Rough heuristic for capital
            ).first()
            
            # If not found by name, try any municipality with rent data in that province
            if not capital:
                capital = db.query(Municipality).filter(
                    Municipality.province_id == prov.id,
                    Municipality.avg_rent_sqm > 0
                ).first()
                
            capital_price = price_map.get(capital.id) if capital else None
            
            # Sub-municipalities
            muns = db.query(Municipality).filter(Municipality.province_id == prov.id).all()
            
            for m in muns:
                if m.avg_rent_sqm and m.avg_rent_sqm > 0 and capital and m.id == capital.id:
                    continue # Keep real data for capital
                
                m_price = price_map.get(m.id)
                if m_price and capital_price:
                    # Rent Propagation Formula: Elasticity factor 0.7
                    # R_m = R_cap * (P_m / P_cap)^0.7
                    ratio = m_price / capital_price
                    estimated_rent = baseline_rent * math.pow(ratio, 0.7)
                    
                    m.avg_rent_sqm = estimated_rent
                    total_updated += 1
                elif baseline_rent:
                    # Simple fallback to province average if no price data
                    m.avg_rent_sqm = baseline_rent
                    total_updated += 1
                    
        db.commit()
        logger.info(f"Rental model applied. Updated {total_updated} municipalities with granular estimates.")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    apply_rental_model()
