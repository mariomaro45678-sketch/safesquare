import requests
import csv
import io

url = "https://geo.agcom.it/arcgis/sharing/rest/content/items/6c0b48a9a06c44059656b987d85acb63/data"
try:
    print("Downloading...")
    response = requests.get(url, stream=True, verify=False)
    content = ""
    for chunk in response.iter_content(chunk_size=1024):
        content += chunk.decode('utf-8', errors='ignore')
        if len(content) > 5000: break
    
    print("Parsing...")
    reader = csv.DictReader(io.StringIO(content), delimiter=';')
    print(f"Fields: {reader.fieldnames}")
    for row in reader:
        print(f"First Row: {row}")
        print(f"PRO_COM value: '{row.get('pro_com')}'")
        break
except Exception as e:
    print(f"Error: {e}")
