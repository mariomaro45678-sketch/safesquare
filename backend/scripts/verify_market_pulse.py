from app.core.database import SessionLocal
from app.models.geography import Municipality
from app.services.market_pulse import MarketPulseService
from sqlalchemy import func

def verify_pulse():
    db = SessionLocal()
    
    cities = ["Roma", "Milano", "Napoli"] # Napoli has no data, should be 0
    
    print("-" * 80)
    print(f"{'CITY':<10} | {'ACTIVE':<6} | {'SOLD(90d)':<10} | {'DOM(Act)':<8} | {'DOM(Sld)':<8} | {'ABSORB(Mo)':<10}")
    print("-" * 80)
    
    for city_name in cities:
        mun = db.query(Municipality).filter(func.lower(Municipality.name) == city_name.lower()).first()
        if mun:
            metrics = MarketPulseService.get_metrics(db, mun.id)
            print(f"{city_name:<10} | {metrics['active_listings']:<6} | {metrics['sold_last_90d']:<10} | "
                  f"{metrics['avg_dom_active']:<8} | {metrics['avg_dom_sold']:<8} | {metrics['absorption_months']:<10}")
        else:
            print(f"{city_name:<10} | NOT FOUND")

if __name__ == "__main__":
    verify_pulse()
