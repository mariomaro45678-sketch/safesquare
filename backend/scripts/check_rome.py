from sqlalchemy import text
from app.core.database import SessionLocal
db = SessionLocal()

# Check Rome Data
res = db.execute(text("SELECT area_sqkm, ST_AsText(centroid) FROM municipalities WHERE name='Roma'")).fetchone()
print(f"Rome Data: {res}")

# Check Intersection
if res:
    # Hardcoded 10km check
    sql = "SELECT COUNT(*) FROM service_nodes s, municipalities m WHERE m.name='Roma' AND ST_DWithin(CAST(m.centroid AS geography), CAST(s.geometry AS geography), 10000)"
    try:
        count = db.execute(text(sql)).scalar()
        print(f"Hardcoded 10km check: {count}")
    except Exception as e:
        print(f"Error: {e}")

    # Check Total Service Nodes
    total = db.execute(text("SELECT COUNT(*) FROM service_nodes")).scalar()
    print(f"Total Service Nodes in DB: {total}")
