import requests

url = "https://geo.agcom.it/arcgis/sharing/rest/content/items/6c0b48a9a06c44059656b987d85acb63/data"
try:
    response = requests.get(url, stream=True, verify=False)
    # Read first 5KB
    content = ""
    for chunk in response.iter_content(chunk_size=1024):
        content += chunk.decode('utf-8', errors='ignore')
        if len(content) > 5000: break
    
    import csv
    import io
    reader = csv.DictReader(io.StringIO(content), delimiter=';')
    print(f"Headers: {reader.fieldnames}")
    
    count = 0
    for row in reader:
        print(f"Row {count}: PRO_COM='{row.get('PRO_COM')}'")
        count += 1
        if count >= 5: break
except Exception as e:
    print(f"Error: {e}")
