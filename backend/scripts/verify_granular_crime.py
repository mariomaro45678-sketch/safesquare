from app.core.database import SessionLocal
from app.models.geography import Municipality, OMIZone
from app.services.scoring_engine import ScoringEngine
from sqlalchemy import func

def verify_granular():
    db = SessionLocal()
    engine = ScoringEngine()
    
    # Get Rome
    rome = db.query(Municipality).filter(func.lower(Municipality.name) == 'roma').first()
    if not rome:
        print("Rome not found")
        return

    print("--- Verifying Granular Crime Scoring (Rome) ---")
    
    # We need to simulate OMI Zones because we might not have them all populated with names
    # matching our seed data perfectly.
    # So we will temporarily create mock zone objects in memory (or use existing if names match)
    
    test_zones = [
        "OMI Zone Z1",      # Should hit our new direct mapping
        "Parioli",          # Should be Safe (Score ~7.0 [Risk 30] -> 10-3 = 7)
        "Tor Bella Monaca", # Should be Risky (Score ~1.5 [Risk 85] -> 10-8.5 = 1.5)
        "Centro Storico",   # Should be Mid (Score ~3.5 [Risk 65] -> 10-6.5 = 3.5)
        "Unknown Zone"      # Should Fallback to ~5-7
    ]
    
    # We can't easily mock db objects for the engine query, so we'll look for actual zones
    # OR we can just unit-test the logic if we can't find real zones.
    # Let's try to find real zones first.
    
    for z_name in test_zones:
        # Try to find a zone containing this name
        zone = db.query(OMIZone).filter(
            OMIZone.municipality_id == rome.id, 
            OMIZone.zone_name.ilike(f"%{z_name}%")
        ).first()
        
        if zone:
            score = engine._score_crime_safety(db, rome.id, zone.id)
            print(f"Zone '{z_name}' (ID: {zone.id}, Name: {zone.zone_name}) -> Crime Score: {score}")
        else:
            print(f"Zone '{z_name}' NOT FOUND in DB. Cannot verify end-to-end.")

if __name__ == "__main__":
    verify_granular()
