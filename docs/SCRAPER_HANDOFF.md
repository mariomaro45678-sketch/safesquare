# SafeSquare Real Estate Scraper - Handoff Document

## Project Overview

SafeSquare is an Italian real estate investment analysis platform. We've built a **production-ready scraper infrastructure** for Casa.it (Italian property portal) using **Playwright headless Chrome** to bypass CAPTCHA/Cloudflare protection.

**Status: WORKING** - The browser-based scraper successfully scrapes real listings from Casa.it.

## Current Architecture

### Key Files

```
backend/
├── app/
│   ├── scrapers/
│   │   ├── base_scraper.py          # HTTP-based scraper with proxy pool
│   │   ├── browser_scraper.py       # NEW: Playwright headless Chrome scraper
│   │   ├── casa_scraper.py          # Casa.it implementation (supports both modes)
│   │   ├── listing_ingestor.py      # Database upsert/deduplication
│   │   ├── scraper_config.yaml      # Configuration (rate limits, targets)
│   │   ├── rotating_proxies_ita.md  # 10 Italian rotating proxies
│   │   └── Sticky_proxies_us.md     # 100 US sticky proxies
│   ├── services/
│   │   └── market_pulse_service.py  # Market metrics aggregation
│   ├── api/v1/
│   │   └── listings.py              # REST API endpoints
│   └── models/
│       └── listing.py               # RealEstateListing SQLAlchemy model
├── scripts/
│   └── run_casa_scraper.py          # CLI with checkpoint/resume
├── tests/
│   ├── test_scraper.py              # Proxy rotation, HTML parsing tests
│   └── test_market_pulse.py         # Market metrics tests
└── Dockerfile                       # Updated with Playwright dependencies
```

### What's Implemented

1. **BrowserScraper** (`browser_scraper.py`) - NEW
   - Playwright-based headless Chrome
   - `playwright-stealth` for anti-detection
   - Proxy integration with existing pool
   - CAPTCHA detection and handling
   - Human behavior simulation (scrolling, mouse movements)
   - Session persistence (cookies)
   - Async/await architecture with sync wrapper

2. **ProxyPool** (`base_scraper.py:26-120`)
   - Italian rotating proxies (primary)
   - US sticky proxies (backup/failover)
   - Round-robin rotation with blacklisting
   - Auto-failover after 5 consecutive Italian failures

3. **CasaScraper** (`casa_scraper.py`)
   - **Dual mode support**: `browser` (default) or `http`
   - Adaptive CSS selectors (article tags, class patterns, URL detection)
   - Italian date parsing (oggi, ieri, X giorni/settimane/mesi fa)
   - Price/size extraction with sanity checks
   - Detail page scraper (rooms, bathrooms, floor, energy class)
   - Behavioral mimicry (15% skip, 10% random pages, 30% early stop)

4. **CLI** (`run_casa_scraper.py`)
   - `--mode browser|http` - Select scraping mode (default: browser)
   - `--no-headless` - Run browser visibly (for debugging CAPTCHA)
   - `--parallel` with ThreadPoolExecutor
   - `--resume` checkpoint/resume functionality
   - `--retry-failed` for failed municipalities
   - `--checkpoint-status` to view progress
   - Progress bars with tqdm

5. **API Endpoints** (Working in Docker)
   - `GET /api/v1/listings/market-pulse/{municipality_id}` - Market metrics
   - `GET /api/v1/listings/recent/{municipality_id}` - Recent listings
   - `GET /api/v1/listings/scraper-status` - Scraper health

### Database Schema

```sql
-- real_estate_listings table
id SERIAL PRIMARY KEY
municipality_id INTEGER REFERENCES municipalities(id)
source_id VARCHAR(100) UNIQUE  -- e.g., "casa_it_12345"
source_platform VARCHAR(50)    -- "casa_it", "immobiliare_it"
url VARCHAR(500)
title VARCHAR(200)
price FLOAT
size_sqm INTEGER
price_per_sqm FLOAT
date_posted DATE
date_removed DATE  -- NULL = active
is_active BOOLEAN DEFAULT TRUE
days_on_market INTEGER DEFAULT 0
views INTEGER DEFAULT 0
created_at TIMESTAMP
updated_at TIMESTAMP
```

## How It Works

### Browser Mode (Default)

```python
# CasaScraper now uses Playwright by default
scraper = CasaScraper(mode='browser', headless=True)
listings = scraper.scrape_municipality(roma, max_listings=100)
```

The browser scraper:
1. Launches headless Chromium with stealth settings
2. Configures proxy from the Italian/US pool
3. Navigates to Casa.it search pages
4. Waits for JavaScript to render
5. Detects and handles CAPTCHA challenges
6. Extracts HTML for parsing
7. Uses existing parsing logic from CasaScraper

### Proxy Integration

```python
# Proxies are loaded from files in app/scrapers/
# Format: username:password:hostname:port

# Example proxy rotation:
proxy, type = proxy_pool.get_next_proxy()
# Returns: ({'server': 'http://host:port', 'username': 'x', 'password': 'y'}, 'italian')
```

## Docker Setup

```bash
# Current running containers
docker ps
# safesquare_db        - PostgreSQL with PostGIS
# safesquare_backend   - FastAPI with Playwright (port 8000)
# safesquare_frontend  - React/Nginx (port 80)
# safesquare_test_db   - Test PostgreSQL (port 5433)

# Test the scraper
docker exec safesquare_backend python scripts/run_casa_scraper.py \
    --municipalities "Roma,Milano" --max-listings-per-city 20 --mode browser

# Test the API
curl http://localhost:8000/api/v1/listings/scraper-status
curl http://localhost:8000/api/v1/listings/market-pulse/5190  # Roma
```

## Usage Examples

```bash
# Scrape Roma with browser mode (default)
python scripts/run_casa_scraper.py --municipalities "Roma" --max-listings-per-city 50

# Scrape multiple cities
python scripts/run_casa_scraper.py --municipalities "Roma,Milano,Napoli" --max-listings-per-city 100

# Use visible browser for CAPTCHA debugging
python scripts/run_casa_scraper.py --municipalities "Roma" --max-listings-per-city 10 --no-headless

# Fall back to HTTP mode (may hit CAPTCHA)
python scripts/run_casa_scraper.py --municipalities "Roma" --mode http

# Parallel scraping (note: resource-intensive with browser mode)
python scripts/run_casa_scraper.py --municipalities "Roma,Milano,Napoli,Firenze,Bologna" \
    --parallel --workers 2 --max-listings-per-city 50

# Check progress
python scripts/run_casa_scraper.py --checkpoint-status

# Resume interrupted scrape
python scripts/run_casa_scraper.py --all-italy --max-listings-per-city 50 --resume

# Retry failed municipalities
python scripts/run_casa_scraper.py --retry-failed
```

## Test Results

Successfully tested on 2026-02-04:

```
Municipalities: Roma, Milano, Napoli, Firenze
Mode: browser (headless)
Results:
- Roma: 33 listings found, HTTP 200
- Milano: 36 listings found, HTTP 200
- Napoli: 27 listings found, HTTP 200
- Firenze: 29 listings found, HTTP 200
Success rate: 100%
```

## Configuration

### scraper_config.yaml (key sections)

```yaml
proxy_config:
  italian_proxy_file: "rotating_proxies_ita.md"
  us_proxy_file: "Sticky_proxies_us.md"
  max_consecutive_italian_failures: 5

rate_limits:
  casa_it_per_proxy: 1.0  # requests per second
  delay_mean_seconds: 2.0
  delay_std_dev_seconds: 0.8

search_params:
  max_pages_per_city: 9  # robots.txt compliant

anti_detection:
  skip_listing_probability: 0.15
  visit_about_page_probability: 0.10
```

## Dependencies

Added to `requirements.txt`:

```
# Browser-based Scraping (CAPTCHA bypass)
playwright==1.41.0        # Headless browser automation
playwright-stealth==1.0.6 # Anti-detection for Playwright
```

Added to `Dockerfile`:

```dockerfile
# Playwright browser dependencies
RUN apt-get install -y libnss3 libnspr4 libatk1.0-0 ...

# Install Playwright browsers
RUN playwright install chromium
```

## Known Limitations

1. **Resource Usage**: Browser mode uses more memory than HTTP mode (~200MB per browser instance)
2. **Speed**: Browser mode is slower (~5-10s per page vs ~1-2s for HTTP)
3. **Parallel Scaling**: Limited to 2-3 browser instances in parallel on typical hardware
4. **CAPTCHA Solving**: Manual intervention required for complex CAPTCHAs (use `--no-headless`)

## Future Improvements

1. **2captcha Integration**: Automatic CAPTCHA solving service
2. **Browser Pool**: Reuse browser instances across municipalities
3. **Immobiliare.it Support**: Add second property portal
4. **Incremental Updates**: Only scrape changed listings
5. **Distributed Scraping**: Scale across multiple containers

## Environment

- **Working Directory**: `/home/pap/Desktop/SafeSquare`
- **Python**: 3.11 (in Docker)
- **Database**: PostgreSQL 15 with PostGIS
- **Key Dependencies**: `playwright`, `playwright-stealth`, `beautifulsoup4`, `tenacity`, `tqdm`

---

**The scraper is now fully functional.** Use `--mode browser` (default) to bypass CAPTCHA protection.
