
import pandas as pd
import json
import random
import os

def create_station_data():
    # Load stations
    with open("backend/data/arpa_stations.json", "r", encoding="utf-8") as f:
        stations = json.load(f)
        
    print(f"Generating pollution data for {len(stations)} stations...")
    
    data = []
    for s in stations:
        # Simulate pollution based on Region (Po Valley vs South)
        region = s.get('region', '')
        is_po_valley = region in ['Lombardia', 'Veneto', 'Piemonte', 'Emilia-Romagna']
        
        base_pm25 = 20 if is_po_valley else 10
        base_no2 = 30 if is_po_valley else 15
        
        # Random Variation
        pm25 = base_pm25 + random.uniform(-5, 10)
        pm10 = pm25 * 1.5 + random.uniform(0, 5)
        no2 = base_no2 + random.uniform(-5, 15)
        
        data.append({
            "Station_ID": s['station_id'],
            "Result_Date": "2023-01-01",
            "PM2.5": round(pm25, 2),
            "PM10": round(pm10, 2),
            "NO2": round(no2, 2),
            "Year": 2023
        })
        
    df = pd.DataFrame(data)
    
    output_path = "backend/data/raw/air_quality_station_data.xlsx"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)
    
    print(f"Station data saved to {output_path}")

if __name__ == "__main__":
    create_station_data()
