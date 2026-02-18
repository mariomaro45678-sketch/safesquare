from app.core.database import SessionLocal
from app.models.geography import Region, Province, Municipality, OMIZone
from app.models.demographics import Demographics
from app.models.risk import SeismicRisk, FloodRisk, LandslideRisk
from app.models.property import PropertyPrice

def check_counts():
    db = SessionLocal()
    try:
        print(f"Regions: {db.query(Region).count()}")
        print(f"Provinces: {db.query(Province).count()}")
        print(f"Municipalities: {db.query(Municipality).count()}")
        print(f"Demographics: {db.query(Demographics).count()}")
        print(f"Seismic Risks: {db.query(SeismicRisk).count()}")
        print(f"Flood Risks: {db.query(FloodRisk).count()}")
        print(f"Landslide Risks: {db.query(LandslideRisk).count()}")
        print(f"OMI Zones: {db.query(OMIZone).count()}")
        print(f"Property Prices (OMI): {db.query(PropertyPrice).count()}")
    finally:
        db.close()

if __name__ == "__main__":
    check_counts()
