
import requests
import sys

def test_endpoints():
    base_url = "http://localhost:8000/api/v1"
    municipality_id = 1 # Assuming Milano or a valid ID exists
    
    # In a real scenario, we'd find a valid ID first. 
    # Let's find Milano
    try:
        muni_resp = requests.post(f"{base_url}/locations/search", json={"query": "Milano"})
        if muni_resp.status_code != 200 or not muni_resp.json().get('found'):
            print(f"FAILED: Could not find Milano. Status: {muni_resp.status_code}")
            return
        
        target_muni = muni_resp.json()['municipality']
        muni_id = target_muni['id']
        name = target_muni['name']
        print(f"Testing with municipality: {name} (ID: {muni_id})")
        
        # 1. Test Scores
        score_resp = requests.get(f"{base_url}/scores/municipality/{muni_id}")
        score_data = score_resp.json()
        if "confidence" in score_data:
            print(f"SUCCESS: Score confidence present: {score_data['confidence']}")
        else:
            print("FAILED: Score confidence missing")
            
        # 2. Test Demographics
        demo_resp = requests.get(f"{base_url}/demographics/municipality/{muni_id}")
        demo_data = demo_resp.json()
        print(f"DEBUG: Demographics Response: {demo_data}")
        if "total_population" in demo_data:
            print(f"SUCCESS: Demographics total_population present: {demo_data['total_population']}")
        else:
            print("FAILED: Demographics total_population missing")
            
        # 3. Test Properties
        prop_resp = requests.get(f"{base_url}/properties/statistics/municipality/{muni_id}")
        prop_data = prop_resp.json()
        if "avg_price_per_sqm" in prop_data:
            print(f"SUCCESS: Properties avg_price_per_sqm present: {prop_data['avg_price_per_sqm']}")
        else:
            print("FAILED: Properties avg_price_per_sqm missing")
            
        # 4. Test Locations (Coordinates)
        if "coordinates" in score_data: # MunicipalityResponse is often nested or separate
             print("CHECK: Checking coordinates in list response...")
             if muni_resp.json()[0].get('coordinates'):
                 print(f"SUCCESS: Coordinates found for {name}")
             else:
                 print(f"NOTE: Coordinates missing for {name} (expected if geocoding pending)")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_endpoints()
