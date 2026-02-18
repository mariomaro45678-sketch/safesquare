
import os
from sqlalchemy import create_engine, text
from app.core.config import settings

def check_distribution():
    engine = create_engine(str(settings.DATABASE_URL))
    with engine.connect() as conn:
        query = text("""
            SELECT 
                floor(overall_score) as bucket, 
                COUNT(*) as count
            FROM investment_scores 
            WHERE omi_zone_id IS NULL 
            GROUP BY 1 
            ORDER BY 1 DESC
        """)
        results = conn.execute(query).fetchall()
        
        print("Score Distribution (Municipalities):")
        print("-" * 30)
        total = 0
        for bucket, count in results:
            total += count
            
        for bucket, count in results:
            percentage = (count / total) * 100 if total > 0 else 0
            label = "RED (Low)"
            if bucket >= 7: label = "GREEN (High)"
            elif bucket >= 5: label = "YELLOW (Mod)"
            
            print(f"Score {bucket}.x: {count:5} ({percentage:5.1f}%) - {label}")
        print("-" * 30)
        print(f"Total: {total}")

if __name__ == "__main__":
    check_distribution()
