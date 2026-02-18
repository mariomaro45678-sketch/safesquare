import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')
print(f"Connecting to: {db_url}")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = cur.fetchall()
    print("Tables found in 'public' schema:")
    for t in tables:
        print(f" - {t[0]}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
