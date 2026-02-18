import os
import sys
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.geography import Municipality, OMIZone
from app.models.property import PropertyPrice
from app.models.demographics import Demographics

db = SessionLocal()

# 1. Check PIDs to see if geocoding is running
pids = [p for p in os.listdir('/proc') if p.isdigit()]
print("--- Background Processes ---")
found_python = False
for p in pids:
    if os.path.exists(f"/proc/{p}/cmdline"):
        try:
            cmd = open(f"/proc/{p}/cmdline").read().replace('\0', ' ')
            if "python" in cmd:
                print(f"PID {p}: {cmd}")
                found_python = True
        except (IOError, PermissionError):
            pass
if not found_python:
    print("No python processes found via /proc check.")

# 2. Check Municipality with Pop 43855 
# (Dot as separator usually means thousands in Italy)
m43 = db.query(Municipality).filter(Municipality.population == 43855).first()
if not m43:
    # Try demographics table
    d43 = db.query(Demographics).filter(Demographics.total_population == 43855).first()
    if d43:
        m43 = db.query(Municipality).get(d43.municipality_id)

print(f"\n--- Population Search (43855) ---")
if m43:
    print(f"Match Found: {m43.name} (ID: {m43.id}, Code: {m43.code})")
else:
    print("No exact match for population 43855")

# 3. Check Rome (5190)
m_rome = db.query(Municipality).get(5190)
print(f"\n--- Rome Status (ID: 5190) ---")
if m_rome:
    print(f"Name: {m_rome.name}")
    print(f"Population (Muni Table): {m_rome.population}")
    d_rome = db.query(Demographics).filter(Demographics.municipality_id == 5190).first()
    print(f"Population (Demo Table): {d_rome.total_population if d_rome else 'None'}")
    
    # Check Price Data
    zone_count = db.query(OMIZone).filter(OMIZone.municipality_id == 5190).count()
    prices = db.query(PropertyPrice).join(OMIZone).filter(OMIZone.municipality_id == 5190).all()
    print(f"OMI Zones: {zone_count}")
    print(f"Price Records: {len(prices)}")
    if prices:
        avg_prices = [p.avg_price for p in prices[:10]]
        print(f"Sample Avg Prices (avg_price): {avg_prices}")
        print(f"Latest Records: {[(p.year, p.semester, p.avg_price) for p in prices[:5]]}")
    else:
        print("No price records found for Rome zones.")
else:
    print("Rome ID 5190 not found!")

# 4. Geocoding Progress
geocoded_count = db.query(Municipality).filter(Municipality.centroid != None).count()
total_count = db.query(Municipality).count()
print(f"\n--- Geocoding Progress ---")
print(f"Geocoded: {geocoded_count} / {total_count}")

db.close()
