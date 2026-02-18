
import requests
import json
import time
from pathlib import Path
from datetime import datetime

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_veneto_measurements():
    """
    Fetches real-time/latest measurements from ARPA Veneto Open Data.
    Same endpoint as stations but different processing or adjacent endpoint.
    URL: https://www2.arpa.veneto.it/bollettini/aria/stazioni/dati_grezzi/stats.json
    This contains 'val' for pollutants.
    """
    print("Fetching Veneto measurements...")
    url = "https://www2.arpa.veneto.it/bollettini/aria/stazioni/dati_grezzi/stats.json"
    output_path = Path("backend/data/veneto_historical.json")
    
    try:
        response = requests.get(url, verify=False, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Structure: list of objects.
        # { "stat": 500000106, "pm10": 25, "o3": 12, ...date... } ??
        # Let's inspect what we get.
        # Usually it's keyed by station ID.
        
        # Based on previous station fetching, each item has 'stat' (ID) and pollutant keys.
        
        processed_data = []
        
        for item in data:
            s_id = item.get("stat")
            if not s_id: continue
            
            # They use integer IDs. Map to our format V_{id}
            our_id = f"V_{s_id}"
            
            # Helper to safely Float
            def get_val(key):
                v = item.get(key)
                if v is None or v == -999: return None
                try:
                    return float(v)
                except (ValueError, TypeError):
                    return None
            
            pm10 = get_val("pm10")
            pm25 = get_val("pm2.5") # Check key name
            no2 = get_val("no2")
            o3 = get_val("o3")
            
            if pm10 is not None or pm25 is not None or no2 is not None:
                processed_data.append({
                    "station_id": our_id,
                    "year": datetime.now().year, # Current status
                    "data_source": "ARPA Veneto API (Live)",
                    "pm10_avg": pm10,
                    "pm25_avg": pm25,
                    "no2_avg": no2,
                    "o3_avg": o3
                })

        print(f"Fetched {len(processed_data)} Veneto measurement records.")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2)
            
        print(f"Saved to {output_path}")
        
    except Exception as e:
        print(f"Failed to fetch Veneto measurements: {e}")

if __name__ == "__main__":
    fetch_veneto_measurements()
