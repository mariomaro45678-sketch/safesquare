import os
import json
import requests
import pandas as pd
import io
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback/Debug
    DATABASE_URL = "postgresql://postgres:password@db:5432/safesquare"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

MAPPING_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "mapping_comuni_arpa.json")

def get_mapping():
    try:
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Mapping file not found at {MAPPING_FILE}")
        return {}

def clean_value(val):
    try:
        v = float(val)
        if v < 0: return None # Filter invalid like -9999
        return v
    except (ValueError, TypeError):
        return None

def upsert_air_quality(db, municipality_id, year, pm10=None, pm25=None, no2=None):
    # Calculate AQI (Simplified)
    aqi_components = []
    if pm10: aqi_components.append(pm10 / 40.0 * 50) 
    if pm25: aqi_components.append(pm25 / 25.0 * 50)
    if no2: aqi_components.append(no2 / 40.0 * 50)
    
    aqi_val = max(aqi_components) if aqi_components else None
    
    risk_level = "Buona"
    if aqi_val:
        if aqi_val > 100: risk_level = "Pessima"
        elif aqi_val > 75: risk_level = "Scarsa"
        elif aqi_val > 50: risk_level = "Mediocre"
        elif aqi_val > 25: risk_level = "Discreta"

    # Check existence
    existing = db.execute(text(
        "SELECT id FROM air_quality WHERE municipality_id = :mid AND year = :year"
    ), {"mid": municipality_id, "year": year}).fetchone()
    
    now = datetime.now()
    
    if existing:
        db.execute(text("""
            UPDATE air_quality 
            SET pm10_avg = :pm10, pm25_avg = :pm25, no2_avg = :no2, 
                aqi_index = :aqi, health_risk_level = :risk, updated_at = :now, data_source = :src
            WHERE id = :id
        """), {
            "pm10": pm10, "pm25": pm25, "no2": no2, "aqi": aqi_val, 
            "risk": risk_level, "now": now, "src": "ARPA Multi-Region", "id": existing[0]
        })
    else:
        db.execute(text("""
            INSERT INTO air_quality (municipality_id, year, pm10_avg, pm25_avg, no2_avg, aqi_index, health_risk_level, data_source, created_at, updated_at)
            VALUES (:mid, :year, :pm10, :pm25, :no2, :aqi, :risk, :src, :now, :now)
        """), {
            "mid": municipality_id, "year": year, 
            "pm10": pm10, "pm25": pm25, "no2": no2, 
            "aqi": aqi_val, "risk": risk_level, "src": "ARPA Multi-Region", "now": now
        })
    db.commit()

# --- Lombardia ---
def ingest_lombardia(mapping, db):
    print("\n--- Ingesting Lombardia ---")
    URL = "https://www.dati.lombardia.it/resource/nicp-bhqi.json?$limit=5000"
    
    # Collect relevant sensor IDs from mapping
    sensor_map = {} # sensor_id -> (municipality_code, pollutant_type)
    for code, data in mapping.items():
        if data.get("region") != "Lombardia": continue
        sensors = data.get("sensors", {})
        for p_type, s_id in sensors.items():
            sensor_map[s_id] = (code, p_type)
            
    print(f"Tracking {len(sensor_map)} sensors for Lombardia.")
    
    try:
        resp = requests.get(URL)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Error fetching Lombardia data: {e}")
        return

    # Aggregate readings
    readings = {} 
    
    for row in data:
        s_id = row.get("idsensore")
        val = clean_value(row.get("valore"))
        if not val or s_id not in sensor_map: continue
        
        mun_code, p_type = sensor_map[s_id]
        
        if mun_code not in readings:
            readings[mun_code] = {"pm10": [], "pm25": [], "no2": []}
            
        readings[mun_code][p_type].append(val)
        
    count = 0
    for code, values in readings.items():
        avg_pm10 = sum(values["pm10"])/len(values["pm10"]) if values["pm10"] else None
        avg_pm25 = sum(values["pm25"])/len(values["pm25"]) if values["pm25"] else None
        avg_no2 = sum(values["no2"])/len(values["no2"]) if values["no2"] else None
        
        res = db.execute(text("SELECT id FROM municipalities WHERE code = :code"), {"code": code}).fetchone()
        if not res: continue
        mun_id = res[0]
        
        upsert_air_quality(db, mun_id, 2024, avg_pm10, avg_pm25, avg_no2)
        count += 1
        
    print(f"Updated {count} municipalities in Lombardia.")

# --- Lazio ---
def ingest_lazio(mapping, db):
    print("\n--- Ingesting Lazio ---")
    # Using 2022 annual data
    URL = "https://dati.lazio.it/dataset/79dfc4f3-6872-4fd9-84e3-786a824509cf/resource/f671c878-9c45-473c-9445-1491da97d123/download/standardcomunali2022_mod.csv"
    
    try:
        resp = requests.get(URL)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text), sep=";")
    except Exception as e:
        print(f"Lazio data source unavailable: {e}. Skipping.")
        return

    count = 0
    df.columns = [c.lower() for c in df.columns]
    
    lazio_muns = {data["municipality_name"].lower(): code for code, data in mapping.items() if data.get("region") == "Lazio"}
    
    for _, row in df.iterrows():
        comune = None
        for col in df.columns:
            if "comune" in col or "localita" in col:
                comune = str(row[col]).lower()
                break
        
        if not comune or comune not in lazio_muns: continue
        
        mun_code = lazio_muns[comune]
        
        pm10, no2, pm25 = None, None, None
        for col in df.columns:
            val = clean_value(row[col])
            if not val: continue
            if "pm10" in col and "media" in col: pm10 = val
            if "no2" in col and "media" in col: no2 = val
            if "pm2.5" in col or ("pm25" in col): pm25 = val
            
        if not (pm10 or no2 or pm25): continue

        res = db.execute(text("SELECT id FROM municipalities WHERE code = :code"), {"code": mun_code}).fetchone()
        if not res: continue
        mun_id = res[0]
        
        upsert_air_quality(db, mun_id, 2022, pm10, pm25, no2)
        count += 1

    print(f"Updated {count} municipalities in Lazio.")


# --- Campania ---
def ingest_campania(mapping, db):
    print("\n--- Ingesting Campania ---")
    URL = "https://dati.regione.campania.it/catalogo/resources/dati-qualita-dellaria_dicembre2018_Napoli.csv"
    
    try:
        resp = requests.get(URL)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text), sep=";")
    except Exception as e:
        print(f"Campania data error: {e}")
        return

    df.columns = [c.lower().strip() for c in df.columns]
    
    campania_muns = {}
    for code, data in mapping.items():
        if data.get("region") == "Campania":
            name = data["municipality_name"].lower()
            campania_muns[name] = code
            
    station_to_mun = {}
    station_data = {} 
    
    for _, row in df.iterrows():
        station_desc = str(row.get("descrizione", "")).lower()
        pollutant = str(row.get("inquinante", "")).lower()
        val = clean_value(row.get("valore"))
        
        if not val: continue
        
        if station_desc not in station_data:
            station_data[station_desc] = {"pm10": [], "pm25": [], "no2": []}
            match = None
            for mun_name, code in campania_muns.items():
                if mun_name in station_desc: 
                    match = code
                    break
            station_to_mun[station_desc] = match
            
        if "pm10" in pollutant: station_data[station_desc]["pm10"].append(val)
        elif "pm2.5" in pollutant or "pm25" in pollutant: station_data[station_desc]["pm25"].append(val)
        elif "no2" in pollutant or "ossidi" in pollutant: station_data[station_desc]["no2"].append(val)
    
    count = 0
    for station_desc, values in station_data.items():
        mun_code = station_to_mun.get(station_desc)
        if not mun_code: continue
        
        avg_pm10 = sum(values["pm10"])/len(values["pm10"]) if values["pm10"] else None
        avg_pm25 = sum(values["pm25"])/len(values["pm25"]) if values["pm25"] else None
        avg_no2 = sum(values["no2"])/len(values["no2"]) if values["no2"] else None
        
        if not (avg_pm10 or avg_pm25 or avg_no2): continue
        
        res = db.execute(text("SELECT id FROM municipalities WHERE code = :code"), {"code": mun_code}).fetchone()
        if not res: continue
        mun_id = res[0]
        
        upsert_air_quality(db, mun_id, 2018, avg_pm10, avg_pm25, avg_no2)
        count += 1
        
    print(f"Updated {count} municipalities in Campania based on station name matching.")

def main():
    mapping = get_mapping()
    db = SessionLocal()
    
    try:
        ingest_lombardia(mapping, db)
        ingest_lazio(mapping, db)
        ingest_campania(mapping, db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
