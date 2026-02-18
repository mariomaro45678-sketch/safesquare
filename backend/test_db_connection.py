import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute("SELECT PostGIS_Version();")
    version = cursor.fetchone()
    print("PostgreSQL connected successfully!")
    print(f"PostGIS version: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Database connection failed: {e}")
