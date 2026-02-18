
import requests
import json
# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def probe():
    url = "https://www2.arpa.veneto.it/aria-json/exported/aria/stats.json"
    try:
        r = requests.get(url, verify=False, timeout=10)
        data = r.json()
        
        print("Keys in root:", data.keys())
        if 'stazioni' in data:
            print("First station sample:", json.dumps(data['stazioni'][0], indent=2))
            
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    probe()
