from app.core.config import settings
from sqlalchemy import create_engine, text
import json
import os

def verify_distribution():
    engine = create_engine(str(settings.DATABASE_URL))
    with engine.connect() as conn:
        # Check scores with the new 'air_quality' indicator
        query = text("""
            SELECT floor(overall_score) as score_range, COUNT(*) 
            FROM investment_scores 
            WHERE weights::jsonb ? 'air_quality'
            GROUP BY 1 
            ORDER BY 1
        """)
        results = conn.execute(query).fetchall()
        
        print("\n--- New Z-Score Distribution Audit ---")
        if not results:
            print("No new scores found yet.")
        for row in results:
            print(f"Score {row[0]}: {row[1]}")
            
        # Check Top 5 scores
        top_query = text("""
            SELECT m.name, s.overall_score 
            FROM investment_scores s 
            JOIN municipalities m ON s.municipality_id = m.id 
            WHERE s.weights::jsonb ? 'air_quality'
            ORDER BY s.overall_score DESC 
            LIMIT 5
        """)
        tops = conn.execute(top_query).fetchall()
        print("\n--- Top 5 Municipalities (New Logic) ---")
        for t in tops:
            print(f"{t[0]}: {t[1]}")

if __name__ == "__main__":
    verify_distribution()
