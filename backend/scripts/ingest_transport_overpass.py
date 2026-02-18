import logging
import requests
import json
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.infrastructure import TransportNode, TransportType
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

def ingest_transport():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # Process by Region to avoid timeouts
    for region in REGIONS:
        logger.info(f"Processing Transport for {region}...")
        
        # 1. Train Stations
        query_stations = f"""
        [out:json][timeout:120];
        area["name"="Italia"]->.country;
        area["name"="{region}"]["admin_level"="4"](area.country)->.searchArea;
        (
          node["railway"="station"](area.searchArea);
        );
        out body;
        """
        try:
            data = get_overpass_data(query_stations)
            count = 0
            for element in data.get('elements', []):
                try:
                    name = element.get('tags', {}).get('name')
                    if not name: continue
                    
                    sub_type = "regional"
                    if "Aeroporto" in name or "Airport" in name: 
                        sub_type = "airport_link"
                    elif any(k in name for k in ["Centrale", "Porta Nuova", "Termini", "Tiburntina", "Garibaldi"]):
                        sub_type = "major"
                    elif "AV" in name or "Alta Velocità" in name:
                        sub_type = "high_speed"

                    geom = from_shape(Point(element['lon'], element['lat']), srid=4326)
                    
                    existing = db.query(TransportNode).filter(TransportNode.osm_id == element['id']).first()
                    if not existing:
                        node = TransportNode(
                            osm_id=element['id'],
                            name=name,
                            node_type=TransportType.TRAIN_STATION,
                            sub_type=sub_type,
                            geometry=geom
                        )
                        db.add(node)
                    else:
                        existing.name = name
                        existing.sub_type = sub_type
                        existing.geometry = geom
                    
                    count += 1
                except Exception as e:
                    logger.error(f"Error processing station {element.get('id')}: {e}")
            
            db.commit()
            logger.info(f"Ingested {count} Train Stations in {region}.")

        except Exception as e:
            logger.error(f"Failed to fetch stations for {region}: {e}")

        # 2. Highway Exits
        query_exits = f"""
        [out:json][timeout:120];
        area["name"="Italia"]->.country;
        area["name"="{region}"]["admin_level"="4"](area.country)->.searchArea;
        (
          node["highway"="motorway_junction"](area.searchArea);
        );
        out body;
        """
        try:
            data = get_overpass_data(query_exits)
            count = 0
            for element in data.get('elements', []):
                try:
                    name = element.get('tags', {}).get('name')
                    if not name: continue
                    
                    geom = from_shape(Point(element['lon'], element['lat']), srid=4326)
                    
                    existing = db.query(TransportNode).filter(TransportNode.osm_id == element['id']).first()
                    if not existing:
                        node = TransportNode(
                            osm_id=element['id'],
                            name=name,
                            node_type=TransportType.HIGHWAY_EXIT,
                            sub_type="exit",
                            geometry=geom
                        )
                        db.add(node)
                    else:
                        existing.name = name
                        existing.geometry = geom

                    count += 1
                except Exception as e:
                    logger.error(f"Error processing exit {element.get('id')}: {e}")
            
            db.commit()
            logger.info(f"Ingested {count} Highway Exits in {region}.")

        except Exception as e:
            logger.error(f"Failed to fetch exits for {region}: {e}")
        
        # Be polite
        time.sleep(2)

    db.close()

if __name__ == "__main__":
    ingest_transport()

