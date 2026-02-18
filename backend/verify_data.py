"""
Database count verification script
"""
from app.core.database import SessionLocal
from app.models.demographics import Demographics, CrimeStatistics
from app.models.risk import SeismicRisk, FloodRisk, LandslideRisk, ClimateProjection
from app.models.geography import Municipality
from app.models.property import PropertyPrice

def check_counts():
    db = SessionLocal()
    try:
        counts = {
            "Municipalities": db.query(Municipality).count(),
            "Demographics": db.query(Demographics).count(),
            "Crime Statistics": db.query(CrimeStatistics).count(),
            "Climate Projections": db.query(ClimateProjection).count(),
            "Seismic Risks": db.query(SeismicRisk).count(),
            "Flood Risks": db.query(FloodRisk).count(),
            "Landslide Risks": db.query(LandslideRisk).count(),
            "Property Prices": db.query(PropertyPrice).count(),
        }
        
        print("=" * 50)
        print("DATABASE STATUS VERIFICATION")
        print("=" * 50)
        for name, count in counts.items():
            print(f"{name:.<30} {count:>6,}")
        print("=" * 50)
        
        return counts
    finally:
        db.close()

if __name__ == "__main__":
    check_counts()
