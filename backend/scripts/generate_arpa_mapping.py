import json
import requests
import os
import sys
import math
import pandas as pd
import io
from collections import defaultdict
from sqlalchemy import create_engine, text, func

# Add parent dir to path for imports if needed, but we'll try to keep it standalone or use app context
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from shapely.geometry import Point

# Load environment variables
load_dotenv()

# Setup Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Configuration ---
REGION_CONFIG = {
    "Lombardia": {
        "region_name": "Lombardia",
        "fetcher": "fetch_lombardia_stations"
    },
    "Lazio": {
        "region_name": "Lazio",
        "fetcher": "fetch_lazio_stations"
    },
    "Campania": {
        "region_name": "Campania",
        "fetcher": "fetch_campania_stations_stub" 
        # Campania lacks a station coordinate file. 
        # We will map by name match during ingestion or manual config if needed.
        # For now, we omit station-based spatial mapping for Campania and rely on string matching in ingestion.
    }
}

# --- Fetchers ---

def fetch_lombardia_stations():
    """
    Fetches station metadata from Socrata (ib47-atvt).
    Returns list of dicts: {id, name, lat, lng, sensors: {type: id}}
    """
    print("Fetching Lombardia stations...")
    url = "https://www.dati.lombardia.it/resource/ib47-atvt.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching Lombardia data: {e}")
        return []

    stations = {}
    
    # Filter for relevant sensor types
    RELEVANT_SENSORS = ["PM10", "PM2.5", "Biossido di Azoto"] # NO2 often labeled 'Biossido di Azoto' or similar codes

    for item in data:
        # Check sensor type
        sensor_type = item.get("nometiposensore")
        if sensor_type not in RELEVANT_SENSORS:
            if "PM10" not in str(sensor_type) and "PM2.5" not in str(sensor_type) and "Azoto" not in str(sensor_type):
                 continue

        station_id = item.get("idstazione")
        if not station_id:
            continue

        if station_id not in stations:
            try:
                lat = float(item.get("lat"))
                lng = float(item.get("lng"))
            except (ValueError, TypeError):
                continue
                
            stations[station_id] = {
                "id": station_id,
                "name": item.get("nomestazione"),
                "municipality": item.get("comune"),
                "lat": lat,
                "lng": lng,
                "sensors": {},
                "region": "Lombardia"
            }
        
        # Map sensor/pollutant type to specific sensor ID
        # Standardize keys: pm10, pm25, no2
        key = None
        if "PM10" in sensor_type: key = "pm10"
        elif "PM2.5" in sensor_type: key = "pm25"
        elif "Azoto" in sensor_type: key = "no2"
        
        if key:
            stations[station_id]["sensors"][key] = item.get("idsensore")

    return list(stations.values())

def fetch_lazio_stations():
    """
    Fetches station metadata from ARPA Lazio CSV.
    URL: https://dati.lazio.it/.../arpaaria2024.csv
    """
    print("Fetching Lazio stations...")
    url = "https://dati.lazio.it/dataset/f50934ce-3e66-4e62-907a-f84a827fd5c2/resource/c7cd1487-103d-4437-b98d-64519f084e6b/download/arpaaria2024.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        # Parse CSV
        df = pd.read_csv(io.StringIO(response.text), sep=";")
    except Exception as e:
        print(f"Error fetching Lazio data: {e}")
        return []

    stations = []
    # Expected cols: Codice stazione;Provincia;Localita';Nome;Tipo;...;Latitudine;Longitudine;...
    
    for _, row in df.iterrows():
        try:
            lat_str = str(row.get("Latitudine", "")).replace(",", ".")
            lng_str = str(row.get("Longitudine", "")).replace(",", ".")
            lat = float(lat_str)
            lng = float(lng_str)
        except (ValueError, TypeError):
            continue

        # Lazio CSV lists stations. It doesn't explicitly list sensors per row like Lombardia.
        # We assume all major stations measure basic pollutants or we filter later during ingestion.
        # For mapping purposes, we just need the location.
        station_id = str(row.get("Codice stazione"))
        
        stations.append({
            "id": station_id,
            "name": row.get("Nome"),
            "municipality": row.get("Localita'"), # Or 'Comune' if available
            "lat": lat,
            "lng": lng,
            "sensors": {"generic": station_id}, # Placeholder, specific sensors might naturally align or need lookup
            "region": "Lazio"
        })
        
    return stations

def fetch_campania_stations_stub():
    """
    Campania Open Data does not provide a clean station list with coordinates (verified in research).
    Mapping for Campania will be done purely by Name Matching in the ingestion script 
    (e.g., matching 'Napoli' in data to 'Napoli' municipality).
    Returning empty list to skip spatial mapping.
    """
    print("Skipping Spatial Mapping for Campania (Name-based matching only).")
    return []


# --- Core Logic ---

def haversine_distance(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, asin, sqrt
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def main():
    db = SessionLocal()
    
    # 1. Collect all stations from all supported regions
    all_stations = []
    for region_key, config in REGION_CONFIG.items():
        fetcher = globals().get(config["fetcher"])
        if fetcher:
            stations = fetcher()
            all_stations.extend(stations)
            print(f"Loaded {len(stations)} stations for {region_key}")

    print(f"Total stations available for spatial mapping: {len(all_stations)}")
    
    # 2. Get Municipalities for target regions
    # We need Region IDs to filter municipalities
    target_regions = ["Lombardia", "Lazio", "Campania"]
    
    # Simple mapping: Municipality Code -> Mapping Info
    master_mapping = {}

    try:
        from app.models.geography import Municipality, Province, Region
        
        # optimized query
        query = db.query(Municipality.code, Municipality.name, Region.name.label("region_name"), 
                         func.ST_Y(Municipality.centroid).label('lat'), 
                         func.ST_X(Municipality.centroid).label('lng')) \
            .join(Province, Municipality.province_id == Province.id) \
            .join(Region, Province.region_id == Region.id) \
            .filter(Region.name.in_(target_regions))
            
        results = query.all()
        print(f"Found {len(results)} municipalities in target regions.")
        
        for mun in results:
            mun_code = mun.code
            mun_name = mun.name
            region = mun.region_name
            mun_lat = mun.lat
            mun_lng = mun.lng
            
            # Find nearest station in the SAME region
            # (Don't map a Lazio town to a Campania station even if closer)
            
            region_stations = [s for s in all_stations if s["region"] == region]
            
            if not region_stations:
                # Fallback for Campania or others with no spatial data:
                # We save a valid entry but without a station_id, 
                # ingestion script will have to try name matching.
                master_mapping[mun_code] = {
                    "municipality_name": mun_name,
                    "region": region,
                    "station_id": None,
                    "station_name": "No Spatial Station Found",
                    "distance_km": None,
                    "sensors": {},
                    "method": "No Spatial Data"
                }
                continue

            nearest_station = None
            min_dist = float('inf')
            
            for station in region_stations:
                dist = haversine_distance(mun_lat, mun_lng, station["lat"], station["lng"])
                if dist < min_dist:
                    min_dist = dist
                    nearest_station = station
            
            mapping_entry = {
                "municipality_name": mun_name,
                "region": region,
                "station_id": None,
                "station_name": None,
                "distance_km": round(min_dist, 2) if min_dist != float('inf') else None,
                "sensors": {},
                "method": "Spatial"
            }
            
            if nearest_station:
                mapping_entry["station_id"] = nearest_station["id"]
                mapping_entry["station_name"] = nearest_station["name"]
                mapping_entry["sensors"] = nearest_station["sensors"]
            
            master_mapping[mun_code] = mapping_entry

        # Robust path resolution
        output_file = os.path.join(os.path.dirname(__file__), "..", "data", "mapping_comuni_arpa.json")
        output_file = os.path.normpath(output_file)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(master_mapping, f, indent=2)
            
        print(f"Mapping saved to {output_file}. Mapped {len(master_mapping)} municipalities.")

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
