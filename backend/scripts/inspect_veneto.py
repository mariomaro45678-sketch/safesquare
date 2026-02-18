
import requests
import json

URLS = {
    "coords": "https://www2.arpa.veneto.it/aria-json/exported/aria/coords.json",
    "stats": "https://www2.arpa.veneto.it/aria-json/exported/aria/stats.json"
}

def inspect():
    for name, url in URLS.items():
        print(f"--- Fecthing {name} from {url} ---")
        try:
            r = requests.get(url, timeout=30, verify=False) # Disable SSL verify for testing
            print(f"Status: {r.status_code}")
            
            try:
                data = r.json()
                print(f"Type: {type(data)}")
                if isinstance(data, list):
                    print(f"Length: {len(data)}")
                    if len(data) > 0:
                        print("Sample item keys:", data[0].keys())
                        print("Sample item:", json.dumps(data[0], indent=2))
                elif isinstance(data, dict):
                    print("Keys:", list(data.keys())[:5])
                    # Print first key's value sample
                    if len(data) > 0:
                        first_key = list(data.keys())[0]
                        print(f"Sample value for key '{first_key}':", data[first_key])
            except json.JSONDecodeError:
                print("Failed to decode JSON. Raw text sample:")
                print(r.text[:500])
                
        except Exception as e:
            print(f"Error fetching {name}: {e}")

if __name__ == "__main__":
    inspect()
