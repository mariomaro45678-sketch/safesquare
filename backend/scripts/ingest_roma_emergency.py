
import logging
import requests
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.services import ServiceNode, ServiceType
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def get_overpass_data(query):
    response = requests.post(OVERPASS_URL, data={'data': query})
    response.raise_for_status()
    return response.json()

def ingest_roma_emergency():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    services_config = [
        {
            "type": ServiceType.HOSPITAL,
            "query_tag": '["amenity"="hospital"]',
            "label": "Hospitals"
        },
        {
            "type": ServiceType.SCHOOL,
            "query_tag": '["amenity"="school"]',
            "label": "Schools"
        }
    ]

    for cfg in services_config:
        logger.info(f"Fetching {cfg['label']} for Roma city specifically...")
        query = f"""
        [out:json][timeout:180];
        area["name"="Roma"]["admin_level"="8"]->.searchArea;
        (
          node{cfg['query_tag']}(area.searchArea);
          way{cfg['query_tag']}(area.searchArea);
          relation{cfg['query_tag']}(area.searchArea);
        );
        out center body;
        """
        try:
            data = get_overpass_data(query)
            count = 0
            for element in data.get('elements', []):
                try:
                    name = element.get('tags', {}).get('name') or f"Unnamed {cfg['label']}"
                    if len(name) > 255: name = name[:252] + "..."
                    
                    lon = element.get('lon') or element.get('center', {}).get('lon')
                    lat = element.get('lat') or element.get('center', {}).get('lat')
                    if lon is None or lat is None: continue

                    geom = from_shape(Point(lon, lat), srid=4326)
                    existing = db.query(ServiceNode).filter(ServiceNode.osm_id == element['id']).first()
                    
                    if not existing:
                        node = ServiceNode(
                            osm_id=element['id'],
                            name=name,
                            service_type=cfg['type'],
                            geometry=geom
                        )
                        db.add(node)
                    count += 1
                except Exception as e:
                    logger.error(f"Error processing {element.get('id')}: {e}")
            
            db.commit()
            logger.info(f"Emergency ingested {count} {cfg['label']} in Roma.")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Failed to fetch {cfg['label']} for Roma: {e}")

    db.close()

if __name__ == "__main__":
    ingest_roma_emergency()
