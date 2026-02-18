from app.core.database import SessionLocal
from app.models.geography import Municipality
from sqlalchemy import func

db = SessionLocal()

mobile_count = db.query(func.count(Municipality.id)).filter(Municipality.mobile_tower_count > 0).scalar()
broadband_count = db.query(func.count(Municipality.id)).filter(Municipality.broadband_ftth_coverage > 0).scalar()

print(f"Municipalities with Mobile Towers: {mobile_count}")
print(f"Municipalities with Broadband > 0: {broadband_count}")

# Check Rome
rome = db.query(Municipality).filter(Municipality.name == 'Roma').first()
if rome:
    print(f"Roma: Towers={rome.mobile_tower_count}, FTTH={rome.broadband_ftth_coverage}%")
else:
    print("Roma not found")
