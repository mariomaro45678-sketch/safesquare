from app.core.database import SessionLocal
from app.models.geography import Municipality
from sqlalchemy import func

def check_geocoding_status():
    db = SessionLocal()
    try:
        total = db.query(Municipality).count()
        missing = db.query(Municipality).filter(Municipality.centroid == None).count()
        print(f"Total Municipalities: {total}")
        print(f"Municipalities without centroids: {missing}")
        print(f"Geocoding Progress: {((total - missing) / total * 100):.2f}%")
    finally:
        db.close()

if __name__ == "__main__":
    check_geocoding_status()
