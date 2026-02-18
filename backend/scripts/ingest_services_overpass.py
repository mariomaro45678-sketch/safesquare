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

def get_overpass_data(query):
    response = requests.post(OVERPASS_URL, data={'data': query})
    response.raise_for_status()
    return response.json()


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


REGIONS = ["Lazio"]

def ingest_services():
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
        },
        {
            "type": ServiceType.SUPERMARKET,
            "query_tag": '["shop"="supermarket"]',
            "label": "Supermarkets"
        }
    ]

    for cfg in services_config:
        for region in REGIONS:
            logger.info(f"Fetching {cfg['label']} for {region}...")
            query = f"""
            [out:json][timeout:180];
            area["name"="Italia"]->.country;
            area["name"="{region}"]["admin_level"="4"](area.country)->.searchArea;
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

                        sub_type = element.get('tags', {}).get('operator') or element.get('tags', {}).get('brand')
                        if sub_type and len(sub_type) > 100: sub_type = sub_type[:97] + "..."

                        geom = from_shape(Point(lon, lat), srid=4326)
                        
                        existing = db.query(ServiceNode).filter(ServiceNode.osm_id == element['id']).first()
                        
                        if not existing:
                            node = ServiceNode(
                                osm_id=element['id'],
                                name=name,
                                service_type=cfg['type'],
                                sub_type=sub_type,
                                geometry=geom
                            )
                            db.add(node)
                        else:
                            existing.name = name
                            existing.geometry = geom
                            existing.sub_type = sub_type

                        count += 1
                        if count % 200 == 0: 
                            db.commit()
                    except Exception as e:
                        logger.error(f"Error processing {cfg['label']} {element.get('id')}: {e}")
                
                db.commit()
                logger.info(f"Ingested {count} {cfg['label']} in {region}.")
                time.sleep(2) # Delay between regions

            except Exception as e:
                logger.error(f"Failed to fetch {cfg['label']} for {region}: {e}")
    
    db.close()

if __name__ == "__main__":
    ingest_services()

