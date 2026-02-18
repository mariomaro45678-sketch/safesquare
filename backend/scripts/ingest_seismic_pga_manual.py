import math
from app.core.database import SessionLocal
from app.models.geography import Municipality
from app.models.risk import SeismicRisk
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# REFERENCE POINTS (INGV MPS04 PGA in g - 475y return period)
# Source: INGV Hazard Map
REFERENCE_PGA = {
    "L'Aquila": (42.3498, 13.3995, 0.260), # High
    "Catania": (37.5079, 15.0830, 0.220),  # High
    "Messina": (38.1938, 15.5540, 0.240),  # High
    "Potenza": (40.6327, 15.8086, 0.230),  # High
    "Reggio di Calabria": (38.1113, 15.6472, 0.250), # High
    
    "Napoli": (40.8518, 14.2681, 0.160),   # Medium-High
    "Benevento": (41.1298, 14.7826, 0.240),# High
    "Perugia": (43.1107, 12.3908, 0.140),  # Medium
    "Firenze": (43.7696, 11.2558, 0.130),  # Medium
    "Bologna": (44.4949, 11.3426, 0.140),  # Medium
    "Roma": (41.9028, 12.4964, 0.100),     # Medium-Low (Avg)
    "Ancona": (43.6158, 13.5189, 0.190),   # Medium-High
    
    "Milano": (45.4642, 9.1900, 0.050),    # Low
    "Torino": (45.0703, 7.6869, 0.040),    # Very Low
    "Genova": (44.4056, 8.9463, 0.060),    # Low
    "Venezia": (45.4408, 12.3155, 0.070),  # Low
    "Trieste": (45.6495, 13.7768, 0.090),  # Medium-Low
    "Bari": (41.1171, 16.8719, 0.060),     # Low
    "Lecce": (40.3515, 18.1750, 0.040),    # Very Low
    
    "Cagliari": (39.2238, 9.1216, 0.020),  # Negligible
    "Sassari": (40.7259, 8.5556, 0.020),   # Negligible
    "Palermo": (38.1157, 13.3615, 0.090),  # Medium-Low
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def interpolate_pga(lat, lon):
    # Inverse Distance Weighting (IDW)
    # Using top 4 nearest references
    distances = []
    for city, (rlat, rlon, pga) in REFERENCE_PGA.items():
        dist = haversine(lat, lon, rlat, rlon)
        distances.append((dist, pga))
    
    distances.sort(key=lambda x: x[0])
    nearest = distances[:4]
    
    # Calculate weighted average
    weighted_sum = 0
    total_weight = 0
    
    for dist, pga in nearest:
        weight = 1 / (dist + 1.0) ** 2 # Power of 2 for closer influence
        weighted_sum += pga * weight
        total_weight += weight
        
    return weighted_sum / total_weight

def update_seismic_data():
    db = SessionLocal()
    try:
        total = db.query(Municipality).count()
        logger.info(f"Updating Seismic Data for {total} municipalities...")
        
        batch_size = 100
        # Fetch ID, Lat, Lon using PostGIS functions
        # SRID 4326: X=Lon, Y=Lat
        municipalities = db.query(
            Municipality.id,
            func.ST_Y(Municipality.centroid).label('latitude'),
            func.ST_X(Municipality.centroid).label('longitude')
        ).filter(Municipality.centroid.isnot(None)).all()
        
        updated = 0
        for mun in municipalities:
            if not mun.latitude or not mun.longitude:
                continue
                
            pga = interpolate_pga(mun.latitude, mun.longitude)
            
            # Determine Zone based on NTC 2008 roughly
            # Zone 1: > 0.25g
            # Zone 2: 0.15 - 0.25g
            # Zone 3: 0.05 - 0.15g
            # Zone 4: < 0.05g
            if pga >= 0.25: zone = 1
            elif pga >= 0.15: zone = 2
            elif pga >= 0.05: zone = 3
            else: zone = 4
            
            # Risk Score (0-100, Higher = More Risk)
            # Normalize 0.30g as 100 (Extremely High)
            risk_score = min(100.0, (pga / 0.30) * 100)
            
            # Update or Create
            risk = db.query(SeismicRisk).filter(SeismicRisk.municipality_id == mun.id).first()
            if not risk:
                risk = SeismicRisk(municipality_id=mun.id)
                db.add(risk)
                
            risk.peak_ground_acceleration = pga
            risk.seismic_zone = zone
            risk.risk_score = risk_score
            risk.hazard_level = f"Zone {zone}"
            
            updated += 1
            if updated % 500 == 0:
                logger.info(f"Processed {updated}/{total}...")
                
        db.commit()
        logger.info(f"Seismic Update Complete. Processed {updated} records.")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_seismic_data()
