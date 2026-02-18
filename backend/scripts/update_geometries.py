"""
Municipality Geometry Updater
Uses Nominatim to geocode municipalities and update centroid coordinates.
This provides basic location data for municipalities lacking geometries.
"""
import sys
import time
import requests
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.geography import Municipality
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org"
USER_AGENT = "italian-property-platform-geocoder/1.0"

def geocode_municipality(name, province_name, region_name):
    """Geocode a municipality using Nominatim API"""
    query = f"{name}, {province_name}, {region_name}, Italy"
    params = {
        'q': query,
        'format': 'json',
        'limit': 1,
        'addressdetails': 1
    }
    headers = {
        'User-Agent': USER_AGENT
    }
    
    try:
        response = requests.get(f"{NOMINATIM_URL}/search", params=params, headers=headers, timeout=10)
        time.sleep(2)  # Respect Nominatim usage policy and throttle local CPU
        
        if response.status_code == 200:
            results = response.json()
            if results:
                result = results[0]
                lat = float(result['lat'])
                lon = float(result['lon'])
                return lat, lon
        else:
            logger.warning(f"Nominatim returned status {response.status_code}")
    except requests.exceptions.Timeout:
        logger.error(f"Geocoding timeout for {name}")
    except Exception as e:
        logger.error(f"Geocoding error for {name}: {e}")
    
    return None, None

def update_centroids():
    """Update centroid coordinates for municipalities"""
    db = SessionLocal()
    try:
        # Get municipalities without centroids, prioritize by population
        municipalities = db.query(Municipality).filter(
            Municipality.centroid == None
        ).order_by(Municipality.population.desc()).all()
        
        logger.info(f"Found {len(municipalities)} municipalities without centroids")
        
        updated = 0
        failed = 0
        
        for i, muni in enumerate(municipalities, 1):
            province_name = muni.province.name if muni.province else ""
            region_name = muni.province.region.name if muni.province and muni.province.region else ""
            
            logger.info(f"[{i}/{len(municipalities)}] Geocoding {muni.name}, {province_name}...")
            
            lat, lon = geocode_municipality(muni.name, province_name, region_name)
            
            if lat and lon:
                # Update using PostGIS ST_SetSRID(ST_MakePoint(lon, lat), 4326)
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
                logger.info(f"  ✓ Updated: ({lat:.4f}, {lon:.4f})")
            else:
                failed += 1
                logger.warning(f"  ✗ Failed to geocode")
            
            # Progress checkpoint every 100 records
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{len(municipalities)} | Updated: {updated} | Failed: {failed}")
        
        logger.info("=" * 60)
        logger.info(f"Geocoding complete!")
        logger.info(f"  Updated: {updated}")
        logger.info(f"  Failed:  {failed}")
        logger.info("=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting municipality centroid update...")
    logger.warning("This will use Nominatim API - max 1 request/second")
    logger.warning(f"Estimated time: ~7895 seconds (~2.2 hours) for all municipalities")
    
    # Auto-confirm for background execution
    update_centroids()
