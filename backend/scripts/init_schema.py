
import sys
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Setup environment
load_dotenv()
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.config import settings
from app.models.base import Base
from app.models.risk import AirQuality # Import to ensure it's registered
from app.models.geography import Municipality, Region, Province # Ensure relationships work

def init_db():
    print("Initializing Database Schema...")
    db_url = str(settings.DATABASE_URL).replace("database", "localhost")
    engine = create_engine(db_url)
    
    print(f"Connected to: {db_url}")
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Schema initialization complete.")

if __name__ == "__main__":
    init_db()
