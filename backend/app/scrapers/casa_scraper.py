"""
Casa.it specific scraper implementation.

Handles:
- Search results parsing
- Individual listing detail extraction
- Municipality mapping
- Deduplication logic

Supports two scraping modes:
- 'browser': Playwright-based (default) - bypasses CAPTCHA/Cloudflare
- 'http': curl_cffi-based - faster but blocked by CAPTCHA
"""

import re
import asyncio
from typing import List, Dict, Optional
from datetime import date, datetime
from urllib.parse import urljoin, urlparse, parse_qs
import random

from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

try:
    from .browser_scraper import BrowserScraper
    BROWSER_AVAILABLE = True
except ImportError:
    BROWSER_AVAILABLE = False

from app.models.geography import Municipality
from app.core.database import SessionLocal
from sqlalchemy import func


class CasaScraper(BaseScraper):
    """
    Casa.it specific scraper with search and detail page parsing.

    Supports two modes:
    - 'browser': Uses Playwright headless Chrome (recommended for production)
    - 'http': Uses curl_cffi (faster but gets blocked by CAPTCHA)
    """

    BASE_URL = "https://www.casa.it"

    def __init__(self, config_path: str = None, mode: str = 'browser', headless: bool = True, listing_type: str = 'sale'):
        """
        Initialize Casa.it scraper.

        Args:
            config_path: Path to scraper config YAML
            mode: 'browser' for Playwright, 'http' for curl_cffi
            headless: Run browser in headless mode (browser mode only)
        """
        super().__init__(config_path)
        self.db = SessionLocal()
        self.mode = mode
        self.headless = headless
        self.listing_type = listing_type # 'sale' or 'rent'

        # Browser scraper instance (lazy initialized)
        self._browser_scraper: Optional[BrowserScraper] = None
        self._loop = None

        if mode == 'browser' and not BROWSER_AVAILABLE:
            self.logger.warning("Browser mode requested but Playwright not available. Falling back to HTTP mode.")
            self.mode = 'http'

        self.logger.info(f"CasaScraper initialized in '{self.mode}' mode")
    
    def _get_loop(self):
        """Get or create event loop for async operations."""
        try:
            self._loop = asyncio.get_event_loop()
            if self._loop.is_closed():
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop

    async def _init_browser(self):
        """Initialize browser scraper if not already done."""
        if self._browser_scraper is None:
            self._browser_scraper = BrowserScraper(
                config_path=self.config.get('_config_path')
            )
            await self._browser_scraper.init_browser(headless=self.headless)
            self.logger.info("Browser scraper initialized")

    async def _browser_request(self, url: str) -> str:
        """Make request using browser."""
        await self._init_browser()
        return await self._browser_scraper.make_request(url)

    def fetch_page(self, url: str) -> str:
        """
        Fetch page content using configured mode.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string
        """
        if self.mode == 'browser':
            loop = self._get_loop()
            return loop.run_until_complete(self._browser_request(url))
        else:
            # Use original curl_cffi method
            response = self.make_request(url)
            return response.text

    def build_search_url(self, municipality_name: str, page: int = 1) -> str:
        """
        Build Casa.it search URL for a municipality.

        Args:
            municipality_name: Name of municipality (e.g., "Roma", "Milano")
            page: Page number (1-9 per robots.txt)

        Returns:
            Full search URL
        """
        # Casa.it URL format: /vendita/residenziale/{city}/?page={n} or /affitto/residenziale/{city}/?page={n}
        city_slug = municipality_name.lower().replace(' ', '-')
        
        action = 'affitto' if self.listing_type == 'rent' else 'vendita'

        if page == 1:
            return f"{self.BASE_URL}/{action}/residenziale/{city_slug}/"
        else:
            return f"{self.BASE_URL}/{action}/residenziale/{city_slug}/?page={page}"
    
    def scrape_municipality(self, municipality: Municipality, max_listings: int = 100) -> List[Dict]:
        """
        Scrape all listings for a municipality.
        
        Args:
            municipality: Municipality object from database
            max_listings: Maximum listings to scrape
        
        Returns:
            List of listing dicts
        """
        all_listings = []
        max_pages = self.config['search_params']['max_pages_per_city']
        
        self.logger.info(f"Starting scrape for {municipality.name}")
        
        for page in range(1, max_pages + 1):
            # Random chance to stop early (behavioral mimicry)
            if page > 3 and random.random() < 0.3:
                self.logger.info(f"Randomly stopping pagination at page {page}")
                break
            
            # Human behavior simulation
            if random.random() < 0.1:
                self.simulate_human_behavior()
            
            # Scrape search results page
            url = self.build_search_url(municipality.name, page)
            self.logger.info(f"Scraping page {page}: {url}")

            try:
                html = self.fetch_page(url)
                listings = self.parse_search_results(html, municipality)
                
                if not listings:
                    self.logger.info(f"No listings found on page {page}, stopping")
                    break
                
                all_listings.extend(listings)
                self.logger.info(f"Found {len(listings)} listings on page {page}")
                
                # Check if we hit our limit
                if len(all_listings) >= max_listings:
                    self.logger.info(f"Reached max listings ({max_listings})")
                    break
                
                # Human delay between pages
                self.human_delay()
                
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {e}")
                break
        
        self.logger.info(f"Total listings scraped for {municipality.name}: {len(all_listings)}")
        return all_listings[:max_listings]
    
    def parse_search_results(self, html: str, municipality: Municipality) -> List[Dict]:
        """
        Parse search results page and extract listing preview data.
        
        Args:
            html: HTML content
            municipality: Municipality object
        
        Returns:
            List of listing dicts (partial data)
        """
        soup = self.parse_html(html)
        listings = []
        
        # Try multiple selector patterns (Italian real estate sites vary)
        listing_cards = []
        
        # Pattern 1: Article tags (common semantic pattern)
        articles = soup.find_all('article')
        if len(articles) > 0:
            self.logger.info(f"Found {len(articles)} listings using <article> tags")
            listing_cards = articles
        
        # Pattern 2: Divs with common listing classes
        if not listing_cards:
            for class_pattern in ['listing', 'card', 'property', 'annuncio', 'item']:
                cards = soup.find_all('div', class_=re.compile(class_pattern, re.I))
                if len(cards) > 3:  # Reasonable number
                    self.logger.info(f"Found {len(cards)} listings using class pattern: {class_pattern}")
                    listing_cards = cards
                    break
        
        # Pattern 3: Fallback - any element with listing URL
        if not listing_cards or len(listing_cards) > 200: # 406 cards might be too generic
             # If we found too many cards (like generic containers), try to refine
             if len(listing_cards) > 200:
                 self.logger.info(f"Found too many cards ({len(listing_cards)}), trying to refine listing detection")
                 listing_cards = []

             # Find all links with /vendita/residenziale/ (specific to listings usually)
             # Casa.it listing URLs often look like: /vendita/residenziale/milano/appartamento-1234
             links = soup.find_all('a', href=re.compile(r'/(vendita|immobile)/', re.I))
             
             # Filter out non-listing links (like pagination, footer, etc.)
             # Heuristic: Listing links usually have a title or price info inside or nearby
             valid_containers = []
             for link in links:
                 # look for parent container that might be a card
                 parent = link.find_parent('div', class_=re.compile(r'(card|article|item)', re.I))
                 if parent:
                      valid_containers.append(parent)
                 else:
                      valid_containers.append(link.parent) # Fallback to direct parent
             
             # Deduplicate
             valid_containers = list(set(valid_containers))
             
             if len(valid_containers) > 0:
                 self.logger.info(f"Found {len(valid_containers)} potential listing containers via links")
                 listing_cards = valid_containers

        if not listing_cards:
            self.logger.error("No listing cards found with any selector pattern")
            # Log a snippet of the HTML for debugging
            self.logger.error(f"HTML snippet: {html[:500]}")
            return []
        
        for card in listing_cards:
            try:
                listing_data = self._extract_listing_preview(card, municipality)
                pass # Logic continues below
                
                if listing_data:
                    # Random chance to skip listing (behavioral mimicry)
                    skip_prob = self.config['anti_detection']['skip_listing_probability']
                    if random.random() < skip_prob:
                        self.logger.debug(f"Randomly skipping listing {listing_data.get('source_id')}")
                        continue
                    
                    listings.append(listing_data)
                    
            except Exception as e:
                self.logger.warning(f"Error parsing listing card: {e}")
                continue
        
        return listings
    
    def _extract_listing_preview(self, card, municipality: Municipality) -> Optional[Dict]:
        """
        Extract data from listing card on search results.
        
        Args:
            card: BeautifulSoup element
            municipality: Municipality object
        
        Returns:
            Dict with listing data or None
        """
        try:
            # Extract URL (try multiple patterns)
            link = None
            
            # Pattern 1: Direct <a> tag in card with valid href
            link = card.find('a', href=re.compile(r'/(vendita|immobile)/', re.I))
            
            # Pattern 2: Any <a> if we are desperate
            if not link:
                link = card.find('a', href=True)
            
            if not link:
                return None
            
            url = urljoin(self.BASE_URL, link['href'])
            
            # Generate source_id from URL
            source_id = None
            
            # Try ID pattern common in URLs
            id_match = re.search(r'(?:id[-_]|/)(\d{5,})', url)
            if id_match:
                source_id = f"casa_it_{id_match.group(1)}"
            
            # Fallback: hash URL
            if not source_id:
                import hashlib
                source_id = f"casa_it_{hashlib.md5(url.encode()).hexdigest()[:10]}"
            
            # Extract title
            title = None
            # Pattern 1: Heading tags
            for tag in ['h1', 'h2', 'h3', 'h4']:
                title_elem = card.find(tag)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            # Pattern 2: Link text
            if not title and link:
                title = link.get_text(strip=True)
                
            # Fallback
            if not title or len(title) < 5:
                title = "Appartamento"
            
            # Extract price
            price = None
            # Pattern 1: Class based
            price_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'(price|prezzo)', re.I))
            if price_elem:
                price = self._parse_price(price_elem.get_text(strip=True))
            
            # Pattern 2: Regex search in text
            if not price:
                price_text = card.find(text=re.compile(r'€\s*[\d.,]+'))
                if price_text:
                    price = self._parse_price(str(price_text))

            # Extract size
            size_sqm = None
            size_text = card.find(text=re.compile(r'\d+\s*mq', re.I)) # casa.it usually uses 'mq'
            if not size_text:
                 size_text = card.find(text=re.compile(r'\d+\s*m[²2]', re.I))

            if size_text:
                size_sqm = self._parse_size(str(size_text))
            
            # Calculate price per sqm
            price_per_sqm = None
            if price and size_sqm and size_sqm > 0:
                price_per_sqm = round(price / size_sqm, 2)
            
            return {
                'municipality_id': municipality.id,
                'source_id': source_id,
                'source_platform': 'casa_it',
                'url': url,
                'title': title[:200],
                'price': price,
                'size_sqm': size_sqm,
                'price_per_sqm': price_per_sqm,
                'date_posted': date.today(),
                'is_active': True,
                'listing_type': self.listing_type,
                'days_on_market': 0,
                'views': 0
            }
            
        except Exception as e:
            # self.logger.debug(f"Failed to extract listing preview: {e}") 
            # reduce noise
            return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from text.
        
        Args:
            price_text: Text containing price (e.g., "€ 250.000", "250000 EUR")
        
        Returns:
            Float price or None
        """
        try:
            # Remove non-numeric except decimal point
            cleaned = re.sub(r'[^\d,.]', '', price_text)
            cleaned = cleaned.replace('.', '').replace(',', '.')  # Handle EU format
            
            if cleaned:
                price = float(cleaned)
                # Sanity check (€10k - €10M)
                if 10000 <= price <= 10000000:
                    return price
        except:
            pass
        
        return None
    
    def _parse_size(self, size_text: str) -> Optional[int]:
        """
        Extract numeric size from text.
        
        Args:
            size_text: Text containing size (e.g., "85 m²", "120m2")
        
        Returns:
            Int size in sqm or None
        """
        try:
            match = re.search(r'(\d+)\s*m[²q2]', size_text)
            if match:
                size = int(match.group(1))
                # Sanity check (20-500 sqm for residential)
                if 20 <= size <= 500:
                    return size
        except:
            pass
        
        return None
    
    def scrape_listing_detail(self, url: str) -> Optional[Dict]:
        """
        Scrape individual listing detail page for complete data.

        Extracts:
        - Date posted
        - Views count
        - Number of rooms
        - Number of bathrooms
        - Floor number
        - Energy class
        - Heating type
        - Condition
        - Description

        Args:
            url: Listing detail URL

        Returns:
            Dict with additional listing fields, or None on failure
        """
        try:
            self.human_delay()
            html = self.fetch_page(url)
            soup = self.parse_html(html)

            details = {}

            # Extract posted date - look for date containers
            date_patterns = [
                r'pubblicat[oa]\s*(?:il\s*)?(.+?)(?:$|\n|<)',
                r'inserit[oa]\s*(?:il\s*)?(.+?)(?:$|\n|<)',
                r'data\s*annuncio[:\s]*(.+?)(?:$|\n|<)',
            ]
            for pattern in date_patterns:
                date_match = soup.find(text=re.compile(pattern, re.I))
                if date_match:
                    # Find actual date text (might be in parent or sibling)
                    date_text = str(date_match)
                    match = re.search(pattern, date_text, re.I)
                    if match:
                        details['date_posted'] = self._parse_date(match.group(1))
                        break

            # Extract views count
            views_patterns = [
                r'(\d+)\s*visualizzazion[ie]',
                r'visto\s*(\d+)\s*volt[ea]',
                r'(\d+)\s*views',
            ]
            for pattern in views_patterns:
                views_match = soup.find(text=re.compile(pattern, re.I))
                if views_match:
                    match = re.search(pattern, str(views_match), re.I)
                    if match:
                        details['views'] = int(match.group(1))
                        break

            # Extract property features from structured data
            # Try JSON-LD first (structured data)
            script_ld = soup.find('script', type='application/ld+json')
            if script_ld:
                try:
                    import json
                    ld_data = json.loads(script_ld.string)
                    if isinstance(ld_data, dict):
                        if ld_data.get('@type') in ['Product', 'RealEstateListing', 'Apartment', 'House']:
                            if 'numberOfRooms' in ld_data:
                                details['rooms'] = int(ld_data['numberOfRooms'])
                            if 'numberOfBathroomsTotal' in ld_data:
                                details['bathrooms'] = int(ld_data['numberOfBathroomsTotal'])
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass

            # Extract rooms from HTML
            if 'rooms' not in details:
                rooms_patterns = [
                    r'(\d+)\s*(?:local[ie]|stanz[ae]|vani)',
                    r'(?:local[ie]|stanz[ae]|vani)[:\s]*(\d+)',
                ]
                for pattern in rooms_patterns:
                    rooms_match = soup.find(text=re.compile(pattern, re.I))
                    if rooms_match:
                        match = re.search(pattern, str(rooms_match), re.I)
                        if match:
                            rooms = int(match.group(1))
                            if 1 <= rooms <= 20:  # Sanity check
                                details['rooms'] = rooms
                                break

            # Extract bathrooms
            if 'bathrooms' not in details:
                bath_patterns = [
                    r'(\d+)\s*bagn[io]',
                    r'bagn[io][:\s]*(\d+)',
                ]
                for pattern in bath_patterns:
                    bath_match = soup.find(text=re.compile(pattern, re.I))
                    if bath_match:
                        match = re.search(pattern, str(bath_match), re.I)
                        if match:
                            baths = int(match.group(1))
                            if 1 <= baths <= 10:  # Sanity check
                                details['bathrooms'] = baths
                                break

            # Extract floor
            floor_patterns = [
                r'piano[:\s]*(\d+|terra|ultimo|rialzato)',
                r'(\d+)[°º]?\s*piano',
            ]
            for pattern in floor_patterns:
                floor_match = soup.find(text=re.compile(pattern, re.I))
                if floor_match:
                    match = re.search(pattern, str(floor_match), re.I)
                    if match:
                        floor_text = match.group(1).lower()
                        if floor_text == 'terra':
                            details['floor'] = 0
                        elif floor_text in ('ultimo', 'rialzato'):
                            details['floor_text'] = floor_text
                        else:
                            try:
                                details['floor'] = int(floor_text)
                            except ValueError:
                                pass
                        break

            # Extract energy class
            energy_patterns = [
                r'classe\s*energetica[:\s]*([a-g][+\d]*)',
                r'energia[:\s]*([a-g][+\d]*)',
                r'ape[:\s]*([a-g][+\d]*)',
            ]
            for pattern in energy_patterns:
                energy_match = soup.find(text=re.compile(pattern, re.I))
                if energy_match:
                    match = re.search(pattern, str(energy_match), re.I)
                    if match:
                        details['energy_class'] = match.group(1).upper()
                        break

            # Extract description text
            desc_elem = soup.find(['div', 'p'], class_=re.compile(r'description|descrizion', re.I))
            if desc_elem:
                desc_text = desc_elem.get_text(strip=True)
                if len(desc_text) > 50:  # Meaningful description
                    details['description'] = desc_text[:2000]  # Limit length

            self.logger.info(f"Extracted {len(details)} detail fields from {url}")
            return details if details else None

        except Exception as e:
            self.logger.error(f"Error scraping detail page {url}: {e}")
            return None
    
    def _parse_date(self, date_text: str) -> date:
        """
        Parse Italian date from text.

        Handles:
        - "Oggi" / "oggi" (today)
        - "Ieri" / "ieri" (yesterday)
        - "X giorni fa" (X days ago)
        - "X settimane fa" / "una settimana fa" (X weeks ago)
        - "X mesi fa" / "un mese fa" (X months ago)
        - "15/01/2025" (DD/MM/YYYY)
        - "15 gennaio 2025" (DD month YYYY)

        Args:
            date_text: Italian date string

        Returns:
            date object (defaults to today if parsing fails)
        """
        from datetime import timedelta

        if not date_text:
            return date.today()

        text = date_text.lower().strip()

        # Handle "oggi" (today)
        if 'oggi' in text:
            return date.today()

        # Handle "ieri" (yesterday)
        if 'ieri' in text:
            return date.today() - timedelta(days=1)

        # Handle "X giorni fa" (X days ago)
        days_match = re.search(r'(\d+)\s*giorn[io]\s*fa', text)
        if days_match:
            days = int(days_match.group(1))
            return date.today() - timedelta(days=days)

        # Handle "una settimana fa" / "X settimane fa" (weeks ago)
        if 'una settimana fa' in text:
            return date.today() - timedelta(weeks=1)
        weeks_match = re.search(r'(\d+)\s*settiman[ae]\s*fa', text)
        if weeks_match:
            weeks = int(weeks_match.group(1))
            return date.today() - timedelta(weeks=weeks)

        # Handle "un mese fa" / "X mesi fa" (months ago)
        if 'un mese fa' in text:
            return date.today() - timedelta(days=30)
        months_match = re.search(r'(\d+)\s*mes[ie]\s*fa', text)
        if months_match:
            months = int(months_match.group(1))
            return date.today() - timedelta(days=months * 30)

        # Handle DD/MM/YYYY format
        date_match = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', text)
        if date_match:
            try:
                day = int(date_match.group(1))
                month = int(date_match.group(2))
                year = int(date_match.group(3))
                return date(year, month, day)
            except ValueError:
                pass

        # Handle "DD mese YYYY" format (e.g., "15 gennaio 2025")
        italian_months = {
            'gennaio': 1, 'febbraio': 2, 'marzo': 3, 'aprile': 4,
            'maggio': 5, 'giugno': 6, 'luglio': 7, 'agosto': 8,
            'settembre': 9, 'ottobre': 10, 'novembre': 11, 'dicembre': 12
        }
        for month_name, month_num in italian_months.items():
            month_match = re.search(rf'(\d{{1,2}})\s*{month_name}\s*(\d{{4}})', text)
            if month_match:
                try:
                    day = int(month_match.group(1))
                    year = int(month_match.group(2))
                    return date(year, month_num, day)
                except ValueError:
                    pass

        # Fallback to today
        return date.today()
    
    def _parse_views(self, views_text: str) -> int:
        """Extract view count from text."""
        match = re.search(r'(\d+)', views_text)
        return int(match.group(1)) if match else 0
    
    def close(self):
        """Close database connection and browser."""
        self.db.close()

        # Close browser if initialized
        if self._browser_scraper:
            loop = self._get_loop()
            loop.run_until_complete(self._browser_scraper.close())
            self._browser_scraper = None
            self.logger.info("Browser scraper closed")
