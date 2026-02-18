
import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, text
from app.models.risk import AirQuality
from app.models.geography import Municipality
from app.core.config import settings
from geopy.distance import geodesic
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Data Paths
DATA_DIR = Path("backend/data")
VENETO_FILE = DATA_DIR / "veneto_historical.json"
LAZIO_FILE = DATA_DIR / "lazio_historical.json"
CAMPANIA_FILE = DATA_DIR / "campania_historical.json"
EMILIA_FILE = DATA_DIR / "emilia_historical.json"
LOMBARDIA_FILE = DATA_DIR / "lombardia_historical.json"
MAPPING_FILE = DATA_DIR / "mapping_comuni_arpa.json"
STATIONS_FILE = DATA_DIR / "arpa_stations.json"

def get_db_session():
    engine = create_engine(str(settings.DATABASE_URL))
    return Session(engine)

def load_json(filepath):
    if not filepath.exists():
        logger.warning(f"File not found: {filepath}")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_stations_metadata():
    stations = load_json(STATIONS_FILE)
    return {s['station_id']: (s['latitude'], s['longitude']) for s in stations if 'latitude' in s and 'longitude' in s}

def load_municipalities(session: Session):
    """Load all municipalities with their centroids (or just coords if geom complex)."""
    # For MVP, we assume we can get lat/lon directly or compute centroid from geometry
    # If geometry is WKB, let's assume we fetch WKT or lat/lon columns if they exist.
    # Checking Municipality model: it likely has geometry. 
    # For speed, let's fetch all and do in-memory distance check if count is manageable (<8000).
    # Ideally, we used PostGIS: ORDER BY geom <-> point LIMIT 1.
    
    # We will query the DB for each point if bulk loading is too slow/complex to code now. 
    # But 8000 munis in memory is fine.
    
    # Let's try to fetch lat/lon from DB. 
    # If Municipality model doesn't have lat/lon columns, we might need to use st_x(st_centroid(geom)).
    
    query = text("SELECT id, name, code, ST_Y(centroid) as lat, ST_X(centroid) as lon FROM municipalities")
    try:
        result = session.execute(query).fetchall()
        return [
            {"id": r.id, "name": r.name, "istat_code": r.code, "lat": r.lat, "lon": r.lon} 
            for r in result
        ]
    except Exception as e:
        logger.error(f"Error fetching municipalities: {e}")
        return []

def find_nearest_municipality(lat, lon, municipalities):
    if not municipalities:
        return None
    
    # Simple Euclidean distance squared for speed (valid for small distances) or geodesic
    # For Italy, simple dist is roughly ok for nearest neighbor.
    # Optimization: Filter by rough bounding box if needed.
    
    nearest = None
    min_dist = float('inf')
    
    for muni in municipalities:
        if muni['lat'] is None or muni['lon'] is None:
            continue
        # Simple euclid approx (degrees)
        dist = (muni['lat'] - lat)**2 + (muni['lon'] - lon)**2
        if dist < min_dist:
            min_dist = dist
            nearest = muni
            
    return nearest

def clean_campania_name(station_id):
    # Format: CAM_Acerra_Scuola_Capora -> Acerra
    parts = station_id.split('_')
    if len(parts) > 1:
        # Try to match the first meaningful part. 
        # Often parts[1] is the city.
        return parts[1]
    return station_id

def ingest_air_quality():
    session = get_db_session()
    
    logger.info("Loading metadata...")
    stations_meta = load_stations_metadata()
    municipalities = load_municipalities(session)
    logger.info(f"Loaded {len(stations_meta)} stations and {len(municipalities)} municipalities.")
    
    records_to_upsert = []
    
    # 1. LATINA/LAZIO (ISTAT Based)
    logger.info("Processing Lazio...")
    lazio_data = load_json(LAZIO_FILE)
    for row in lazio_data:
        istat = str(row.get('istat_code', ''))
        # If 8 digits, strip region prefix (first 2) to get 6-digit ISTAT
        if len(istat) == 8:
            istat = istat[2:]
        elif len(istat) == 5: # handle leading zero loss
            istat = istat.zfill(6)
            
        muni = next((m for m in municipalities if str(m['istat_code']) == istat), None)
        if muni:
            records_to_upsert.append({
                "municipality_id": muni['id'],
                "year": row.get('year'),
                "pm10": row.get('pm10_avg'),
                "pm25": row.get('pm25_avg'),
                "no2": row.get('no2_avg'),
                "o3": None,
                "data_source": "ARPA Lazio"
            })
            
    # 2. VENETO (Station ID -> Metadata -> Nearest Muni)
    logger.info("Processing Veneto...")
    veneto_data = load_json(VENETO_FILE)
    for row in veneto_data:
        station_id = row.get('station_id')
        coords = stations_meta.get(station_id)
        if coords:
            muni = find_nearest_municipality(coords[0], coords[1], municipalities)
            if muni:
                records_to_upsert.append({
                    "municipality_id": muni['id'],
                    "year": row.get('year'),
                    "pm10": row.get('pm10_avg'),
                    "pm25": None,
                    "no2": None,
                    "o3": row.get('o3_avg'),
                    "data_source": "ARPA Veneto"
                })
        else:
            logger.debug(f"Missing coords for Veneto station {station_id}")

    # 3. EMILIA (Lat/Lon in JSON -> Nearest Muni)
    logger.info("Processing Emilia...")
    emilia_data = load_json(EMILIA_FILE)
    for row in emilia_data:
        lat, lon = row.get('latitude'), row.get('longitude')
        if lat and lon:
            muni = find_nearest_municipality(lat, lon, municipalities)
            if muni:
                records_to_upsert.append({
                    "municipality_id": muni['id'],
                    "year": row.get('year'),
                    "pm10": row.get('pm10_avg'),
                    "pm25": row.get('pm25_avg'),
                    "no2": row.get('no2_avg'),
                    "o3": None,
                    "data_source": "ARPA Emilia"
                })

    # 4. CAMPANIA (Name Matching -> Muni Name)
    logger.info("Processing Campania...")
    campania_data = load_json(CAMPANIA_FILE)
    for row in campania_data:
        station_id = row.get('station_id')
        city_name = clean_campania_name(station_id)
        # Fuzzy match or direct match
        muni = next((m for m in municipalities if city_name.lower() in m['name'].lower()), None)
        if muni:
             records_to_upsert.append({
                "municipality_id": muni['id'],
                "year": row.get('year'),
                "pm10": row.get('pm10_avg'),
                "pm25": row.get('pm25_avg'),
                "no2": row.get('no2_avg'),
                "o3": None,
                "data_source": "ARPA Campania"
            })
    

    # 5. LOMBARDIA (Weighted Mapping)
    logger.info("Processing Lombardia (Weighted Mapping)...")
    if LOMBARDIA_FILE.exists() and MAPPING_FILE.exists():
        lombardia_raw = load_json(LOMBARDIA_FILE)
        # Organize Lombardia data by Station -> Year -> Data
        lombardia_map = {}
        processed_years = set()
        for row in lombardia_raw:
            sid = str(row.get('station_id'))
            year = row.get('year')
            if year: processed_years.add(year)
            if sid not in lombardia_map:
                lombardia_map[sid] = {}
            lombardia_map[sid][year] = row

        mapping_data = load_json(MAPPING_FILE)
        
        # Iterate over all mapped municipalities
        for muni_id_str, method in mapping_data.items():
            # method is like {"name": "...", "stations": [...]}
            # Check if this muni exists in our DB keys (loaded municipalities)
            # muni_id_str might be istat or internal id?
            # From previous context, mapping_comuni_arpa uses ISTAT codes (numeric strings).
            # Our `municipalities` list has `istat_code`.
            
            # Find DB ID for this ISTAT code
            # Note: mapping keys might be int or string.
            muni_match = next((m for m in municipalities if str(m['istat_code']) == str(muni_id_str).zfill(6)), None)
            if not muni_match:
                continue
                
            stations_list = method.get('stations', [])
            if not stations_list:
                continue
                
            # For each year in the dataset
            for year in sorted(list(processed_years)):
                # Calculate weighted avg
                # Formula: sum(value * weight) / sum(weight)  (for available stations)
                
                sums = {"pm10": 0, "pm25": 0, "no2": 0, "o3": 0}
                weights = {"pm10": 0, "pm25": 0, "no2": 0, "o3": 0}
                
                for s_info in stations_list:
                    s_id = str(s_info.get('station_id')) # Mapped ID (e.g. 501)
                    # Lombardia JSON uses "L_501". We need to handle this prefix difference if it exists.
                    # Let's check if mapping uses raw numbers.
                    # If mapping says "501", lombardia json says "L_501".
                    # Try both.
                    
                    s_data = lombardia_map.get(s_id) or lombardia_map.get(f"L_{s_id}")
                    if not s_data: continue
                    
                    year_data = s_data.get(year)
                    if not year_data: continue
                    
                    w = s_info.get('weight', 1.0)
                    
                    for poll in ["pm10", "pm25", "no2", "o3"]:
                        key = f"{poll}_avg"
                        val = year_data.get(key)
                        if val is not None:
                            sums[poll] += (val * w)
                            weights[poll] += w
                
                # If we have data for this year/muni
                if any(weights.values()):
                    records_to_upsert.append({
                        "municipality_id": muni_match['id'],
                        "year": year,
                        "pm10": sums['pm10'] / weights['pm10'] if weights['pm10'] > 0 else None,
                        "pm25": sums['pm25'] / weights['pm25'] if weights['pm25'] > 0 else None,
                        "no2": sums['no2'] / weights['no2'] if weights['no2'] > 0 else None,
                        "o3": sums['o3'] / weights['o3'] if weights['o3'] > 0 else None,
                        "data_source": "ARPA Lombardia (Weighted)"
                    })
    else:
        logger.warning("Skipping Lombardia: Missing data or mapping file.")

    logger.info(f"Prepared {len(records_to_upsert)} records for ingestion.")
    
    # Bulk Upsert
    # We aggregate by municipality/year (averaging if multiple stations hit same muni)
    # Simpler: Dictionary keyed by (muni_id, year) -> Accumulates sums/counts -> Averages
    
    aggregated = {}
    for r in records_to_upsert:
        key = (r['municipality_id'], r['year'])
        if key not in aggregated:
            aggregated[key] = {
                "pm10_sum": 0, "pm10_count": 0,
                "pm25_sum": 0, "pm25_count": 0,
                "no2_sum": 0, "no2_count": 0,
                "o3_sum": 0, "o3_count": 0,
                "sources": set()
            }
        
        agg = aggregated[key]
        if r['pm10'] is not None:
            agg['pm10_sum'] += r['pm10']
            agg['pm10_count'] += 1
        if r['pm25'] is not None:
            agg['pm25_sum'] += r['pm25']
            agg['pm25_count'] += 1
        if r['no2'] is not None:
            agg['no2_sum'] += r['no2']
            agg['no2_count'] += 1
        if r['o3'] is not None:
            agg['o3_sum'] += r['o3']
            agg['o3_count'] += 1
        agg['sources'].add(r['data_source'])

    final_objects = []
    for (muni_id, year), agg in aggregated.items():
        if year is None: continue 
        
        final_objects.append({
            "municipality_id": muni_id,
            "year": int(year),
            "pm10_avg": agg['pm10_sum'] / agg['pm10_count'] if agg['pm10_count'] > 0 else None,
            "pm25_avg": agg['pm25_sum'] / agg['pm25_count'] if agg['pm25_count'] > 0 else None,
            "no2_avg": agg['no2_sum'] / agg['no2_count'] if agg['no2_count'] > 0 else None,
            "o3_avg": agg['o3_sum'] / agg['o3_count'] if agg['o3_count'] > 0 else None,
            "data_source": ", ".join(agg['sources']),
            "station_count": max(agg['pm10_count'], agg['pm25_count'], agg['no2_count'], agg['o3_count'])
        })

    logger.info(f"Upserting {len(final_objects)} aggregated air quality records.")
    
    # Upsert Logic (Delete existing for year/muni or Merge)
    # Safer to just use simple merge if supported, or loop-upsert.
    # Or using basic SQLAlchemy merge?
    
    processed = 0
    for obj in final_objects:
        # Check if exists
        # Also handle cleaning up 'Interpolated' data for this muni/year
        session.query(AirQuality).filter(
            AirQuality.municipality_id == obj['municipality_id'],
            AirQuality.year == obj['year'],
            AirQuality.data_source.like("%Interpolated%")
        ).delete(synchronize_session=False)

        existing = session.query(AirQuality).filter_by(municipality_id=obj['municipality_id'], year=obj['year']).first()
        if existing:
            existing.pm10_avg = obj['pm10_avg']
            existing.pm25_avg = obj['pm25_avg']
            existing.no2_avg = obj['no2_avg']
            existing.o3_avg = obj['o3_avg']
            existing.data_source = obj['data_source']
            existing.station_count = obj['station_count']
        else:
            new_aq = AirQuality(**obj)
            session.add(new_aq)
        processed += 1
        
        if processed % 1000 == 0:
            session.commit()
            logger.info(f"Committed {processed} records...")
            
    session.commit()
    logger.info("Ingestion Complete.")

if __name__ == "__main__":
    ingest_air_quality()
