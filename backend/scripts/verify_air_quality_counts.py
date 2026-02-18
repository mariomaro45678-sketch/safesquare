
from sqlalchemy import create_engine, text
from app.core.config import settings

def verify_ingestion():
    engine = create_engine(str(settings.DATABASE_URL))
    with engine.connect() as conn:
        result = conn.execute(text("SELECT data_source, COUNT(*) FROM air_quality GROUP BY data_source")).fetchall()
        print("\n--- Air Quality Data Summary ---")
        for row in result:
            print(f"{row[0]}: {row[1]} records")
        print("--------------------------------\n")

if __name__ == "__main__":
    verify_ingestion()
