import logging
import time
import requests
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.services import ServiceNode, ServiceType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


REGIONS = ["Lazio"]

def ingest_mobile_towers():
    engine = create_engine(settings.DATABASE_URL)
    
    # Use a persistent temp table (not dropped on commit)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS global_temp_towers"))
        conn.execute(text("CREATE TABLE global_temp_towers (id BIGINT, geom GEOMETRY(Point, 4326))"))
        conn.commit()

    all_elements = []
    
    for region in REGIONS:
        logger.info(f"Fetching Mobile Towers for {region}...")
        query = f"""
        [out:json][timeout:120];
        area["name"="Italia"]->.country;
        area["name"="{region}"]["admin_level"="4"](area.country)->.searchArea;
        (
          node["man_made"="mast"](area.searchArea);
          node["tower:type"="communication"](area.searchArea);
        );
        out center;
        """
        try:
            # Increased requests timeout
            response = requests.post(OVERPASS_URL, data={'data': query}, timeout=130)
            response.raise_for_status()
            data = response.json()
            elements = data.get('elements', [])
            logger.info(f"Fetched {len(elements)} towers for {region}.")
            all_elements.extend(elements)
            
            # Small delay to be polite to Overpass API
            time.sleep(2)
        except Exception as e:
            logger.error(f"Failed to fetch towers for {region}: {e}")
            continue

    if not all_elements:
        logger.error("No towers fetched. Aborting.")
        return

    # Process and Count
    db = SessionLocal()
    BATCH_SIZE = 500
    temp_rows = []
    
    logger.info(f"Preparing {len(all_elements)} towers for bulk insert...")
    
    with engine.connect() as conn:
        count = 0
        for element in all_elements:
            lon = element.get('lon') or element.get('center', {}).get('lon')
            lat = element.get('lat') or element.get('center', {}).get('lat')
            
            if lon and lat:
                wkt = f"POINT({lon} {lat})"
                temp_rows.append({'id': element['id'], 'wkt': wkt})
                
                if len(temp_rows) >= BATCH_SIZE:
                    values_str = ",".join([f"({r['id']}, ST_GeomFromText('{r['wkt']}', 4326))" for r in temp_rows])
                    conn.execute(text(f"INSERT INTO global_temp_towers (id, geom) VALUES {values_str}"))
                    conn.commit()
                    temp_rows = []
                    count += BATCH_SIZE
                    if count % 2000 == 0:
                        logger.info(f"Inserted {count} towers...")
        
        if temp_rows:
             values_str = ",".join([f"({r['id']}, ST_GeomFromText('{r['wkt']}', 4326))" for r in temp_rows])
             conn.execute(text(f"INSERT INTO global_temp_towers (id, geom) VALUES {values_str}"))
             conn.commit()

        # 3. Run Spatial Update
        logger.info("Updating municipality mobile_tower_count...")
        sql = """
        UPDATE municipalities m
        SET mobile_tower_count = (
            SELECT COUNT(*)
            FROM global_temp_towers t
            WHERE ST_DWithin(
                m.centroid::geography, 
                t.geom::geography, 
                (SQRT(COALESCE(NULLIF(m.area_sqkm, 0), 50.0) / 3.14159) * 1000 * 1.2)
            )
        );
        """
        conn.execute(text(sql))
        conn.commit()
        
        # Cleanup
        conn.execute(text("DROP TABLE global_temp_towers"))
        conn.commit()
        logger.info("Mobile Tower count updated successfully.")

if __name__ == "__main__":
    ingest_mobile_towers()
