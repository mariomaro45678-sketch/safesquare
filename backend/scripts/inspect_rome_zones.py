from app.core.database import SessionLocal
from app.models.geography import Municipality, OMIZone
from sqlalchemy import func

def inspect_zones():
    db = SessionLocal()
    rome = db.query(Municipality).filter(func.lower(Municipality.name) == 'roma').first()
    if rome:
        zones = db.query(OMIZone).filter(OMIZone.municipality_id == rome.id).limit(20).all()
        for z in zones:
            print(f"ID: {z.id} | Name: {z.zone_name}")

if __name__ == "__main__":
    inspect_zones()
