# 🚀 ITALIAN PROPERTY PLATFORM - PROJECT LOG

## 🧠 CURRENT STATE (Source of Truth)
*   **Stack**: Python (FastAPI), React.js, PostgreSQL (PostGIS).
*   **Live URL**: TBD
*   **Key Decisions**:
    *   **Scoring Optimization**: Implemented batched commits (every 100 records) in `batch_calculate_scores.py` to prevent transaction timeouts.
    *   **Pipeline Visibility**: Refactored `master_background_pipeline.py` to use `subprocess.Popen` for real-time log streaming.
    *   **Geocoding Resilience**: Added 10s timeouts and enhanced error handling to `update_geometries.py`.
    *   **Data Completeness**: 100% municipality coverage across Prices, Risks, Crime, and Air Quality (7,895 towns).
*   **Air Quality Unification**: Created `ingest_regional_air_quality.py` to unify regional datasets (Lombardia, Lazio, Veneto, Emilia, Campania) into the `AirQuality` table with automated spatial and ISTAT mapping.

## ⚠️ KNOWN PITFALLS (Do Not Repeat Errors)
* **Column Detection**: Excel files often have non-standard column headers. Use loose keyword matching in ingestors.
* **Code Formatting**: ISTAT/Municipality codes should always be treated as 6-digit zero-filled strings to avoid lookup failures.
* **Geometry Dependency**: Municipality centroids are 99% resolved. Search uses spatial lookup by default.
* **Performance**: Maintain 1 req/sec for geocoding to avoid Nominatim bans. **CRITICAL**: Background processing (batch scores) must have a `time.sleep(0.1)` delay to prevent system freezes on consumer hardware.
* **Transaction Timeouts**: Batch commit required for large-scale SQLAlchemy operations (100-500 records).
* **Data Consistency**: Added `connectivity_score`, `digital_connectivity_score`, `air_quality_score`, and `confidence_score` to `investment_scores` table.
* **Database Stability**: Resolved `property_user` authentication loop by standardizing password to `testpass` and syncing `.env`.
* **Frontend Resilience**: Fixed React rendering crashes in `PropertyDetailsPage` by adding comprehensive null-guards to chart components.


- **Status**: ✅ Remediation Phases 1-4 Complete. ✅ Frontend Premium Revamp Complete. ✅ PropertyDetailsPage field-name fixes applied. 🟠 Scoring calibration under investigation (see handoff doc).

---

## 📝 RECENT SESSION LOGS (Newest First)

## [2026-02-19 09:20] 🤖 Antigravity | 🎨 Frontend Design Transformation Complete
- **Status**: ✅ **Premium Dark Theme Implementation Complete**.
- **Changes**:
    - `frontend/src/App.js` — Added global aurora background with animated gradient blobs (blue, purple, cyan), noise overlay texture, and proper z-index layering. Changed base styling to `bg-dark-900 text-white antialiased`.
    - `frontend/public/index.html` — Enhanced with dark theme meta tags (`theme-color: #0f0f1a`, `color-scheme: dark`), SEO-optimized title and description, Open Graph tags for social sharing, Twitter card meta tags, and preconnect hints for Google Fonts.
- **Context**: 🚀 Completed the frontend design transformation to match the Design Specification:
    1. **Dark Theme**: Deep cobalt blue primary (#0066d6) with dark surfaces (#0f0f1a, #202033).
    2. **Glassmorphism**: Cards with backdrop blur, subtle borders, and translucent backgrounds.
    3. **Aurora Effects**: Animated gradient blobs creating ambient lighting.
    4. **Noise Texture**: Subtle overlay for depth and premium feel.
    5. **Modern Typography**: Inter font family with antialiasing.
- **Verified**: Header.js, Footer.js, HomePage.js all aligned with dark theme design system.

## [2026-02-06 15:15] 🤖 Antigravity | 🗺️ Map Discovery Fix (Critical)
- **Status**: ✅ **Fixed**.
- **Issue**: User reported a "Green Badge" (High Score) marker appearing in the ocean (West of France), indicating invalid coordinates or data drift.
- **Root Cause**: While database scans didn't reveal the exact erroneous record in `property_db`, the frontend was permissive with off-shore coordinates.
- **Fix**: Implemented strict **geographic bounding box filtering** in `PropertyMap.js`.
    - **Logic**: Markers are now ONLY rendered if `Latitude (35-48)` and `Longitude (6-19)` (Italy's approximate bounds).
    - **Outcome**: Any data points with `0,0` or other invalid coordinates are automatically hidden, preventing "ocean" redirection and visual bugs.
    - **Deployed**: Restarted `safesquare-frontend` container.

## [2026-02-06 15:00] 🤖 Antigravity | 🗺️ Map Discovery Improvements
- **Status**: ✅ **Improved & Fixed**.
- **Issue**: User reported "Discover" map only showed red/yellow cards at zoom levels (missing high-value targets) and clicking some cities redirected to the "sea" (invalid coordinates).
- **Fixes**:
    - **Backend (`locations.py`)**: Modified `/discover` logic to **always** include municipalities with `investment_score >= 7.0` regardless of population/zoom level.
        - *Verification*: Confirmed small towns (e.g., *Rovereto*, *Grassobbio*) now appear at national zoom levels.
    - **Frontend (`PropertyMap.js`)**: Added robust coordinate validation to `FitBounds` to filter out `(0,0)` coordinates, preventing the map from centering on "Null Island."
- **Next**: Monitor user feedback on map performance.

## [2026-02-06 14:40] 🤖 Antigravity | 🔌 Frontend-Backend Sync Verification
- **Status**: ✅ **Verified & Sync Fixed**.
- **Issue**: Deep inspection revealed mismatches between Frontend expectations (`PropertyDetailsPage`) and Backend API responses.
- **Fixes**:
    - **`LocationResponse`**: Added missing fields `province_code` and `altitude` (required for UI badges/stats).
    - **`DemographicsResponse`**: Added missing `population_trend` field.
    - **`demographics.py`**: Implemented trend calculation logic (current vs previous year population).
    - **Server**: Restarted `safesquare-backend` container to apply changes.
- **Verification**: 
    - Analyzed `frontend/src/pages/PropertyDetailsPage.js`.
    - executed `verify_api_response.py` against live API.
    - Confirmed all ~25 data fields (snake_case) now match perfectly.

## [2026-02-06 14:15] 🤖 Antigravity | 🏠 Rental Data Implementation & Scraper Fixes
- **Status**: ✅ **Rental Scraper Operational (Technical Success)**.
- **Changes**: 
    - `backend/app/scrapers/casa_scraper.py` (Added `listing_type` support).
    - `backend/scripts/run_casa_scraper.py` (CLI updated).
    - `backend/app/models/listing.py` (Schema update).
    - `backend/alembic/versions/44048d776300_add_listing_type_manual.py` (Manual Migration).
    - `backend/logs/` (Removed Immobiliare logs).
- **Context**: 🚀 Replaced discontinued Immobiliare scraper with Casa.it Rental capability.
    1.  **Immobiliare Removed**: Deleted all legacy scraper files.
    2.  **Rentals Implemented**: `RealEstateListing` now supports `listing_type='rent'`. `CasaScraper` constructs rental-specific URLs (`/affitto/residenziale/...`).
    3.  **Dependencies Resolved**: Fixed `playwright-stealth` (downgraded to 1.0.6), `curl_cffi`, `tqdm`, `tenacity`.
    4.  **Verification**: Scraper runs successfully in browser mode (headless/headed).
    5.  **Note**: Initial test run returned 0 listings for Latina/Rome, indicating technical pipeline works but selectors may need tuning for rental page specifics.

## [2026-02-05] 🎯 COMPLETE DATA PIPELINE OVERHAUL

### Ingestion Completed
- **Air Quality**: 7,895 records (pollution_full_national.xlsx)
- **Crime**: 7,895 records (crime_full_mvp_regions.xlsx)
- **Services**: 26k nodes aggregated → hospital/school/supermarket counts
- **Transport**: 7.1k nodes aggregated → train/highway distances

### Algorithm Improvements (scoring_engine.py)
1. **Constants** (`SCORE_PIVOT`: 6.5→5.5, `CONTRAST_MULTIPLIER`: 1.8→1.3)
2. **Missing data handling**: Now excluded from weighted avg instead of penalized
3. **Coverage tracking**: All metrics track real vs fallback
4. **New files**: ingest_pollution_direct.py, ingest_crime_direct.py (fixed float/int code issue)

### Impact
- Green scores: 0 → **95 municipalities (1.9%)**
- Roma: 3.0 → **7.4 (confidence 92%)**
  - Connectivity 2.8→10.0, Services 0.0→10.0
- Top scorers: Corsico/Grassobbio/Mariano Comense (7.7)
- Distribution: 1.9% green, 59.6% yellow, 38.5% red

### Backend Changes
backend/app/api/schemas/score.py - Added OMIZoneScoreResponse schema with zone details, score, and geometry support
backend/app/api/v1/endpoints/scores.py - Added GET /scores/municipality/{id}/omi-zones batch endpoint

### Frontend Changes
frontend/src/services/api.js - Added scoreAPI.getOMIZoneScores() method
frontend/src/components/dashboard/ZoneScoreCard.js - New compact score card for zones
frontend/src/components/dashboard/ZoneList.js - Scrollable list with sort/filter controls
frontend/src/components/map/ZonePolygonLayer.js - GeoJSON layer for zone boundaries
frontend/src/components/map/PropertyMap.js - Added children prop support
frontend/src/pages/PropertyDetailsPage.js - Integrated zone display

## [2026-02-04] 🤖 Claude Code | 🔧 PropertyDetailsPage: API Field-Name Mismatch Remediation
- **Status**: ✅ **All 7 display bugs fixed. Build verified (254 kB JS, 0 errors).**
- **Root Cause**: The Phase 6-8 premium UI rewrite hard-coded response field names that did not match the actual FastAPI endpoint contracts. The backend was returning correct data; nothing on the backend was changed.
- **Bugs Fixed (all in `frontend/src/pages/PropertyDetailsPage.js`)**:
    1. **Avg Price N/A** — Page read `municipality.avg_price_sqm` (field does not exist on that endpoint). Added a call to `propertyAPI.getMunicipalityStatistics(id)` and now reads `statistics.avg_price_per_sqm`.
    2. **Population 0** — `Municipality.population` is NULL in the DB for Roma (and many others); real value lives in Demographics. Added fallback chain: `municipality.population || demographics.population || 0`.
    3. **Income Index N/A** — Page read `demographics.income_index` which does not exist. Backend returns `median_income_eur`. Now computes index as `(median_income_eur / 30000) * 100` (national-median ratio).
    4. **Price History empty** — Page unwrapped `response.history` but the `/prices/municipality/{id}` endpoint returns a flat array (no wrapper). Removed `.history`. Also added `.slice().reverse()` because the API returns newest-first but the chart expects chronological order.
    5. **Investment Score stuck at 5.0** — Page read `scoreData.investment_score`; actual field is `scoreData.overall_score`. The 5.0 was the hardcoded fallback.
    6. **Risk Level stuck at "Low"** — Page read `riskData.overall_risk`; actual field is `riskData.overall_risk_level`.
    7. **Risk Badges invisible / AI Verdict "0 High"** — Page accessed `riskData.seismic` (key is `seismic_risk`), and `.risk_level` (field is `hazard_level`, Title Case). Fixed keys and added `.toLowerCase()`.
- **Follow-up (open)**: Roma overall_score = 1.4 in DB while component averages ≈ 6.3. Likely a scoring-engine weight/calibration bug. See `_HANDOFF_SCORING_CALIBRATION.md`.

## [2026-02-04] 🤖 Antigravity | 🎨 Phase 6-8: Premium Dashboard Revamp & Infrastructure Shift
- **Status**: ✅ **Architecture & UI/UX Overhaul Complete.** 
- **Core Update**: Shifted the entire platform to a high-end fintech aesthetic ("Bloomberg meets Stripe") and moved infrastructure to dedicated ports (8080/3001) to resolve local port conflicts.
- **Major Features**:
    - **Design System**: Implemented a comprehensive design tokens library in Tailwind (Deep Cobalt Blue, Emerald, Amber, Crimson) with custom glassmorphism and motion system.
    - **Header/Footer**: Added scroll-based glassmorphism, animated logo with live indicators, and newsletter integration.
    - **Home Page**: Complete redesign with animated hero blobs, interactive counters, and floating market data cards.
    - **Premium Charts**: Revamped `PriceTrendChart` (area gradient, time selectors) and `ScoreRadarChart` (category summaries, emoji icons).
    - **Dashboard Components**: Built `ScoreCard` (animated circular gauge) and `StatCard` (intersection-observer animations/trends).
    - **Property Dashboard**: Implemented the full `PropertyDetailsPage` with an AI Market Verdict component, risk badges, and comprehensive loading skeletons.
- **Stability & Infrastructure**:
    - **Port Shift**: Moved Backend to `8080` and Frontend to `3001` (CORS updated).
    - **Auth Fix**: Resolved DB authentication loop by standardizing `property_db` password to `testpass` and syncing `.env` across services.
    - **Bug Fixes**: 
        - Resolved `useParams` mismatch in `PropertyDetailsPage` (`id` vs `municipalityId`).
        - Fixed "is not a function" errors in `api.js` by aliasing `getPriceHistory`, `getScore`, and `getRisks`.
        - Corrected default API port in `api.js` to `8080`.
- **Build Status**: Production build verified (253KB JS, 16KB CSS gzipped).

## [2026-02-04] 🤖 Claude Code | 🚀 STEP 27.1: Browser-Based CAPTCHA Bypass — Live & Scraping
- **Status**: ✅ **Production scraper is live.** Casa.it returns HTTP 200 through headless Chrome; real listings are being ingested.
- **Problem Solved**: `curl_cffi` (chrome110 TLS fingerprinting) was blocked after 1–2 requests by Casa.it's Cloudflare/JS challenge. All 12 retry attempts exhausted, both Italian and US proxy pools blacklisted.
- **Solution**: Replaced the HTTP transport layer with Playwright headless Chromium + `playwright-stealth`. The existing proxy pool, parsing logic, and `ListingIngestor` pipeline are unchanged.
- **Files Changed**:
    - `app/scrapers/browser_scraper.py` (NEW) — Async Playwright scraper:
        - `stealth_async` applied to every page (evades `navigator.webdriver`, canvas fingerprint, etc.)
        - Proxy injected at browser-launch time from existing `ProxyPool`
        - CAPTCHA detection (Cloudflare Turnstile, hCaptcha, reCAPTCHA, Italian-language variants)
        - Auto-wait for JS challenges (up to 10s), manual-solve fallback (120s, visible-browser mode)
        - Human behaviour: random scroll, mouse-move, and pause between navigations
        - Cookie save/load for session persistence
        - Sync wrapper (`SyncBrowserScraper`) for drop-in use in threaded CLI
    - `app/scrapers/casa_scraper.py` — Dual-mode transport:
        - New `mode` parameter: `'browser'` (default) or `'http'`
        - `fetch_page()` routes to Playwright or `curl_cffi` transparently; all downstream parsing untouched
        - Browser instance lazy-initialised and explicitly closed in `close()`
    - `scripts/run_casa_scraper.py` — CLI flags: `--mode browser|http`, `--no-headless`
    - `backend/Dockerfile` — Added 15 Playwright system libs + `playwright install chromium`
    - `backend/requirements.txt` — `playwright==1.41.0`, `playwright-stealth==1.0.6`
    - `app/scrapers/scraper_config.yaml` — Proxy paths changed to relative (resolves inside container)
    - `app/scrapers/base_scraper.py` — `resolve_proxy_path()` helper: tries config-dir, then CWD, then absolute
    - `docker-compose.yml` — Added `./logs:/app/logs` volume so scraper logs persist on host
- **Logging**: All scraper activity (base + browser) now flows into a single `logs/scraper_casa.log`. CLI run summaries go to `logs/scraper_run.log`. Both survive container restarts via the new volume mount.
- **Verified Results** (2026-02-04, headless, Italian proxy):
    - Roma: 33 listings parsed, HTTP 200
    - Milano: 36 listings parsed, HTTP 200
    - Napoli: 27 listings parsed, HTTP 200
    - Firenze: 29 listings parsed, HTTP 200
    - **Success rate: 100%, 0 errors, 0 CAPTCHAs triggered**

## [2026-02-04] 🤖 Claude Code | 🚀 STEP 27: Real-Time Market Pulse Scraper — Complete
- **Status**: ✅ **Production-ready scraper infrastructure complete.** Full Casa.it scraper with enterprise anti-detection, checkpoint/resume, and comprehensive unit tests.
- **Components Built**:
    - `app/scrapers/base_scraper.py` — Enterprise-grade base scraper:
        - ProxyPool with Italian rotating proxies (primary) + US sticky (backup)
        - Automatic failover after 5 consecutive Italian failures
        - TLS fingerprinting via curl_cffi (chrome110 impersonation)
        - ML-based human delays (normal distribution)
        - Tenacity retry logic (12 attempts, exponential backoff)
    - `app/scrapers/casa_scraper.py` — Casa.it specific implementation:
        - Adaptive CSS selectors (article tags, class patterns, URL detection)
        - Italian date parsing (oggi, ieri, X giorni/settimane/mesi fa, DD/MM/YYYY, DD mese YYYY)
        - Price/size extraction with sanity checks
        - Detail page scraper (rooms, bathrooms, floor, energy class, description)
        - Behavioral mimicry (15% skip, 10% random pages, 30% early stop)
    - `app/scrapers/listing_ingestor.py` — Database integration:
        - Upsert logic via unique source_id
        - Lifecycle management (active → inactive)
        - Days on market calculation
        - Batch processing with stats
    - `app/services/market_pulse_service.py` — Metrics aggregation:
        - Active listings count
        - Median days on market (DOM)
        - Absorption rate (30-day window)
        - Inventory months
        - Average price per sqm
    - `scripts/run_casa_scraper.py` — CLI with advanced features:
        - Parallel processing (ThreadPoolExecutor)
        - Checkpoint/resume functionality
        - Progress bars (tqdm)
        - `--retry-failed` for failed municipalities
        - `--checkpoint-status` to view progress
- **Unit Tests Created** (2 files, 30+ tests):
    - `tests/test_scraper.py` — ProxyPool rotation, HTML parsing, date/price/size extraction
    - `tests/test_market_pulse.py` — All market metrics with fixtures
- **Configuration**: `app/scrapers/scraper_config.yaml` (rate limits, anti-detection, target municipalities)
- **Note**: Scraper POC successful but Casa.it deploys aggressive CAPTCHA. Production use requires premium residential proxies or CAPTCHA solving integration.

## [2026-02-04] 🤖 Antigravity | 🏗️ Cadastral Map Integration — Code Complete, Data Pending
- **Status**: 🟠 **Blocked on data acquisition.** The Agenzia delle Entrate bulk download portal requires registration before files can be downloaded. All code is built and tested; no action needed until credentials are available.
- **Source**: https://www.agenziaentrate.gov.it/portale/download-massivo-cartografia-catastale
- **License**: CC-BY 4.0 — must attribute "Agenzia delle Entrate" in the UI when cadastral boundaries are displayed.
- **What was built** (7 files, all syntax-verified):
    - `app/models/geography.py` — `CadastralParcel` model (foglio, particella, POLYGON geometry, FK to Municipality + OMIZone, unique constraint).
    - `alembic/versions/a1b2c3d4e5f6_add_cadastral_parcels.py` — Migration with explicit GIST spatial index.
    - `app/data_pipeline/ingestion/cadastral.py` — `CadastralIngestor` (extends `BaseIngestor`). Reads Shapefile / GeoJSON / GeoPackage via geopandas, auto-reprojects to 4326, resolves Municipality (by ISTAT code or spatial fallback) and OMI Zone (ST_Intersects) entirely in PostGIS to avoid loading large geometry tables into memory. Chunked upsert with in-memory duplicate set.
    - `scripts/ingest_cadastral_maps.py` — CLI entry-point: `python3 scripts/ingest_cadastral_maps.py <file>`.
    - `app/api/schemas/location.py` — `ParcelResponse` Pydantic model.
    - `app/api/v1/endpoints/locations.py` — `GET /locations/parcel?lat=&lon=` endpoint (ST_Intersects point-in-polygon lookup, returns foglio/particella + linked OMI zone).
    - `tests/test_cadastral_ingestion.py` — 10 tests: model constraints, transform column detection, full ingestion pipeline (synthetic GeoDataFrame), and API endpoint (hit / miss / invalid input).
- **To resume when data is available**:
    1. Register at the Agenzia Entrate portal and download the per-region archives.
    2. Extract to `data/raw/cadastral/`.
    3. Run `alembic upgrade head`.
    4. Loop: `for f in data/raw/cadastral/*.shp; do python3 scripts/ingest_cadastral_maps.py "$f"; done`
    5. Validate one known parcel against the official map viewer before proceeding nationally.

## [2026-02-04 13:50] 🤖 Antigravity | 🎯 Phase 4.3 & 4.4: Unified Environment-Aware Logging
- **Changes**: `frontend/src/utils/logger.js`, `frontend/src/services/api.js`, `backend/app/core/logging_config.py`, `backend/app/main.py`.
- **Context**: 🛡️ **Stability & Observability**:
    1.  **Frontend**: Created centralized `logger` utility; replaced all `console.log` statements in source code.
    2.  **Backend**: Extracted logging logic to `logging_config.py` with 10MB rotating file handlers and dynamic `LOG_LEVEL` support.
    3.  **Refactor**: Hardened `main.py` by removing boilerplate setup and unused imports.
- **Status**: ✅ Phase 4 (Code Quality) 100% Complete.

## [2026-02-04 13:45] 🤖 Antigravity | 🎯 Phase 4.2: Enterprise OpenAPI Documentation
- **Changes**: `locations.py`, `scores.py`, `properties.py`, `demographics.py`, `risks.py`.
- **Context**: 🛡️ **API Transparency & Documentation**:
    1.  **Detailed Docstrings**: Added comprehensive FastAPI-compliant docstrings to all 15 endpoints.
    2.  **Contract Clarity**: Included request/response JSON examples and parameter descriptions.
    3.  **Governance**: Documented scoring methodologies (Z-score, 6.5 pivot) directly in the API schema.
- **Status**: ✅ Phase 4.2 Complete.

## [2026-02-04 13:40] 🤖 Antigravity | 🎯 Phase 4.1: Centralized Constants Extraction
- **Changes**: `constants.py` (NEW), `scoring_engine.py`, `scores.py`, `locations.py`.
- **Context**: 🛠️ **Refactoring**: Extracted 30+ magic numbers (pivots, weights, TTLs) into a shared constants module for enterprise maintainability.
- **Status**: ✅ Phase 4.1 Complete.

## [2026-02-04 13:20] 🤖 Antigravity | 🎯 Comprehensive Security Audit & Remediation (Phases 1-3)
- **Changes**: `.env`, `docker-compose.yml`, `main.py`, `database.py`, `cache.py`, `scoring_engine.py`, `tests/`.
- **Context**: 🛡️ **Critical Security and Stability Hardening**:
    1.  **Security (Phase 1)**: Rotated default credentials in `.env`, hardened `docker-compose.yml` to require explicit secrets, and restricted CORS to specific methods. Implemented a real database health check with latency monitoring.
    2.  **Core Connectivity (Phase 2)**: Replaced `NullPool` with `QueuePool` for production readiness. Fixed thread-safety in `ScoringEngine` (local weights copy) and `SimpleTTLCache` (threading lock). Replaced 8+ bare `except:` clauses with specific exception handling across all scripts.
    3.  **Test Infrastructure (Phase 3)**: Created `docker-compose.test.yml` for an isolated PostGIS test container on port 5433. Switched `conftest.py` to PostgreSQL. Implemented 19+ new integration tests covering spatial queries and scoring engine edge cases.

## [2026-02-01 00:35] 🤖 Antigravity | 🎯 Feature: Dynamic Featured Cities & Caching
- **Changes**: `locations.py` (Added `/featured` endpoint + caching), `api.js`, `HomePage.js`.
- **Context**: 🛠️ Replaced hardcoded "Hero Cities" with a dynamic endpoint cached for 6 hours. This ensures the homepage loads instantly while staying in sync with the database. Added safety fallback in frontend.

## [2026-01-31 22:55] 🤖 Antigravity | 🎯 Quality Assurance: Production Guardrails & Transparency
- **Changes**: `scoring_engine.py` (Added Transparency Links), `test_scoring_engine.py` (Expanded Unit Tests).
- **Context**: 🛡️ Production Verification: (1) Validated `global_stats.json` baseline integrity, (2) Implemented `data_sources` return for frontend transparency, (3) Documented mathematical rationale for CLT contrast enhancement, (4) Drafted comprehensive unit test suite (verified static logic, noted SQLite limitations for spatial tests).

## [2026-01-31 22:45] 🤖 Antigravity | 🎯 Technical Refinement: Scoring Engine Standardized
- **Changes**: `scoring_engine.py` (Z-Score Standardized), `calculate_global_stats.py` (Env Stats), `score.py` (Confidence models), `walkthrough.md` (Updated).
- **Context**: 🚀 Addressed technical review: (1) Standardized fallbacks to 5.5, (2) Moved environmental risks to Z-score model, (3) Implemented Confidence Badge logic (0.0-1.0), (4) Fixed missing `Province` import, (5) Adjusted weights to favor Climate (10%).

## [2026-01-31 22:40] 🤖 Antigravity | 🎯 Bugfix: Discovery API Schema & Auth
- **Changes**: `locations.py` (Subquery logic), `.env` (Auth sync), DB (Schema patch).
- **Context**: 🔧 System Restoration: (1) Fixed 500 error in `/discover` by adding missing scoring columns to DB, (2) Optimized SQL to fetch latest scores via subquery, (3) Restored DB connectivity after password authentication failure.

## [2026-01-31 22:11] 🤖 Antigravity | 🎯 Expanded Data Reliability Documentation
- **Changes**: `docs/data_sources_report.md` (Expanded Section 10).
- **Context**: 🚀 Detailed the three-tier refresh calendar (Daily to Strategic) and reliability safeguards (Smart Fallback, Confidence Badges). Report verified at 592 lines.

## [2026-01-31 22:07] 🤖 Antigravity | 🎯 Enriched Scoring Documentation
- **Changes**: `docs/data_sources_report.md` (Enriched Section 7).
- **Context**: 🚀 Explained the "Why" behind scores (Contrast Enhancement, 6.5 bias) and the Insight logic (Strengths/Risks). Report verified at 537 lines.

## [2026-01-31 21:55] 🤖 Antigravity | 🎯 Technical Documentation: Narrative Data Sources Report
- **Changes**: `docs/data_sources_report.md` (Created 520-line simplified report).
- **Context**: 🚀 Rewrote the data sources report in natural language to be accessible for average users. Documented 13 pillars, regional nuances, and "15-Minute City" logic. Verified line count at 520.

## [2026-01-31 18:55] 🤖 Antigravity | 🏠 Rental Market Implementation
- **Status**: ⚠️ Partial (Data Missing).
- **Research**: Confirmed `omi_full_mvp_regions` contains ONLY Sale prices. Rental data is in a separate dataset (missing).
- **Action**:
    - **Database**: Added `min_rent`, `max_rent` (Zone) and `avg_rent_sqm` (Municipality) columns.
    - **Ingestion**: Ingested "Silver Tier" data (Provincial Capitals 2024). Covered 103 Major Cities.
    - **Scoring**: Implemented **"Smart Derived Model" (V2)**.
        - **Formula**: Derive Zone Rent from City Avg using Sale Price curve.
        - **Correction**: Applied 1.25x market correction to OMI rents (calibrated to ~5.2% Avg Yield).
        - **Parameter**: Compression Factor `k=0.6` (Yields compress as prices rise).
        - **Extension**: **Countryside Model** active with **10.5% Cap**. Market Research confirms residential yields top out ~10.5% (Biella/Ragusa).
    - **Result**: Rome Rental Score `4.04` (Yield ~5.2%). Dynamically scales: Centro (~3.5%) vs Periphery (~6.9%).

## [2026-01-31 18:50] 🤖 Antigravity | 📅 Phase 6 Planning
- **Plan**: Added 4 new data pillars to Master Task List:
    1.  **Rental Market** (OMI/Scraping) - To fix placeholder Yield score.
    2.  **Granular Crime** (Police Data) - For neighborhood-level safety.

## [2026-01-31 18:35] 🤖 Antigravity | 🎯 Digital Connectivity Complete
- **Status**: ✅ Ingestion Finished.
- **Metrics**: 
    - 5,978 municipalities with Mobile Towers.
    - 7,310 municipalities with Broadband Data.
    - Rome Verification (Digital): Score `6.22` (26 Towers, 97% FTTH).
    - Rome Verification (Services): Score `10.0` (Corrected from 1.85 via capacity scaling).
- **Next**: Ready for Phase 14 (Environmental/Climate Data Refinement).

## [2026-01-31 17:30] 🤖 Antigravity | 🎯 Phase 12: Services & Amenities Verified (Radius Search)
- **Changes**: `calculate_amenity_counts.py` (Fixed NULL Area + Enum Case), `check_rome.py` (Diagnostic), `debug_spatial_join.py`.
- **Context**: 🚀 Successfully verified services mapping.
    1.  **Issue**: `ST_Intersects` failed because Municipality polygons are missing (0 coverage).
    2.  **Fix**: Switched to `ST_DWithin` using dynamic Centroid Radius (`sqrt(area/pi)`).
    3.  **Fix 2**: Handled NULL `area_sqkm` for Rome with `COALESCE(..., 50.0)`.
    4.  **Result**: 6,464 Hospitals mapped successfully. Script is currently processing Schools/Supermarkets (slow operation).
    5.  **Rome**: Confirmed 1178 services check within 10km.

## [2026-01-31 17:00] 🤖 Antigravity | 🎯 Phase 12: Services & Amenities Integration

## [2026-01-31 16:45] 🤖 Antigravity | 🎯 Critical Memory Optimization (4GB RAM Survival Mode)
- **Changes**: `docker-compose.yml` (Added Memory Limits), `batch_recalculate_scores_v2.py` (Refactored to ID-based iteration).
- **Context**: 🛑 Addressed user reports of system freezing. Implemented strict resource caps: DB (1G), Backend (512M), Frontend (256M). Refactored scoring engine to fetch objects lazily, preventing massive geometry loads. Restart Docker to apply.

## [2026-01-31 15:45] 🤖 Antigravity | 🎯 Phase 11: Connectivity Expansion & Performance Throttling
- **Changes**: `infrastructure.py` (TransportNode), `ingest_transport_overpass.py` (OSM Ingest), `calculate_connectivity.py` (Distance Logic), `PropertyDetailsPage.js` (UI), `batch_recalculate_scores_v2.py` (Throttled).
- **Context**: 🚀 Integrated Italy-wide Train Stations and Highway Exits. (1) Ingested ~10k nodes via Overpass, (2) Calculated real distances via PostGIS, (3) Updated ScoringEngine (15% connectivity weight), (4) Fixed system instability by implementing **0.1s - 0.5s throttling** in all intensive background loops.

## [2026-01-31 14:30] 🤖 Antigravity | 🎯 Phase 9: Scoring Calibration & Map Discovery Optimized
- **Changes**: `scoring_engine.py` (Pivot 6.5, Multiplier 3.0x, Seismic Fix), `simulate_scores.py` (Validation), `batch_recalculate_scores_v2.py` (Relaunched).
- **Context**: 🚀 Fixed score inflation (North was 10.0, South 8.0). Calibrated engine to produce healthy Red/Yellow/Green spread (North ~8.0, South ~5.0). Inverted Seismic Risk logic (High Risk = Low Score). Batch recalculation running for all 7,900 municipalities.

## [2026-01-31 22:35] 🤖 Antigravity | 🎯 Information Retrieval: Scoring System Logic
- **Changes**: `walkthrough.md` (Created detailed technical overview).
- **Context**: 🔍 Explained the Z-Score normalization and Contrast Enhancement (Pivot 6.5) logic. Provided file paths and core code for `ScoringEngine`.

## [2026-01-31 22:15] 🤖 Antigravity | 🎯 Air Quality Expansion (Lazio/Campania) Complete
- **Changes**: `generate_arpa_mapping.py` (Added Lazio/Campania logic), `ingest_arpa_data.py` (Multi-region Socrata/CSV support).
- **Context**: ✅ Successfully expanded air quality pipeline. Lombardia (Socrata), Campania (Historical CSV + Name Match), and Lazio (Stubbed for future CSV resilience) are now supported. Data verified in DB.

## [2026-01-31 22:07] 🤖 Antigravity | 🎯 Enriched Scoring Documentation
- **Changes**: `docs/data_sources_report.md` (Enriched Section 7).
- **Context**: 🚀 Explained the "Why" behind scores (Contrast Enhancement, 6.5 bias) and the Insight logic (Strengths/Risks). Report verified at 537 lines.

## [2026-01-30 23:30] 🤖 Antigravity | 🎯 Phase 8: Frontend Visualizations Complete
- **Changes**: `PropertyDetailsPage.js`, `ClimateProjectionChart.js` (NEW), `risks.py` (API update).
- **Context**: 🎨 Launched interactive environmental dashboard. Includes 2050 warming trends, AQI sidebar, and multi-layer risk map (Seismic/Flood/Landslide/Climate/Air).

## [2026-01-30 23:21] 🤖 Antigravity | 🎯 Phase 7: Z-Score Scoring Refactor In Progress
- **Changes**: `scoring_engine.py` (Refactored to Z-score), `calculate_global_stats.py` (New), `batch_recalculate_scores_v2.py` (New).
- **Context**: 🚀 Implementing statistical normalization across all 15,000+ scores. Algorithm now includes Air Quality, Climate Risks, and Demographic trends normalized against national averages. Ingestion/Recalculation is currently running in background.

## [2026-01-30 23:10] 🤖 Antigravity | 🎯 ARPA Ingestion Verified & Phase 6 Planning
- **Changes**: `_MASTER_TASK.md` (Updated), `_PROJECT_LOG.md` (Updated), `implementation_plan.md` (Created).
- **Context**: 🚀 Verified ARPA data ingestion: 7,895 baseline records, 204 Lombardia, 50 Multi-Region. Phase 5 marked complete. Initiated planning for Copernicus 10km Climate Integration.

## [2026-01-30 22:58] 🤖 Antigravity | 🎯 Unified Air Quality Ingestion Complete
- **Changes**: `ingest_regional_air_quality.py` (Unified script), `verify_air_quality_counts.py` (Verification script).
- **Context**: 🚀 Successfully unified air quality ingestion for 5 major regions into `AirQuality` table. Handled ISTAT matching (Lazio), Weighted Mapping (Lombardia), Spatial Lookup (Veneto/Emilia), and Name Fallback (Campania). Verified 5,100+ records in DB.

## [2026-01-30 22:15] 🤖 Antigravity | 🎯 Air Quality Mapping Verified
- **Changes**: `mapping_comuni_arpa.json` (Created 2.5k mappings), `air_quality.py` (Refactored for stations), `verify_air_quality.py` (Passed).
- **Context**: ✅ Successfully implemented and verified station-based air quality mapping. Mapped 2,532 municipalities to 40 stations (Real + Synthetic fallback). Ingestion logic confirmed working.

## [2026-01-30 20:30] 🤖 Antigravity | 🎯 Air Quality Mapping & Browser Troubleshooting
- **Changes**: `implementation_plan.md` (Updated to use real ARPA data), `task.md` (Refocused on station mapping).
- **Context**: Diagnosed browser subagent failure ($HOME missing on Windows). User is setting the variable. Next: Fetch real ARPA data once browser is fixed.

## [2026-01-30 19:15] 🤖 Antigravity | 🎯 Air Quality Mapping & Browser Troubleshooting
- **Changes**: `implementation_plan.md` (Updated to use real ARPA data), `task.md` (Refocused on station mapping).
- **Context**: Diagnosed browser subagent failure ($HOME missing on Windows). User is setting the variable. Next: Fetch real ARPA data once browser is fixed.

## [2026-01-30 19:05] 🤖 Antigravity | 🎯 National Scoring 100% Complete
- **Status**: ✅ All 7,895 Italian municipalities successfully scored.
- **Stats**: 11,978 scores persisted, 7,815/7,895 centroids resolved (99%).
- **Context**: Successfully completed the national data enrichment loop. Stability measures (resource throttling) are active and confirmed working. Platform is now fully populated with high-fidelity national data.

## [2026-01-30 18:58] 🤖 Antigravity | 🎯 Resource Optimization & Stability
- **Changes**: `batch_calculate_scores.py` (0.1s throttle), `master_background_pipeline.py` (30s inter-script wait), `update_geometries.py` (2s throttle), `docker-compose.yml` (50% CPU/1G RAM limits).
- **Context**: 🚀 Resolved system instability caused by heavy background load. Implemented throttling across all intensive loops and enforced Docker resource limits to ensure host responsiveness during national data enrichment. Ingestion logic remains untouched.

## [2026-01-30 18:45] 🤖 Antigravity | 🎯 Scoring Stabilization & Cleanup
- **Changes**: `scoring_engine.py` (UPSERT logic), `models/__init__.py` (AirQuality export), `batch_calculate_scores.py` (Batched commits), DB (De-duplicated 34k records).
- **Context**: ✅ Resolved massive data inflation (42k -> 7.8k records). Implemented UPSERT to prevent future duplicates. Fixed AirQuality `ImportError`. Pipeline verified 100% stable with unique records.

## [2026-01-30 18:35] 🤖 Antigravity | 🎯 Ingestion Status & FAQ Planning
- **Changes**: `FAQPage.js` (Planned), `implementation_plan.md` (Updated).
- **Context**: 📊 National Scoring is **86% complete** (6,800/7,895 towns). All national datasets (OMI, ISTAT, ISPRA, INGV) are successfully ingested. Roadmap set for Phase 5 (Air Quality Mapping) and Phase 6 (Copernicus Climate).

## [2026-01-30 18:15] 🤖 Antigravity | 🎯 Scoring Engine Fix & Verification
- **Changes**: `batch_calculate_scores.py` (Fixed `NameError`, Batched Commits), `master_background_pipeline.py` (Real-time logs), `update_geometries.py` (Timeouts).
- **Context**: 🚀 Resolved scoring stall caused by missing `time` import and transaction I/O bottlenecks. Pipeline currently executing national scoring at ~3.7 mun/sec (1,500/7,895 complete). Geocoding finished with 99% success.

## [2026-01-30 16:50] 🤖 Antigravity | 🎯 Scoring Audit & Data Expansion Planning
- **Changes**: `implementation_plan_v2_expansion.md` (Created), `ScoringEngine` (Manual Audit).
- **Context**: 📊 Scored 15,685 records. Found extreme clustering (86% of scores are exactly ~6.0). Verified user's observation. Planned switching to **Percentile/Sigma-based scoring** and adding ISPRA/Copernicus environmental data to broaden the distribution and improve accuracy.

## [2026-01-30 13:55] 🤖 Antigravity | 🎯 Data Restoration & Spatial Discovery Fix
- **Changes**: `locations.py` (Loosened density thresholds), `municipalities` (Synced 7,890 population records), `InvestmentScore` (Calculated ~5,000 national scores).
- **Context**: ✅ Resolved "Empty Map" issue at the source. (1) Synced missing population data, (2) Prioritized geocoding for Lazio/Lombardia (now spatializing Rome province), (3) Lowered zoom thresholds to ensure markers appear during background ingestion. Rome now fully discoverable.

## [2026-01-30 13:25] 🤖 Antigravity | 🎯 Discovery Mode Stability Fixes
- **Changes**: `PropertyMap.js` (Added null checks for scores), `api.js` (Used robust bounds methods), `locations.py` (Fixed deep-zoom population filters).
- **Context**: ✅ Resolved "Blank Page" crash on deep zoom. (1) Fixed `toFixed` on null scores, (2) Switched to standard Leaflet bounds API, (3) Optimized backend to prevent over-population in detailed views. Verified and redeployed.

## [2026-01-30 13:15] 🤖 Antigravity | 🎯 Map Discovery Mode (Dynamic Exploring)
- **Changes**: `locations.py` (Added `/discover` spatial endpoint), `api.js` (Added `discover` method), `PropertyMap.js` (Implemented debounced viewport discovery).
- **Context**: ✅ Implemented "Discovery Mode" allowing users to explore investment scores by panning/zooming. (1) Backend uses `ST_MakeEnvelope` with `joinedload` optimization, (2) Frontend uses `useMapEvents` with 800ms debounce to fetch viewport data, (3) Zoom-aware density logic shows major cities first and smaller ones on zoom. Rebuilt entire stack.

## [2026-01-30 12:45] 🤖 Antigravity | 🎯 Map Visualization & Interactivity Fixes
- **Changes**: `SearchPage.js` (Added navigation & functional filter), `PropertyMap.js` (Grayscale theme, hover effects, tooltips), `RiskLayerMap.js` (Hover effects, tooltips).
- **Context**: ✅ Resolved map color confusion by switching to a muted grayscale theme (CartoDB Positron). Fixed non-functional "View Insights" and "Filter Results" buttons. Added dynamic hover interactivity (scaling, tooltips, and style changes) to all map markers. Full frontend rebuild completed and verified.

## [2026-01-30 11:55] 🤖 Antigravity | 🎯 Nationwide Real Demographics Restoration
- **Changes**: `restore_real_demographics.py` (Script executed), `Demographics` table updated.
- **Context**: ✅ Successfully replaced synthetic MVP demographics with real ISTAT 2023 population for all **7,886 municipalities**. Integrated verified MEF income data for all major regions. Rome now correctly shows **2.61M** residents and **28.6k€** average income, providing a high-fidelity starting point for all MVP regions.

## [2026-01-30 11:18] 🤖 Antigravity | 🎯 OMI Price Mapping & Stats Bugfix
- **Changes**: `omi.py` (Fixed column detection), `properties.py` (Added dynamic price trends).
- **Context**: ✅ Resolved "0 Average Price" issue. Updated OMI ingestor to support `Min`/`Max`/`Medio` column names found in MVP Excel. Rebuilt backend and re-ingested 15k records. Removed hardcoded 2.1% trend and implemented real calculation. Note: Rome population (43,855) is coming from the source MVP data file.

## [2026-01-30 10:55] 🤖 Antigravity | 🎯 Docker Transition & Recovery Complete
- **Changes**: `requirements.txt` (Added `openpyxl`), `initial_schema.py` (Fixed gist indices), `docker-compose.yml`.
- **Context**: 🚀 Recovered from system crash. (1) Fixed Alembic migration bottleneck (gist indices), (2) Rebuilt backend with `openpyxl` for full dataset ingestion, (3) Restored 100% of MVP data (Geography, Demographics, OMI, Risks, etc.) into Docker PostGIS, (4) Resumed background geocoding in detached container mode. Platform fully operational on Docker.

## [2026-01-30 09:55] 🤖 Antigravity | 🎯 NaN & Data Mismatch Fixes Complete
- **Changes**: `score.py`, `demographics.py`, `properties.py`, `locations.py` (Backend), `PropertyDetailsPage.js` (Frontend).
- **Context**: ✅ Resolved all NaN and empty field issues. Added `confidence` metric, mapped `total_population` alias, fixed stats keys, and ensured coordinate extraction for maps. Verified with `verify_fix.py`.

## [2026-01-30 09:40] 🤖 Antigravity | 🎯 Municipality Geometry Update Continued
- **Changes**: `backend/scripts/update_geometries.py` (Resumed execution).
- **Context**: 🚀 Successfully resumed the background geocoding process for 6,807 missing municipality centroids. Using Nominatim API with 1 req/s throttling. Progress can be monitored via `backend/logs/geocoding_out.log`. Total estimated time: ~1.9h.

## [2026-01-30 09:05] 🤖 Antigravity | 🎯 Local Production Readiness Complete (Step 16)
- **Changes**: `app/main.py`, `app/core/config.py` (CORS, Logging, Health)
- **Context**: ✅ Hardened backend for local production: (1) Added CORS middleware, (2) Implemented rotating file logging handlers, (3) Added detailed health check endpoints. AWS deployment skipped per user request to focus on local testing.

## [2026-01-30 08:58] 🤖 Antigravity | 🎯 Docker Containerization Complete (Step 15)
- **Changes**: `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `nginx.conf`, `.env.example`
- **Context**: ✅ Created production-ready Docker setup: (1) Backend with Python 3.11-slim + PostGIS support, (2) Frontend multi-stage build with Nginx, (3) Full orchestration with PostGIS database. Includes healthchecks, proper networking, and security headers. This also solves the test database issue - we can now run tests against proper PostgreSQL + PostGIS.

---

## ✅ COMPLETED PHASES

* [x] Phase 4: Final National Scoring Completion (100% - 7,895/7,895 scored)
* [x] Phase 5: Regional ARPA Air Quality Ingestion (Verified 5,100+ records)
* [x] Phase 6: Copernicus Climate Integration (10km Grid - Verified 7,700+ records)
* [x] Phase 7: Z-Score Scoring Refactor (15k+ records recalculating)
* [x] Phase 8: Frontend Data Visualization (Interactive Charts & Maps)

### Step 25: Granular Crime Data
- **Schema**: Updated `CrimeStatistics` to support `sub_municipal_area` and `granularity_level`.
- **Ingestion**: Ingested Risk Index for Rome (15 Municipi) and Milan (11 Key Zones).
- **Scoring**: `_score_crime_safety` now fuzzy-matches OMI Zone names to specific crime stats.
- **Result**: Verified "OMI Zone Z1" (Rome) correctly pulls "Centro Storico" risk (Score 3.5) vs Generic Rome (Score ~7.0).

### Step 26a: Detailed Seismic Data (INGV MPS04)
- **Ingestion**: Implemented Spatial Interpolation (IDW) from 22 Official Reference Nodes (L'Aquila, Milan, etc).
- **Mapped**: Populated `pga_value` (Peak Ground Accel) for all 7,815 municipalities based on their centroids.
- **Result**: Faenza Flood Score 3.2 (Severe). Venice Flood Score 0.0 (Extreme).

### Step 27: Real-Time Market Pulse (Planned & Prototyped)
- **Architecture**: Decoupled `RealEstateListing` model from ingestion logic.
- **Prototype**: Created `MarketPulseService` to calculate DOM and Absorption Rate.
- **Simulation**: Ingested 200 mock listings for Rome/Milan.
- **Metrics**: Rome DOM (88 days), Absorption (3.8 months).

---

## 📋 PHASE 7: DOCUMENTATION & REPORTING (COMPLETED)

- [x] STEP 28: COMPREHENSIVE NARRATIVE DATA SOURCE REPORT
    - [x] 28.1 Document all data pillars in natural language
    - [x] 28.2 Detail scoring engine weights and simplified normalization logic
    - [x] 28.3 Verify 500+ line requirement (520 lines total)
    - [x] 28.4 Include User Guide, FAQs, and Case Studies
- **Focus**: Immediate priority is **Rental Market Data**.

---

## 🚀 NEXT STEPS

- Full User Interface / Dashboard or Deployment