
import requests
import pandas as pd
import json
import csv
import os
import time
from pathlib import Path

# Configuration
EEA_METADATA_URL = "https://discomap.eea.europa.eu/map/fme/AirQualityExport.htm" # Placeholder
# Actual EEA metadata is often retrieved via other means, but we'll try a known reliable endpoint or fallback
# Better source for Italy: ARPA Lombardia Open Data (for a start)
LOMBARDIA_API = "https://www.dati.lombardia.it/resource/648a-798d.json" 

OUTPUT_FILE = "backend/data/arpa_stations.json"

def fetch_lombardia_stations():
    print("Fetching ARPA Lombardia stations...")
    try:
        response = requests.get(LOMBARDIA_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        stations = []
        for item in data:
            if 'location' in item and 'latitude' in item['location']:
                stations.append({
                    "station_id": item.get('codice_eu', item.get('idsensore', 'UNKNOWN')),
                    "name": item.get('nome_stazione', 'Unknown'),
                    "municipality": item.get('comune', 'Unknown'),
                    "latitude": float(item['location']['latitude']),
                    "longitude": float(item['location']['longitude']),
                    "region": "Lombardia",
                    "source": "ARPA Lombardia Open Data",
                    "is_synthetic": False
                })
        print(f"  Found {len(stations)} stations in Lombardia.")
        return stations
    except Exception as e:
        print(f"  Failed to fetch Lombardia data: {e}")
        return []

def generate_synthetic_stations(existing_count=0):
    print("Generating synthetic stations for national coverage...")
    # Major Italian cities coordinates to simulate station coverage
    cities = [
        {"name": "Roma", "lat": 41.9028, "lon": 12.4964, "reg": "Lazio"},
        {"name": "Milano", "lat": 45.4642, "lon": 9.1900, "reg": "Lombardia"},
        {"name": "Napoli", "lat": 40.8518, "lon": 14.2681, "reg": "Campania"},
        {"name": "Torino", "lat": 45.0703, "lon": 7.6869, "reg": "Piemonte"},
        {"name": "Palermo", "lat": 38.1157, "lon": 13.3615, "reg": "Sicilia"},
        {"name": "Genova", "lat": 44.4056, "lon": 8.9463, "reg": "Liguria"},
        {"name": "Bologna", "lat": 44.4949, "lon": 11.3426, "reg": "Emilia-Romagna"},
        {"name": "Firenze", "lat": 43.7696, "lon": 11.2558, "reg": "Toscana"},
        {"name": "Bari", "lat": 41.1171, "lon": 16.8719, "reg": "Puglia"},
        {"name": "Catania", "lat": 37.5079, "lon": 15.0830, "reg": "Sicilia"},
        {"name": "Venezia", "lat": 45.4408, "lon": 12.3155, "reg": "Veneto"},
        {"name": "Verona", "lat": 45.4384, "lon": 10.9916, "reg": "Veneto"},
        {"name": "Messina", "lat": 38.1938, "lon": 15.5540, "reg": "Sicilia"},
        {"name": "Padova", "lat": 45.4064, "lon": 11.8768, "reg": "Veneto"},
        {"name": "Trieste", "lat": 45.6495, "lon": 13.7768, "reg": "Friuli-Venezia Giulia"},
        {"name": "Taranto", "lat": 40.4740, "lon": 17.2470, "reg": "Puglia"},
        {"name": "Brescia", "lat": 45.5416, "lon": 10.2118, "reg": "Lombardia"},
        {"name": "Prato", "lat": 43.8777, "lon": 11.1022, "reg": "Toscana"},
        {"name": "Parma", "lat": 44.8015, "lon": 10.3279, "reg": "Emilia-Romagna"},
        {"name": "Modena", "lat": 44.6471, "lon": 10.9252, "reg": "Emilia-Romagna"}
    ]
    
    stations = []
    base_id = 9000
    for city in cities:
        # Create 2-3 stations per major city to simulate network
        for i in range(2):
            stations.append({
                "station_id": f"SYNTH_{base_id + i}",
                "name": f"{city['name']} Station {i+1}",
                "municipality": city['name'],
                # Add slight random offset to separate stations
                "latitude": city['lat'] + (0.01 * (i if i%2==0 else -i)),
                "longitude": city['lon'] + (0.01 * (i if i%2!=0 else -i)),
                "region": city['reg'],
                "source": "Synthetic Baseline",
                "is_synthetic": True
            })
            base_id += 1
            
    print(f"  Generated {len(stations)} synthetic stations for coverage.")
    return stations

def get_piemonte_baseline():
    """
    Returns manually defined stations for Piemonte based on the SRRQA map.
    Covers all provincial capitals and key industrial areas.
    """
    print("Loading Piemonte SRRQA baseline from map...")
    stations = [
        {"station_id": "P_TO_01", "name": "Torino - Consolata (Urban)", "municipality": "Torino", "latitude": 45.0766, "longitude": 7.6806, "region": "Piemonte"},
        {"station_id": "P_TO_02", "name": "Torino - Lingotto (Traffic)", "municipality": "Torino", "latitude": 45.0264, "longitude": 7.6651, "region": "Piemonte"},
        {"station_id": "P_TO_03", "name": "Torino - Rebaudengo (Traffic)", "municipality": "Torino", "latitude": 45.1052, "longitude": 7.6974, "region": "Piemonte"},
        {"station_id": "P_TO_04", "name": "Ivrea", "municipality": "Ivrea", "latitude": 45.4667, "longitude": 7.8667, "region": "Piemonte"},
        {"station_id": "P_NO_01", "name": "Novara", "municipality": "Novara", "latitude": 45.4459, "longitude": 8.6232, "region": "Piemonte"},
        {"station_id": "P_VC_01", "name": "Vercelli", "municipality": "Vercelli", "latitude": 45.3205, "longitude": 8.4215, "region": "Piemonte"},
        {"station_id": "P_BI_01", "name": "Biella", "municipality": "Biella", "latitude": 45.5629, "longitude": 8.0583, "region": "Piemonte"},
        {"station_id": "P_VB_01", "name": "Verbania", "municipality": "Verbania", "latitude": 45.9238, "longitude": 8.5516, "region": "Piemonte"},
        {"station_id": "P_VB_02", "name": "Domodossola", "municipality": "Domodossola", "latitude": 46.1167, "longitude": 8.2833, "region": "Piemonte"},
        {"station_id": "P_AT_01", "name": "Asti", "municipality": "Asti", "latitude": 44.8997, "longitude": 8.2045, "region": "Piemonte"},
        {"station_id": "P_AL_01", "name": "Alessandria", "municipality": "Alessandria", "latitude": 44.9122, "longitude": 8.6180, "region": "Piemonte"},
        {"station_id": "P_AL_02", "name": "Novi Ligure", "municipality": "Novi Ligure", "latitude": 44.7618, "longitude": 8.7857, "region": "Piemonte"},
        {"station_id": "P_CN_01", "name": "Cuneo", "municipality": "Cuneo", "latitude": 44.3845, "longitude": 7.5427, "region": "Piemonte"},
        {"station_id": "P_CN_02", "name": "Alba", "municipality": "Alba", "latitude": 44.6993, "longitude": 8.0361, "region": "Piemonte"}
    ]
    # Add common fields
    for s in stations:
        s.update({"source": "Piemonte SRRQA Map", "is_synthetic": False})
    return stations

def get_veneto_data():
    """
    Fetches real station data from ARPA Veneto JSON endpoints.
    Merges stats.json (metadata) with coords.json (location).
    """
    print("Fetching ARPA Veneto stations...")
    stats_url = "https://www2.arpa.veneto.it/aria-json/exported/aria/stats.json"
    coords_url = "https://www2.arpa.veneto.it/aria-json/exported/aria/coords.json"
    
    try:
        # Fetch Data
        r_stats = requests.get(stats_url, timeout=15, verify=False)
        r_coords = requests.get(coords_url, timeout=15, verify=False)
        
        stats_data = r_stats.json()
        coords_data = r_coords.json()
        
        stations = []
        
        # 1. Index Coordinates by Station ID
        # coords.json -> {'coordinate': [{'codseqst': '...', 'lat': '...', 'lon': '...'}, ...]}
        coords_map = {}
        if 'coordinate' in coords_data:
            for item in coords_data['coordinate']:
                s_id = str(item.get('codseqst', ''))
                if s_id:
                    coords_map[s_id] = {
                        'lat': float(item.get('lat', 0)),
                        'lon': float(item.get('lon', 0))
                    }
                    
        # 2. Iterate Metadata and Merge
        # stats.json -> {'stazioni': [{'codseqst': '...', 'nome': '...', ...}, ...]}
        if 'stazioni' in stats_data:
            for item in stats_data['stazioni']:
                s_id = str(item.get('codseqst', ''))
                
                # Check if we have coords for this station
                if s_id in coords_map:
                    coords = coords_map[s_id]
                    stations.append({
                        "station_id": f"V_{s_id}",
                        "name": item.get('nome', 'Unknown'),
                        "municipality": item.get('comune', 'Unknown'),
                        "latitude": coords['lat'],
                        "longitude": coords['lon'],
                        "region": "Veneto",
                        "source": "ARPA Veneto JSON",
                        "is_synthetic": False
                    })
                    
        print(f"  Found {len(stations)} stations in Veneto.")
        return stations
        
    except Exception as e:
        print(f"  Failed to fetch Veneto data: {e}")
        return []

def get_emilia_romagna_data():
    """
    Fetches real station data from ARPAE Emilia-Romagna Google Sheet (CSV export).
    Contains: Cod_staz, Stazione, LAT_GEO, LON_GEO
    """
    print("Fetching ARPAE Emilia-Romagna stations...")
    url = "https://docs.google.com/spreadsheets/d/1-4wgZ8JeLeg0bODTSFUrshPY-_y9mERUu0FJtSFr78s/export?format=csv"
    
    try:
        response = requests.get(url, timeout=15, verify=False)
        response.raise_for_status()
        
        # Parse CSV
        content = response.content.decode('utf-8')
        lines = content.splitlines()
        reader = csv.DictReader(lines)
        
        stations = {}
        count = 0
        
        for row in reader:
            s_id = row.get('Cod_staz', '').strip()
            if not s_id: continue
            
            # Remove dots from ID for consistency (e.g. 7.000.014 -> 7000014)
            # The measurement file uses IDs like 9000070 (no dots)
            clean_id = s_id.replace('.', '')
            
            # Avoid duplicates (CSV has one row per parameter)
            if clean_id in stations:
                continue
                
            lat_str = row.get('LAT_GEO', '').replace(',', '.')
            lon_str = row.get('LON_GEO', '').replace(',', '.')
            
            if lat_str and lon_str:
                try:
                    stations[clean_id] = {
                        "station_id": clean_id,
                        "name": row.get('Stazione', 'Unknown').title(),
                        "municipality": row.get('COMUNE', 'Unknown').title(),
                        "latitude": float(lat_str),
                        "longitude": float(lon_str),
                        "region": "Emilia-Romagna",
                        "source": "ARPAE Open Data",
                        "is_synthetic": False
                    }
                    count += 1
                except ValueError:
                    continue
                    
        result = list(stations.values())
        print(f"  Found {len(result)} stations in Emilia-Romagna.")
        print(f"  Found {len(result)} stations in Emilia-Romagna.")
        return result
        
    except Exception as e:
        print(f"  Failed to fetch Emilia-Romagna data: {e}")
        return []

def get_lombardia_data():
    """
    Parses local CSV file for Lombardia stations.
    Path: C:/Users/pap/Downloads/SafeSquare/Stazioni_qualità_dell'aria_NRT_20260130.csv
    Contains: IdStazione, NomeStazione, Comune, lat, lng
    """
    print("Loading Lombardia stations from local CSV...")
    # csv_path = Path("C:/Users/pap/Downloads/SafeSquare/Stazioni_qualità_dell'aria_NRT_20260130.csv")
    # Using relative path assuming script runs from C:\Users\pap\Downloads\SafeSquare
    csv_path = Path("Stazioni_qualità_dell'aria_NRT_20260130.csv")
    
    if not csv_path.exists():
        print(f"  Warning: Lombardia CSV not found at {csv_path}")
        return []
        
    try:
        stations = {}
        with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                s_id = row.get('IdStazione', '').strip()
                if not s_id: continue
                
                if s_id in stations:
                    continue
                    
                lat_str = row.get('lat', '').replace(',', '.')
                lon_str = row.get('lng', '').replace(',', '.')
                
                if lat_str and lon_str:
                    try:
                        stations[s_id] = {
                            "station_id": f"L_{s_id}",
                            "name": row.get('NomeStazione', 'Unknown').strip(),
                            "municipality": row.get('Comune', 'Unknown').strip(),
                            "latitude": float(lat_str),
                            "longitude": float(lon_str),
                            "region": "Lombardia",
                            "source": "ARPA Lombardia Open Data",
                            "is_synthetic": False
                        }
                    except ValueError:
                        continue
                        
        result = list(stations.values())
        print(f"  Found {len(result)} stations in Lombardia.")
        print(f"  Found {len(result)} stations in Lombardia.")
        return result
        
    except Exception as e:
        print(f"  Failed to parse Lombardia CSV: {e}")
        return []

def get_lazio_data():
    """
    Parses local JSON file for Lazio stations.
    Path: stazioni_lazio.json
    Format: {"fields": [...], "records": [[id, code, prov, loc, name, ...], ...]}
    """
    print("Loading Lazio stations from local JSON...")
    json_path = Path("stazioni_lazio.json")
    
    if not json_path.exists():
        print(f"  Warning: Lazio JSON not found at {json_path}")
        return []
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        records = data.get('records', [])
        stations = []
        
        # Field mapping based on inspection:
        # 0: _id, 1: Codice stazione, 2: Provincia, 3: Localita', 4: Nome, 
        # 7: Latitudine, 8: Longitudine
        
        for row in records:
            if len(row) < 9: continue
            
            s_id = str(row[1])
            name = row[4]
            city = row[3]
            lat_str = row[7].replace(',', '.')
            lon_str = row[8].replace(',', '.')
            
            try:
                stations.append({
                    "station_id": f"Lazio_{s_id}",
                    "name": name,
                    "municipality": city,
                    "latitude": float(lat_str),
                    "longitude": float(lon_str),
                    "region": "Lazio",
                    "source": "ARPA Lazio Open Data",
                    "is_synthetic": False
                })
            except (ValueError, TypeError):
                continue
                
        print(f"  Found {len(stations)} stations in Lazio.")
        return stations
        
    except Exception as e:
        print(f"  Failed to parse Lazio JSON: {e}")
        return []

def get_campania_data():
    """
    Parses local HTML file for Campania stations.
    Path: Rete di Monitoraggio Regionale - Arpac.html
    Strategy: Extract station names from table cells and map to hardcoded city coordinates.
    """
    print("Loading Campania stations from local HTML...")
    html_path = Path("Rete di Monitoraggio Regionale - Arpac.html")
    
    if not html_path.exists():
        print(f"  Warning: Campania HTML not found at {html_path}")
        return []
    
    # Approx coordinates for cities found in the HTML list
    CITY_COORDS = {
        "Acerra": (40.9413, 14.3688),
        "Aversa": (40.9728, 14.2053),
        "Caserta": (41.0718, 14.3323),
        "Casoria": (40.9048, 14.2917),
        "Maddaloni": (41.0378, 14.3822),
        "Napoli": (40.8518, 14.2681),
        "Pomigliano": (40.9167, 14.3833), # Pomigliano D’Arco
        "Portici": (40.8197, 14.3411),
        "Pozzuoli": (40.8258, 14.1206),
        "S.Vitaliano": (40.9231, 14.4764),
        "Torre Annunziata": (40.7570, 14.4444),
        "Volla": (40.8664, 14.3331),
        "Avellino": (40.9144, 14.7969),
        "Battipaglia": (40.6139, 14.9856),
        "Benevento": (41.1292, 14.7830),
        "Cava dei Tirreni": (40.7011, 14.7083),
        "Nocera Inferiore": (40.7428, 14.6406),
        "Polla": (40.5186, 15.4950),
        "Salerno": (40.6824, 14.7681),
        "S. Felice a Cancello": (41.0183, 14.4822),
        "Solofra": (40.8353, 14.8506),
        "Ariano Irpino": (41.1519, 15.0886),
        "Ottati": (40.4578, 15.3131),
        "San Vitaliano": (40.9231, 14.4764)
    }

    try:
        stations = []
        with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Simple regex to find table cells with probable station names
        # Pattern looks for <td align="left">Station Name</td>
        import re
        matches = re.findall(r'<td align="left">([^<]+)</td>', content)
        
        unique_names = set()
        
        for name in matches:
            name = name.strip()
            if not name or name in unique_names:
                continue
            
            unique_names.add(name)
            
            # Find city
            found_city = None
            lat, lon = 0.0, 0.0
            
            # Check if name starts with a known city
            for city, coords in CITY_COORDS.items():
                if name.startswith(city) or city in name:
                    found_city = city
                    lat, lon = coords
                    break
            
            if found_city:
                # Add random jitter to coordinates if multiple stations in same city
                # to prevent complete overlap (e.g. Napoli has multiple)
                import random
                offset_lat = (random.random() - 0.5) * 0.02
                offset_lon = (random.random() - 0.5) * 0.02
                
                stations.append({
                    "station_id": f"CAM_{name.replace(' ', '_')[:20]}",
                    "name": name,
                    "municipality": found_city,
                    "latitude": lat + offset_lat,
                    "longitude": lon + offset_lon,
                    "region": "Campania",
                    "source": "ARPA Campania HTML",
                    "is_synthetic": False
                })

        print(f"  Found {len(stations)} stations in Campania.")
        return stations
        
    except Exception as e:
        print(f"  Failed to parse Campania HTML: {e}")
        return []

def main():
    all_stations = []
    
    # 1. Try Fetching Real Data (Lombardia as pilot)
    # lombardia_stations = fetch_lombardia_stations() # Fails in automation
    # all_stations.extend(lombardia_stations)
    
    # 1b. Add Piemonte Baseline (Manual from Map)
    piemonte = get_piemonte_baseline()
    all_stations.extend(piemonte)

    # 1c. Add Veneto Data (Real JSON)
    veneto = get_veneto_data()
    all_stations.extend(veneto)
    
    # 1d. Add Emilia-Romagna Data (Real CSV)
    emilia = get_emilia_romagna_data()
    all_stations.extend(emilia)

    # 1e. Add Lombardia Data (Local CSV)
    lombardia = get_lombardia_data()
    all_stations.extend(lombardia)

    # 1f. Add Lazio Data (Local JSON)
    lazio = get_lazio_data()
    all_stations.extend(lazio)
    
    # 1g. Add Campania Data (Local HTML)
    campania = get_campania_data()
    all_stations.extend(campania)

    # 2. Add Synthetic Data for National Coverage
    # Check if we have enough
    if len(all_stations) < 50:
        print("Dataset too small, adding synthetic national web...")
        existing_count = len(all_stations)
        synthetic = generate_synthetic_stations(existing_count)
        all_stations.extend(synthetic)
        
    # 3. Save to JSON
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_stations, f, indent=2, ensure_ascii=False)
        
    print(f"Total stations saved: {len(all_stations)}")
    print(f"Output: {output_path.absolute()}")

if __name__ == "__main__":
    main()
