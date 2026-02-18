import sys
import os
from app.core.database import SessionLocal
from app.services.scoring_engine import ScoringEngine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_milano():
    db = SessionLocal()
    try:
        engine = ScoringEngine()
        # Milano ID is 1685 based on previous probe
        milano_id = 1685
        
        logger.info(f"Testing Investment Score for Milano (ID: {milano_id})...")
        
        # Calculate score
        result = engine.calculate_score(db, municipality_id=milano_id)
        
        print("\n" + "="*50)
        print(f"INVESTMENT ANALYSIS: {result['location']}")
        print("="*50)
        print(f"OVERALL SCORE: {result['overall_score']}/10")
        print("-" * 50)
        print("COMPONENT SCORES:")
        for comp, score in result['component_scores'].items():
            print(f"  - {comp.replace('_', ' ').title()}: {score}/10")
        print("="*50 + "\n")
        
        # Test saving
        saved = engine.save_score(db, result)
        logger.info(f"Score saved to DB with ID: {saved.id}")
        
    except Exception as e:
        logger.error(f"Scoring test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_milano()
