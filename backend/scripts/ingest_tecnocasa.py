import requests
from bs4 import BeautifulSoup
import re
from datetime import date
from app.core.database import SessionLocal
from app.models.listing import RealEstateListing
from app.models.geography import Municipality
from sqlalchemy import func
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def clean_price(price_str):
    if not price_str: return 0.0
    # Remove € and dots
    p = re.sub(r'[^\d]', '', price_str)
    try:
        return float(p)
    except (ValueError, TypeError):
        return 0.0

def clean_surface(surface_str):
    if not surface_str: return 0
    # Extract numbers
    s = re.search(r'\d+', surface_str)
    try:
        return int(s.group()) if s else 0
    except (ValueError, TypeError, AttributeError):
        return 0

def scrape_tecnocasa(city_name, pages=2):
    db = SessionLocal()
    try:
        # Find Municipality
        mun = db.query(Municipality).filter(func.lower(Municipality.name) == city_name.lower()).first()
        if not mun:
            logger.error(f"Municipality {city_name} not found in DB")
            return

        # Mapping for some regions (could be expanded)
        region_map = {
            "roma": "lazio/roma/roma",
            "milano": "lombardia/milano/milano",
            "napoli": "campania/napoli/napoli",
            "torino": "piemonte/torino/torino",
            "bologna": "emilia-romagna/bologna/bologna",
            "firenze": "toscana/firenze/firenze"
        }
        
        path = region_map.get(city_name.lower())
        if not path:
            logger.error(f"Region path mapping missing for {city_name}")
            return

        base_url = f"https://www.tecnocasa.it/annunci/immobili/{path}.html"
        
        total_ingested = 0
        
        for p in range(1, pages + 1):
            url = base_url if p == 1 else f"{base_url}/pag-{p}"
            logger.info(f"Fetching {url}...")
            
            try:
                response = requests.get(url, headers=HEADERS, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                cards = soup.select('.estate-card')
                
                if not cards:
                    logger.warning(f"No cards found on page {p}")
                    logger.debug(f"HTML Snippet: {response.text[:1000]}")
                    # Try fallback selector
                    cards = soup.select('article')
                    if cards:
                        logger.info(f"Found {len(cards)} 'article' tags as fallback.")
                    else:
                        # Print titles to see if we got the page
                        titles = soup.find_all(['h1', 'h2', 'h3'])
                        logger.info(f"Page titles found: {[t.get_text(strip=True) for t in titles]}")
                    
                if not cards:
                    break
                
                for card in cards:
                    try:
                        # Extract basic info
                        link_el = card.select_one('a')
                        if not link_el or not link_el.get('href'): continue
                        
                        listing_url = link_el['href']
                        source_id = listing_url.split('/')[-1].replace('.html', '')
                        
                        # Use full URL if relative
                        if listing_url.startswith('/'):
                            listing_url = "https://www.tecnocasa.it" + listing_url
                            
                        title = card.select_one('.estate-card-title').get_text(strip=True) if card.select_one('.estate-card-title') else "Appartamento"
                        price_str = card.select_one('.estate-card-current-price').get_text(strip=True) if card.select_one('.estate-card-current-price') else "0"
                        surface_str = card.select_one('.estate-card-surface').get_text(strip=True) if card.select_one('.estate-card-surface') else "0"
                        
                        price = clean_price(price_str)
                        size = clean_surface(surface_str)
                        
                        if price == 0 or size == 0: continue
                        
                        # Check exist
                        listing = db.query(RealEstateListing).filter(RealEstateListing.source_id == source_id).first()
                        if not listing:
                            listing = RealEstateListing(
                                municipality_id=mun.id,
                                source_id=source_id,
                                source_platform="tecnocasa",
                                url=listing_url,
                                title=title,
                                price=price,
                                size_sqm=size,
                                price_per_sqm=price / size if size > 0 else 0,
                                date_posted=date.today(), # We don't have the real date easily
                                is_active=True,
                                days_on_market=1 # Start with 1
                            )
                            db.add(listing)
                            total_ingested += 1
                        else:
                            # Update existing to stay active
                            listing.is_active = True
                            
                    except Exception as e:
                        logger.error(f"Error parsing card: {e}")
                
                db.commit()
                time.sleep(1) # Be polite
                
            except Exception as e:
                logger.error(f"Error fetching page {p}: {e}")
                
        logger.info(f"Ingested {total_ingested} real listings for {city_name}")

    finally:
        db.close()

if __name__ == "__main__":
    # Scrape Rome and Milan
    scrape_tecnocasa("roma", pages=3)
    scrape_tecnocasa("milano", pages=3)
