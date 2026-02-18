
import json
import os
from pathlib import Path

def process_lazio_data():
    print("Processing Lazio measurement data...")
    input_path = Path("backend/data/raw/lazio_2023.json")
    output_path = Path("backend/data/lazio_historical.json")
    
    if not input_path.exists():
        print(f"Input file {input_path} not found.")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        fields = data.get("fields", [])
        records = data.get("records", [])
        
        # Map field names to indices
        idx_map = {f["id"]: i for i, f in enumerate(fields)}
        
        # Helper to safely get float
        def get_val(row, col_name):
            if col_name not in idx_map: return None
            val = row[idx_map[col_name]]
            if val is None or val == "": return None
            if isinstance(val, str):
                val = val.replace(',', '.')
            try:
                return float(val)
            except ValueError:
                return None

        # Helper to get string
        def get_str(row, col_name):
            if col_name not in idx_map: return None
            return row[idx_map[col_name]]

        final_records = []
        
        # Identify relevant columns (names might differ slightly, use keywords if needed)
        # Based on file inspection:
        # "cod ISTAT"
        # "nome"
        # "PM10 media annua  (µg/m3) MED"
        # "PM2.5 media annua (µg/m3) MED"
        # "NO2 media annua  (µg/m3) MED"
        
        keys = idx_map.keys()
        # Fuzzy match keys just in case
        k_istat = next((k for k in keys if "cod istat" in k.lower()), None)
        k_nome = next((k for k in keys if "nome" in k.lower()), None)
        k_pm10 = next((k for k in keys if "pm10" in k.lower() and "media" in k.lower() and "med" in k), None)
        k_pm25 = next((k for k in keys if "pm2.5" in k.lower() and "media" in k.lower() and "med" in k), None)
        k_no2 = next((k for k in keys if "no2" in k.lower() and "media" in k.lower() and "med" in k), None)
        
        print(f"Mapped Keys:\nISTAT: {k_istat}\nNome: {k_nome}\nPM10: {k_pm10}\nPM2.5: {k_pm25}\nNO2: {k_no2}")

        if not k_istat:
            print("Critical error: Could not find ISTAT code column.")
            return

        for row in records:
            istat_raw = row[idx_map[k_istat]]
            # Format ISTAT: The file has 12057001 (Region 12, Prov 057, Com 001). 
            # We standardize to string.
            istat_str = str(istat_raw)
            
            nome = get_str(row, k_nome)
            
            pm10 = get_val(row, k_pm10) if k_pm10 else None
            pm25 = get_val(row, k_pm25) if k_pm25 else None
            no2 = get_val(row, k_no2) if k_no2 else None
            
            # Skip if no pollution data at all? 
            # No, even valid 0s or missing data might be important, but usually we want at least one value.
            if pm10 is None and pm25 is None and no2 is None:
                continue

            record = {
                "station_id": f"LAZ_MUN_{istat_str}", # Virtual station ID
                "name": f"{nome} (Municipality Aggregate)",
                "istat_code": istat_str,
                "year": 2023,
                "data_source": "ARPA Lazio Open Data 2023"
            }
            
            if pm10 is not None: record["pm10_avg"] = pm10
            if pm25 is not None: record["pm25_avg"] = pm25
            if no2 is not None: record["no2_avg"] = no2
            
            final_records.append(record)

        print(f"Generated {len(final_records)} records for Lazio.")
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_records, f, indent=2)
        print(f"Saved to {output_path}")

    except Exception as e:
        print(f"Error processing Lazio data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    process_lazio_data()
