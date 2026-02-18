import random
from datetime import date, timedelta
import logging
from app.core.database import SessionLocal
from app.models.listing import RealEstateListing
from app.models.geography import Municipality, OMIZone
from app.models.property import PropertyPrice
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simulate_market_pulse(city_names=["Roma", "Milano", "Napoli", "Torino", "Bologna", "Firenze"]):
    db = SessionLocal()
    try:
        for city_name in city_names:
            muni = db.query(Municipality).filter(func.lower(Municipality.name) == city_name.lower()).first()
            if not muni: continue
            
            logger.info(f"Simulating market pulse for {city_name}...")
            
            # Get latest OMI prices for this city
            zones = db.query(OMIZone).filter(OMIZone.municipality_id == muni.id).all()
            if not zones: 
                # Fallback to municipality avg
                avg_price = 2500 # Very rough default
            else:
                zone_ids = [z.id for z in zones]
                prices = db.query(func.avg(PropertyPrice.avg_price)).filter(
                    PropertyPrice.omi_zone_id.in_(zone_ids),
                    PropertyPrice.year == 2023
                ).scalar()
                avg_price = prices or 2500

            # Generate 50-100 listings per city
            count = 0
            for i in range(random.randint(50, 100)):
                is_active = random.random() > 0.3
                days_ago = random.randint(1, 90)
                posted = date.today() - timedelta(days=days_ago)
                
                size = random.randint(35, 140)
                # OMI price + jitter (-15% to +35% for listings vs state averages)
                listing_price_sqm = avg_price * random.uniform(0.85, 1.35)
                price = int(size * listing_price_sqm)
                
                source_id = f"sim_{muni.id}_{i}_{posted.strftime('%Y%m%d')}"
                
                # Check if exists
                exists = db.query(RealEstateListing).filter(RealEstateListing.source_id == source_id).first()
                if not exists:
                    listing = RealEstateListing(
                        municipality_id=muni.id,
                        source_id=source_id,
                        source_platform="market_simulator",
                        url=f"https://simulated-market.sq/{source_id}",
                        title=f"Sample Property {size}mq",
                        price=price,
                        size_sqm=size,
                        price_per_sqm=listing_price_sqm,
                        date_posted=posted,
                        date_removed=None if is_active else date.today() - timedelta(days=random.randint(0, days_ago)),
                        is_active=is_active,
                        days_on_market=random.randint(5, 120) if not is_active else days_ago,
                        views=random.randint(50, 2000)
                    )
                    db.add(listing)
                    count += 1
            
            db.commit()
            logger.info(f"Added {count} simulated listings for {city_name}.")

    finally:
        db.close()

if __name__ == "__main__":
    simulate_market_pulse()
