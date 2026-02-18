from app.core.database import SessionLocal
from app.models.score import InvestmentScore
from app.models.geography import Municipality

def inspect_scores():
    db = SessionLocal()
    try:
        scores = db.query(InvestmentScore).all()
        print(f"Total scores: {len(scores)}")
        for s in scores:
            muni = db.query(Municipality).get(s.municipality_id)
            print(f"Muni: {muni.name if muni else 'Unknown'}, Score: {s.overall_score}, Date: {s.calculation_date}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_scores()
