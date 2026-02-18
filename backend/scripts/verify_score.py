from app.core.database import SessionLocal
from app.services.scoring_engine import ScoringEngine
from app.models.geography import Municipality

try:
    db = SessionLocal()
    engine = ScoringEngine()
    rome = db.query(Municipality).filter(Municipality.name=='Roma').first()
    
    if rome:
        res = engine.calculate_score(db, municipality_id=rome.id)
        dc_score = res['component_scores'].get('digital_connectivity', 'N/A')
        ry_score = res['component_scores'].get('rental_yield', 'N/A')
        print(f"Digital Connectivity Score: {dc_score}")
        print(f"Rental Yield Score: {ry_score}")
        print(f"Overall Score: {res['overall_score']}")
        print(f"Metrics - Towers: {rome.mobile_tower_count}, FTTH: {rome.broadband_ftth_coverage}")
    else:
        print("Roma not found")
except Exception as e:
    print(f"Error: {e}")
