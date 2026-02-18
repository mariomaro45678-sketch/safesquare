from app.core.database import SessionLocal
from app.models.listing import RealEstateListing
from app.models.geography import Municipality
from sqlalchemy import func
import random
from datetime import date, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_listings():
    db = SessionLocal()
    try:
        roma = db.query(Municipality).filter(func.lower(Municipality.name) == 'roma').first()
        milano = db.query(Municipality).filter(func.lower(Municipality.name) == 'milano').first()
        
        targets = [
            (roma, 3500, 100), # City, Base Price, Count
            (milano, 4500, 100)
        ]
        
        count = 0
        for city, base_price, limit in targets:
            if not city: continue
            
            logger.info(f"Generating listings for {city.name}...")
            
            for i in range(limit):
                # Randomize
                is_active = random.random() > 0.3 # 70% active
                days_ago = random.randint(1, 180)
                posted = date.today() - timedelta(days=days_ago)
                
                removed = None
                if not is_active:
                    # Sold/Removed random days after posting
                    # Ensure range is valid
                    max_dur = max(1, days_ago)
                    min_dur = 1
                    duration = random.randint(min_dur, max_dur)
                    removed = posted + timedelta(days=duration)
                    dom = duration
                else:
                    dom = days_ago
                    
                size = random.randint(40, 150)
                # Price variation
                price_sqm = base_price * random.uniform(0.8, 1.4)
                price = int(size * price_sqm)
                
                lid = f"mock_{city.name[:3]}_{i}_{random.randint(1000,9999)}"
                
                # Check exist
                exists = db.query(RealEstateListing).filter(RealEstateListing.source_id == lid).first()
                if not exists:
                    listing = RealEstateListing(
                        municipality_id=city.id,
                        source_id=lid,
                        source_platform="mock_scraper",
                        url=f"http://mock.com/{lid}",
                        title=f"Appartamento {size}mq centro",
                        price=price,
                        size_sqm=size,
                        price_per_sqm=price_sqm,
                        date_posted=posted,
                        date_removed=removed,
                        is_active=is_active,
                        days_on_market=dom,
                        views=random.randint(10, 500)
                    )
                    db.add(listing)
                    count += 1
        
        db.commit()
        logger.info(f"Generated {count} listings.")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_listings()
