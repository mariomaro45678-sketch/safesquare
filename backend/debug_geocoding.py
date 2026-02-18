from app.core.database import SessionLocal
from app.models.geography import Municipality, OMIZone
from app.services.geocoding import GeocodingService

db = SessionLocal()
try:
    count = db.query(Municipality).count()
    print(f"Total municipalities: {count}")
    
    m = db.query(Municipality).filter(Municipality.name == 'Milano').first()
    if m:
        print(f"Milano found (ID: {m.id}, Code: {m.code})")
        if m.geometry:
            print("Milano geometry exists")
        else:
            print("Milano geometry is MISSING")
    else:
        print("Milano NOT FOUND in database")
        # Try case insensitive or partial
        m2 = db.query(Municipality).filter(Municipality.name.ilike('%Milano%')).first()
        if m2:
            print(f"Found partial match: {m2.name} (Code: {m2.code})")

    # Debug geocoding
    geocoder = GeocodingService()
    print("\nTesting geocoding for 'Milano'...")
    res = geocoder.geocode_address("Milano")
    if res:
        print(f"Geocoded Milano: {res['latitude']}, {res['longitude']}")
        m_spatial = geocoder.find_municipality_by_coordinates(db, res['latitude'], res['longitude'])
        if m_spatial:
            print(f"Spatially found municipality: {m_spatial.name}")
        else:
            print("Spatial resolution failed to find municipality")
    else:
        print("Geocoding API failed")

finally:
    db.close()
