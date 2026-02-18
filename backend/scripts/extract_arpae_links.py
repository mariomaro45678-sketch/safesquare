
import requests
import re

URL = "https://dati.arpae.it/dataset/qualita-dell-aria-rete-di-monitoraggio"

def get_links():
    print(f"Fetching {URL}...")
    try:
        r = requests.get(URL, verify=False, timeout=15)
        print(f"Status: {r.status_code}")
        
        # Regex to find links to resources
        # Look for href="..." containing "resource" or "dump"
        links = re.findall(r'href=[\'"]?([^\'" >]+)', r.text)
        
        found_resources = []
        for link in links:
            if "resource" in link or "dump" in link or "csv" in link.lower():
                if link not in found_resources:
                    found_resources.append(link)
                    
        print(f"Found {len(found_resources)} potential resource links:")
        for l in found_resources:
            print(f" - {l}")
            
        # Also check specifically for "Anagrafe" in the text context if possible (simple grep here)
        if "Anagrafe" in r.text:
            print("\n'Anagrafe' term found in page text!")
        else:
            print("\n'Anagrafe' term NOT found in page text.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_links()
