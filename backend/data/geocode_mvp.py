import os
import sys
import time
import requests
from sqlalchemy import text, desc

# Add /app to path since we are in /app/data
sys.path.append('/app')

from app.core.database import SessionLocal
from app.models.geography import Municipality, Province, Region
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org"
USER_AGENT = "safesquare-mvp-geocoder-v2/1.0"

def geocode_municipality(name, province_name, region_name):
    """Geocode a municipality using Nominatim API"""
    query = f"{name}, {province_name}, {region_name}, Italy"
    params = {
        'q': query,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': USER_AGENT
    }
    
    try:
        response = requests.get(f"{NOMINATIM_URL}/search", params=params, headers=headers)
        # Nominatim policy: 1 request per second
        time.sleep(1.2)
        
        if response.status_code == 200:
            results = response.json()
            if results:
                result = results[0]
                lat = float(result['lat'])
                lon = float(result['lon'])
                return lat, lon
    except Exception as e:
        logger.error(f"Geocoding error for {name}: {e}")
    
    return None, None

def run_mvp_geocoding():
    db = SessionLocal()
    try:
        # Prioritize Lazio (12) then Lombardia (3)
        # Fetch Lazio first
        lazio_munis = db.query(Municipality).join(Province).join(Region).filter(
            Region.id == 12,
            Municipality.centroid == None
        ).all()
        
        lombardia_munis = db.query(Municipality).join(Province).join(Region).filter(
            Region.id == 3,
            Municipality.centroid == None
        ).all()
        
        municipalities = lazio_munis + lombardia_munis
        
        logger.info(f"Found {len(lazio_munis)} Lazio municipalities and {len(lombardia_munis)} Lombardia municipalities without centroids")
        
        updated = 0
        for i, muni in enumerate(municipalities, 1):
            province_name = muni.province.name if muni.province else ""
            region_name = muni.province.region.name if muni.province and muni.province.region else ""
            
            logger.info(f"[{i}/{len(municipalities)}] Geocoding {muni.name}, {province_name} ({region_name})...")
            
            lat, lon = geocode_municipality(muni.name, province_name, region_name)
            
            if lat and lon:
                db.execute(
                    text("""
                        UPDATE municipalities 
                        SET centroid = ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                        WHERE id = :id
                    """),
                    {"lon": lon, "lat": lat, "id": muni.id}
                )
                db.commit()
                updated += 1
                logger.info(f"  ✓ Updated")
            else:
                logger.warning(f"  ✗ Failed")
                
        logger.info(f"Priority geocoding complete. Updated {updated} MVP locations.")
    finally:
        db.close()

if __name__ == "__main__":
    run_mvp_geocoding()
