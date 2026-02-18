
import csv
import json
import os
import glob
from pathlib import Path
from collections import defaultdict
from statistics import mean

def process_emilia_data():
    print("Processing Emilia-Romagna measurement data...")
    
    # Path to CSVs
    # Adjust this to the actual location
    input_dir = Path("C:/Users/pap/Downloads/SafeSquare/emiliaromagna/CSV Stazione_Parametro_AnnoMese")
    output_path = Path("backend/data/emilia_historical.json")
    
    if not input_dir.exists():
        print(f"Input directory {input_dir} not found.")
        return

    # Province mapping heuristic (First 2 digits of filename station code -> Province)
    # 02=PC, 03=PR, 04=RE, 05=MO, 06=BO, 07=FE, 08=RA, 09=FC, 10=RN
    province_map = {
        "02": {"name": "Piacenza", "lat": 45.05, "lon": 9.69},
        "03": {"name": "Parma", "lat": 44.80, "lon": 10.33},
        "04": {"name": "Reggio Emilia", "lat": 44.70, "lon": 10.63},
        "05": {"name": "Modena", "lat": 44.64, "lon": 10.92},
        "06": {"name": "Bologna", "lat": 44.49, "lon": 11.34},
        "07": {"name": "Ferrara", "lat": 44.83, "lon": 11.62},
        "08": {"name": "Ravenna", "lat": 44.41, "lon": 12.20},
        "09": {"name": "Forlì-Cesena", "lat": 44.22, "lon": 12.05},
        "10": {"name": "Rimini", "lat": 44.06, "lon": 12.56},
    }

    # Parameter codes (from file inspection and standard codes)
    # 5 -> PM10
    # 8 -> NO2
    # 111 -> PM2.5 (also 10 sometimes found in files? Assuming 111 is main PM2.5 based on high counts)
    # 7 -> Ozone (ignored for now?) - Let's include NO2, PM10, PM2.5
    pollutant_codes = {
        "005": "pm10",
        "008": "no2",
        "111": "pm25",
        "010": "pm25", # Sometimes used?
        "5": "pm10",
        "8": "no2"
    }

    # Station Data: StationID -> Year -> Pollutant -> [Values]
    station_aggregates = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    station_metadata = {} # ID -> {lat, lon, name}

    files = list(input_dir.glob("storico_*.csv"))
    print(f"Found {len(files)} CSV files. Processing...")

    count = 0
    for file_path in files:
        count += 1
        if count % 500 == 0:
            print(f"Processed {count} files...")

        # Parse filename: storico_YYYY_StationCode_ParamCode.csv
        # Example: storico_2019_02000003_005.csv
        try:
            parts = file_path.stem.split('_')
            if len(parts) < 4: continue
            
            year = int(parts[1])
            station_code_full = parts[2] # "02000003"
            param_code = parts[3] # "005"
            
            if param_code not in pollutant_codes:
                continue
                
            pollutant = pollutant_codes[param_code]
            
            # Heuristic for location
            prov_code = station_code_full[:2]
            
            # Normalize station ID for system
            station_id = f"EM_{station_code_full}"
            
            if station_id not in station_metadata:
                if prov_code in province_map:
                    info = province_map[prov_code]
                    station_metadata[station_id] = {
                        "name": f"Stazione {station_code_full} ({info['name']} approx)",
                        "lat": info["lat"],
                        "lon": info["lon"],
                        "province": info["name"]
                    }
                else:
                    # Fallback to Bologna centroid if unknown
                    station_metadata[station_id] = {
                        "name": f"Stazione {station_code_full} (Unknown Prov)",
                        "lat": 44.49,
                        "lon": 11.34,
                        "province": "Unknown"
                    }

            # Read Values
            # We assume the file contains valid data.
            # Format: COD_STAZ,ID_PARAM,DATA_INIZIO,DATA_FINE,VALORE,UM
            # Skip header.
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f)
                next(reader, None) # Skip header
                for row in reader:
                    if len(row) < 5: continue
                    val_str = row[4]
                    try:
                        val = float(val_str.replace(',', '.'))
                        if val < 0: continue # Skip negative/invalid?
                        station_aggregates[station_id][year][pollutant].append(val)
                    except ValueError:
                        continue

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            continue

    print("Aggregating annual values...")
    
    final_records = []
    
    for st_id, years in station_aggregates.items():
        meta = station_metadata.get(st_id)
        if not meta: continue
        
        for year, pollutants in years.items():
            record = {
                "station_id": st_id,
                "name": meta["name"],
                "latitude": meta["lat"],
                "longitude": meta["lon"],
                "region": "Emilia-Romagna",
                "province": meta["province"],
                "year": year,
                "data_source": "ARPA Emilia Open Data"
            }
            
            has_data = False
            for p, values in pollutants.items():
                if values:
                    avg_val = mean(values)
                    record[f"{p}_avg"] = round(avg_val, 2)
                    has_data = True
            
            if has_data:
                final_records.append(record)

    print(f"Generated {len(final_records)} annual records for Emilia-Romagna.")
    
    # Ensure directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_records, f, indent=2)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    process_emilia_data()
