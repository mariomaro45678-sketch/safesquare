
import json
import math
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
from dotenv import load_dotenv
from tqdm import tqdm

# Load env vars
load_dotenv()

# Add the project root to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.core.config import settings
from app.models.geography import Municipality


# Haversine formula for distance
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def create_mapping():
    print("Loading ARPA stations...")
    stations_file = Path("backend/data/arpa_stations.json")
    if not stations_file.exists():
        print("Error: stations file not found!")
        return
        
    with open(stations_file, 'r', encoding='utf-8') as f:
        stations = json.load(f)
        
    print(f"Loaded {len(stations)} stations.")
    
    # DB Connection
    db_url = str(settings.DATABASE_URL).replace("database", "localhost")
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Use ST_X and ST_Y to get coordinates from the centroid
    from geoalchemy2.functions import ST_X, ST_Y
    
    try:
        # Query ID, Code, Name, and Coordinates directly
        # We need to cast the centroid to geometry to extract coordinates
        municipalities = db.query(
            Municipality.code,
            Municipality.name,
            ST_Y(Municipality.centroid).label('latitude'),
            ST_X(Municipality.centroid).label('longitude')
        ).filter(Municipality.centroid.isnot(None)).all()
        
        print(f"Mapping {len(municipalities)} municipalities...")
        
        mapping = {}
        
        for mun in tqdm(municipalities):
            # mun is now a named tuple-like result due to specific column selection
            if not mun.latitude or not mun.longitude:
                continue
                
            # Find nearest 3 stations
            distances = []
            for station in stations:
                dist = haversine_distance(
                    float(mun.latitude), float(mun.longitude), 
                    station['latitude'], station['longitude']
                )
                distances.append({
                    "station_id": station['station_id'],
                    "distance_km": dist,
                    "weight": 0
                })
            
            # Sort by distance
            distances.sort(key=lambda x: x['distance_km'])
            
            # Take top 3
            nearest = distances[:3]
            
            # Calculate IDW weights (Inverse Distance Weighting)
            # weight = 1 / distance^2
            # Handle 0 distance
            total_inv_dist = 0
            for item in nearest:
                dist = max(item['distance_km'], 0.1) # Avoid div by zero
                item['inv_dist'] = 1 / (dist ** 2)
                total_inv_dist += item['inv_dist']
                
            # Normalize weights
            final_stations = []
            for item in nearest:
                weight = item['inv_dist'] / total_inv_dist
                final_stations.append({
                    "station_id": item['station_id'],
                    "distance_km": round(item['distance_km'], 2),
                    "weight": round(weight, 4)
                })
                
            mapping[mun.code] = {
                "municipality_name": mun.name,
                "stations": final_stations
            }
            
        output_file = Path("backend/data/mapping_comuni_arpa.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=None, ensure_ascii=False)
            
        print(f"Mapping saved to {output_file}")
        
    finally:
        db.close()

if __name__ == "__main__":
    create_mapping()
