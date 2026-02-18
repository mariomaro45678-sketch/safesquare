import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"✅ Connection successful!")
    print(f"✅ PostgreSQL version: {db_version[0]}")
    
    # Check if PostGIS is installed (it shouldn't be, but good to verify again)
    cursor.execute("SELECT name FROM pg_available_extensions WHERE name = 'postgis';")
    postgis_available = cursor.fetchone()
    if postgis_available:
        print(f"✅ PostGIS is available!")
    else:
        print(f"⚠️ PostGIS is NOT available.")
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
