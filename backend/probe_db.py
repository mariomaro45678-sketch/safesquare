import psycopg2
import sys

def probe():
    print("Probing localhost:5432...")
    try:
        # Try common passwords if any, or no password
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            host="localhost",
            port=5432,
            connect_timeout=3
        )
        print("✅ Connected to postgres database as postgres user!")
        conn.close()
        return
    except Exception as e:
        print(f"❌ Failed to connect as postgres: {e}")

    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="property_user",
            password="change_me_in_production",
            host="localhost",
            port=5432,
            connect_timeout=3
        )
        print("✅ Connected to postgres database as property_user!")
        conn.close()
    except Exception as e:
        print(f"❌ Failed to connect as property_user: {e}")

if __name__ == "__main__":
    probe()
