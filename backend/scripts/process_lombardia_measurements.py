
import csv
import json
from pathlib import Path
from collections import defaultdict
from statistics import mean

def process_data():
    print("Starting Lombardia Data Optimization...")
    
    # Files
    station_csv = Path("Stazioni_qualità_dell'aria_NRT_20260130.csv")
    data_csv = Path("Dati_sensori_aria_20260130.csv")
    output_json = Path("backend/data/lombardia_historical.json")
    
    # 1. Build Sensor -> Station Map
    # We need: SensorID -> {StationID, PollutantType}
    sensor_map = {}
    
    # Pollutant normalization map
    pollutant_map = {
        "Biossido di Azoto": "no2",
        "PM10 (SM2005)": "pm10",
        "Particelle sospese PM2.5": "pm25",
        "Ozono": "o3",
        "Biossido di Zolfo": "so2",
        "Monossido di Carbonio": "co"
    }
    
    print(f"Loading metadata from {station_csv}...")
    try:
        with open(station_csv, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                s_id = row.get('idSensore')
                st_id = row.get('IdStazione')
                p_type_raw = row.get('NomeTipoSensore')
                
                # Normalize pollutant name
                p_key = None
                for k, v in pollutant_map.items():
                    if k in p_type_raw:
                        p_key = v
                        break
                
                if s_id and st_id and p_key:
                    sensor_map[s_id] = {
                        "station_id": f"L_{st_id}", # Consistent with fetch_arpa_stations.py
                        "pollutant": p_key
                    }
    except Exception as e:
        print(f"Error reading station metadata: {e}")
        return

    print(f"Mapped {len(sensor_map)} relevant sensors.")

    # 2. Process Massive CSV
    # Structure: IdSensore,Data,Valore,Stato,idOperatore
    # We want: StationID -> Year -> Pollutant -> [Values]
    
    # Use a nested dict: station_data[station_id][year][pollutant] = [list of values]
    # To save memory, we can store running sums and counts: [sum, count]
    station_aggregates = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0.0, 0])))
    
    print(f"Processing measurements from {data_csv} (this may take a moment)...")
    
    row_count = 0
    try:
        with open(data_csv, 'r', encoding='utf-8', errors='replace') as f:
            # Skip header if present (it likely is based on view_file earlier)
            # The previous view showed header on line 1: "IdSensore","Data","Valore","Stato","idOperatore"
            reader = csv.reader(f)
            header = next(reader, None)
            
            for row in reader:
                row_count += 1
                if row_count % 1000000 == 0:
                    print(f"  Processed {row_count} rows...")
                    
                if len(row) < 3: continue
                
                s_id = row[0]
                date_str = row[1] # "22/05/2025 01:00:00 AM"
                val_str = row[2] # "20,3"
                status = row[3] # "VA" (Valid)
                
                # Filter for Valid data only? Or all? Usually "VA"
                if status != "VA":
                    continue
                    
                if s_id in sensor_map:
                    # Parse Value
                    try:
                        val = float(val_str.replace(',', '.'))
                        if val == -9999: continue # Common nodata value
                    except ValueError:
                        continue
                        
                    # Extract Year
                    # Format: dd/mm/yyyy ...
                    # Quick parse: split by space, then split date by /
                    try:
                        date_part = date_str.split(' ')[0]
                        parts = date_part.split('/')
                        year = int(parts[2])
                    except (IndexError, ValueError):
                        continue
                        
                    info = sensor_map[s_id]
                    st_id = info['station_id']
                    pollutant = info['pollutant']
                    
                    # Update aggregate
                    agg = station_aggregates[st_id][year][pollutant]
                    agg[0] += val
                    agg[1] += 1

    except Exception as e:
        print(f"Error reading measurement data: {e}")
        return

    print(f"Finished processing {row_count} rows.")
    
    # 3. Final Calculation and Save
    print("Calculating averages...")
    final_output = []
    
    for st_id, years in station_aggregates.items():
        for year, pollutants in years.items():
            record = {
                "station_id": st_id,
                "year": year,
                "data_source": "ARPA Lombardia (CSV Aggregated)"
            }
            has_data = False
            for p, (total, count) in pollutants.items():
                if count > 0:
                    avg = total / count
                    record[f"{p}_avg"] = round(avg, 2)
                    has_data = True
            
            if has_data:
                final_output.append(record)
                
    print(f"Generated {len(final_output)} annual station records.")
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2)
        
    print(f"Saved to {output_json}")

if __name__ == "__main__":
    process_data()
