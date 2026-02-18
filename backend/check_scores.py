import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def check_scores():
    if not DATABASE_URL:
        print("DATABASE_URL not found in environment")
        return

    try:
        # Connect to 'postgres' first to list databases
        postgres_url = DATABASE_URL.replace("/property_db", "/postgres")
        engine_root = create_engine(postgres_url)
        with engine_root.connect() as conn:
            result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
            print("Databases:")
            for row in result:
                print(f"- {row[0]}")
        
        # Check safesquare database
        safesquare_url = DATABASE_URL.replace("/property_db", "/safesquare")
        engine_ss = create_engine(safesquare_url)
        try:
            with engine_ss.connect() as conn:
                result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
                print("\nTables in safesquare:")
                tables = [row[0] for row in result]
                for t in tables:
                    print(f"- {t}")
                
                if 'investment_scores' in tables:
                    result = conn.execute(text("SELECT count(*) FROM investment_scores"))
                    print(f"\nTotal scores in safesquare.investment_scores: {result.scalar()}")
                else:
                    print("\n'investment_scores' table NOT found in safesquare DB")
        except Exception as e:
            print(f"Error checking safesquare DB: {e}")

        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Check tables in property_db
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            print("\nTables in property_db:")
            for row in result:
                print(f"- {row[0]}")

                result = conn.execute(text("SELECT count(*) FROM municipalities"))
                print(f"Total municipalities: {result.scalar()}")

                result = conn.execute(text("SELECT count(*) FROM property_prices"))
                print(f"Total property prices: {result.scalar()}")

                result = conn.execute(text("SELECT count(*) FROM investment_scores"))
                count = result.scalar()
                print(f"Total scores in investment_scores: {count}")
                
                result = conn.execute(text("SELECT id, municipality_id, overall_score, calculation_date FROM investment_scores"))
                print("\nAll scores in table:")
                for row in result:
                    print(f"- ID: {row[0]}, MunID: {row[1]}, Score: {row[2]}, Date: {row[3]}")
                
                # Check if there are any errors in the backend log itself
                print("\nChecking backend.log for errors...")
                try:
                    with open("logs/backend.log", "r") as f:
                        lines = f.readlines()[-20:]
                        for line in lines:
                            if "ERROR" in line or "Scoring" in line:
                                print(line.strip())
                except:
                    print("Could not read logs/backend.log")
                
    except Exception as e:
        print(f"Error checking scores: {e}")

if __name__ == "__main__":
    check_scores()
