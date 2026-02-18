
import json
from pathlib import Path
from collections import defaultdict

def process_veneto_data():
    print("Processing Veneto measurement data...")
    input_path = Path("venetodata.json")
    output_path = Path("backend/data/veneto_historical.json")
    
    if not input_path.exists():
        print("Input file venetodata.json not found.")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        stations_data = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'sum': 0.0}))
        
        # Structure: root -> stazioni (list) -> item -> misurazioni (list) -> item -> pollutant_key (list) -> item -> {data, mis}
        
        station_list = data.get("stazioni", [])
        print(f"Found {len(station_list)} stations in source file.")
        
        for st in station_list:
            raw_id = st.get("codseqst")
            if not raw_id: continue
            
            # Ensure ID matches our station fetching logic (V_ prefix)
            station_id = f"V_{raw_id}"
            
            measurements = st.get("misurazioni", [])
            for m_block in measurements:
                # keys in m_block could be "pm10", "ozono", etc.
                for poll_key, readings in m_block.items():
                    # Map to our standard keys
                    std_key = None
                    if "pm10" in poll_key.lower(): std_key = "pm10_avg"
                    elif "pm2.5" in poll_key.lower(): std_key = "pm25_avg"
                    elif "no2" in poll_key.lower(): std_key = "no2_avg"
                    elif "ozono" in poll_key.lower(): std_key = "o3_avg"
                    
                    if not std_key: continue
                    
                    for reading in readings:
                        val_str = reading.get("mis")
                        date_str = reading.get("data") # "2026-01-23 21:25:32"
                        
                        if not val_str or val_str == "": continue
                        
                        try:
                            val = float(val_str)
                            # Simple annual aggregation (assuming mostly recent data)
                            # If we want specific year, we could parse date_str.
                            # For now, let's just aggregate everything as "latest/historical"
                            
                            stations_data[station_id][std_key]['sum'] += val
                            stations_data[station_id][std_key]['count'] += 1
                        except ValueError:
                            continue

        # Calculate averages
        final_records = []
        for s_id, polls in stations_data.items():
            record = {
                "station_id": s_id,
                "year": 2025, # Valid based on file dates seen (Jan 2026 implies full 2025 coverage available or partial 2026)
                "data_source": "ARPA Veneto JSON (Aggregated)"
            }
            has_data = False
            for p_key, stats in polls.items():
                if stats['count'] > 0:
                    record[p_key] = round(stats['sum'] / stats['count'], 2)
                    has_data = True
            
            if has_data:
                final_records.append(record)

        print(f"Generated {len(final_records)} aggregated station records.")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_records, f, indent=2)
        print(f"Saved to {output_path}")

    except Exception as e:
        print(f"Error processing Veneto data: {e}")

if __name__ == "__main__":
    process_veneto_data()
