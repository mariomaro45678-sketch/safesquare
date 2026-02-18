from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Optional
from app.api.schemas.location import (
    LocationSearchRequest,
    LocationSearchResponse,
    MunicipalityResponse,
    OMIZoneResponse,
    CoordinatesResponse,
    ParcelResponse,
    SearchResult,
    DiscoveryResult
)
from app.core.database import get_db
from app.services.geocoding import GeocodingService
from app.models.geography import Municipality, OMIZone, Province, Region, CadastralParcel
from app.models.score import InvestmentScore
from app.models.demographics import Demographics
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_MakeEnvelope, ST_Intersects
from app.core.cache import global_cache
from app.core.constants import CACHE_TTL_FEATURED_LOCATIONS
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
geocoder = GeocodingService()

@router.post("/search", response_model=LocationSearchResponse)
async def search_location(
    request: LocationSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for a location by address, postal code, or municipality name.
    
    Intelligent search engine that resolves user-friendly queries to structured
    geographic entities (ISTAT municipalities and OMI zones). Supports fuzzy matching,
    partial addresses, postal codes, and municipality names. Powered by Nominatim geocoding.
    
    **Request Body:**
    ```json
    {
      "query": "Via del Corso, Roma"
    }
    ```
    
    **Search Capabilities:**
    - Full/partial addresses ("Via Dante 12, Milano")
    - Postal codes ("20121")
    - Municipality names ("Firenze")
    - Neighborhood names ("Navigli, Milano")
    
    **Resolution Process:**
    1. Geocode query to geographic coordinates
    2. Reverse lookup to find ISTAT municipality
    3. Spatial lookup to find matching OMI zone
    4. Return both entities with full metadata
    
    **Example Response:**
    ```json
    {
      "query": "Duomo, Milano",
      "found": true,
      "geocoded": true,
      "coordinates": {
        "latitude": 45.464,
        "longitude": 9.19
      },
      "municipality": {
        "id": 15146,
        "name": "Milano",
        "code": "015146",
        "province_name": "Milano",
        "region_name": "Lombardia",
        "population": 1352000
      },
      "omi_zone": {
        "id": 4821,
        "zone_code": "B1",
        "zone_name": "Centro Storico",
        "municipality_name": "Milano"
      },
      "message": "Location found successfully"
    }
    ```
    
    **Error Responses:**
    - **404**: Location not found or ambiguous query
    - **500**: Geocoding service error
    """
    try:
        result = geocoder.resolve_search_query(db, request.query)
        
        # Convert to response model
        response = LocationSearchResponse(
            query=result['query'],
            found=result['municipality'] is not None,
            geocoded=result.get('geocoded'),
            coordinates=result.get('coordinates'),
        )
        
        # Add municipality if found
        if result['municipality']:
            muni_data = result['municipality']
            # Fetch the full object to get relationships if needed, 
            # or just use the IDs from the geocoder result
            muni = db.query(Municipality).filter(Municipality.id == muni_data['id']).first()
            if muni:
                response.municipality = MunicipalityResponse(
                    id=muni.id,
                    name=muni.name,
                    code=muni.code,
                    province_name=muni.province.name if muni.province else None,
                    region_name=muni.province.region.name if muni.province and muni.province.region else None,
                    population=muni.population,
                    area_sqkm=muni.area_sqkm,
                    postal_codes=muni.postal_codes,
                    coordinates=CoordinatesResponse(
                        latitude=to_shape(muni.centroid).y,
                        longitude=to_shape(muni.centroid).x
                    ) if muni.centroid else None
                )
        
        # Add OMI zone if found
        if result['omi_zone']:
            zone_data = result['omi_zone']
            zone = db.query(OMIZone).filter(OMIZone.id == zone_data['id']).first()
            if zone:
                response.omi_zone = OMIZoneResponse(
                    id=zone.id,
                    zone_code=zone.zone_code,
                    zone_name=zone.zone_name,
                    zone_type=zone.zone_type,
                    municipality_id=zone.municipality_id,
                    municipality_name=zone.municipality.name if zone.municipality else None,
                )
        
        response.message = "Location found successfully" if response.found else "Location not found"
        return response
        
    except Exception as e:
        logger.error(f"Location search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/municipalities/{id}", response_model=MunicipalityResponse)
def get_municipality(id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific municipality by ID.
    
    Returns comprehensive municipal data including administrative classification,
    population statistics, geographic coordinates, and coverage area.
    
    **Parameters:**
    - **id**: Municipality unique identifier (ISTAT code)
    
    **Returns:**
    - Complete municipality profile with nested relationships
    - Centroid coordinates for map visualization
    - Postal code ranges
    
    **Example Response:**
    ```json
    {
      "id": 58091,
      "name": "Roma",
      "code": "058091",
      "province_name": "Roma",
      "region_name": "Lazio",
      "population": 2761000,
      "area_sqkm": 1285.31,
      "postal_codes": ["00118", "00119", "..."],
      "coordinates": {
        "latitude": 41.9028,
        "longitude": 12.4964
      }
    }
    ```
    
    **Error Responses:**
    - **404**: Municipality not found
    """
    municipality = db.query(Municipality).filter(Municipality.id == id).first()
    if not municipality:
        raise HTTPException(status_code=404, detail="Municipality not found")
    
    # Extract coordinates from centroid
    coords = None
    if municipality.centroid:
        point = to_shape(municipality.centroid)
        coords = CoordinatesResponse(latitude=point.y, longitude=point.x)
    
    return MunicipalityResponse(
        id=municipality.id,
        name=municipality.name,
        code=municipality.code,
        province_name=municipality.province.name if municipality.province else None,
        province_code=municipality.province.code if municipality.province else None,
        region_name=municipality.province.region.name if municipality.province and municipality.province.region else None,
        population=municipality.population,
        altitude=None, # Not currently tracked in DB
        area_sqkm=municipality.area_sqkm,
        postal_codes=municipality.postal_codes,
        coordinates=coords
    )

@router.get("/municipalities", response_model=List[MunicipalityResponse])
async def list_municipalities(
    region_id: Optional[int] = Query(None),
    province_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List municipalities with optional regional or provincial filtering.
    
    Paginated endpoint for browsing municipalities. Supports hierarchical filtering
    by region or province. Useful for building navigation menus, dropdowns,
    and directory listings.
    
    **Parameters:**
    - **region_id** (optional): Filter by region (e.g., Lombardia)
    - **province_id** (optional): Filter by province (e.g., Milano)
    - **limit**: Max results per page (default: 100, max: 1000)
    - **offset**: Pagination offset (default: 0)
    
    **Filtering Logic:**
    - If province_id provided: Returns only municipalities in that province
    - If region_id provided: Returns ALL municipalities in ALL provinces of that region
    - If neither provided: Returns all municipalities (use pagination!)
    
    **Example Request:**
    ```
    GET /municipalities?region_id=3&limit=50&offset=0
    ```
    
    **Example Response:**
    ```json
    [
      {
        "id": 15146,
        "name": "Milano",
        "province_name": "Milano",
        "region_name": "Lombardia",
        "population": 1352000
      },
      {...}
    ]
    ```
    
    **Use Cases:**
    - Populate region/province selection dropdowns
    - Build browsable municipal directory
    - Implement autocomplete typeahead
    """
    query = db.query(Municipality)
    if province_id:
        query = query.filter(Municipality.province_id == province_id)
    elif region_id:
        from app.models.geography import Province
        query = query.join(Province).filter(Province.region_id == region_id)
        
    municipalities = query.offset(offset).limit(limit).all()
    
    results = []
    for m in municipalities:
        coords = None
        if m.centroid:
            point = to_shape(m.centroid)
            coords = CoordinatesResponse(latitude=point.y, longitude=point.x)
        
        results.append(MunicipalityResponse(
            id=m.id,
            name=m.name,
            code=m.code,
            province_name=m.province.name if m.province else None,
            region_name=m.province.region.name if m.province and m.province.region else None,
            population=m.population,
            area_sqkm=m.area_sqkm,
            postal_codes=m.postal_codes,
            coordinates=coords
        ))
    
    return results

@router.get("/discover", response_model=List[MunicipalityResponse])
async def discover_locations(
    min_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lat: float = Query(...),
    max_lon: float = Query(...),
    zoom: int = Query(6),
    db: Session = Depends(get_db)
):
    """
    Discover municipalities within a bounding box (viewport-based exploration).
    
    Dynamic spatial discovery endpoint for interactive map exploration. Returns
    municipalities visible in the current map viewport, with density adjustments
    based on zoom level. Optimized for real-time panning/zooming.
    
    **Parameters:**
    - **min_lat**: Bounding box minimum latitude (south)
    - **min_lon**: Bounding box minimum longitude (west)
    - **max_lat**: Bounding box maximum latitude (north)
    - **max_lon**: Bounding box maximum longitude (east)
    - **zoom**: Map zoom level (6-18, default: 6)
    
    **Zoom-Based Density Filtering:**
    - **Zoom < 7**: Only cities > 100k population (major metros)
    - **Zoom 7-8**: Cities > 50k (regional centers)
    - **Zoom 9-10**: Cities > 5k (towns)
    - **Zoom 11-12**: Cities > 1k (villages)
    - **Zoom > 12**: All municipalities
    
    **Score Prioritization:**
    Results are ordered by investment score (highest first) to highlight
    the best opportunities in the visible area.
    
    **Example Request:**
    ```
    GET /discover?min_lat=45.0&min_lon=9.0&max_lat=45.5&max_lon=9.5&zoom=8
    ```
    
    **Example Response:**
    ```json
    [
      {
        "id": 15146,
        "name": "Milano",
        "investment_score": 8.2,
        "coordinates": {...}
      },
      {...}
    ]
    ```
    
    **Performance:**
    - Max 150 results per request (prevents UI lag)
    - Spatial index enabled (fast bounding box queries)
    - Debounce recommended on frontend (800ms)
    """
    from sqlalchemy import func
    from geoalchemy2.functions import ST_MakeEnvelope

    # Create bounding box envelope
    # ST_MakeEnvelope(xmin, ymin, xmax, ymax, srid)
    bbox = ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)

    from app.models.score import InvestmentScore
    from datetime import date
    
    # Base query for municipalities with a centroid in the bbox
    # Joinedload investment scores to avoid N+1 queries
    # Subquery to find the latest calculation date for each municipality
    latest_dates_subquery = db.query(
        InvestmentScore.municipality_id,
        func.max(InvestmentScore.calculation_date).label('max_date')
    ).group_by(InvestmentScore.municipality_id).subquery()
    
    # Base query for municipalities with a centroid in the bbox
    # Join with the subquery and then with InvestmentScore to get the actual score data
    query = db.query(Municipality, InvestmentScore.overall_score).outerjoin(
        latest_dates_subquery,
        Municipality.id == latest_dates_subquery.c.municipality_id
    ).outerjoin(
        InvestmentScore, 
        (Municipality.id == InvestmentScore.municipality_id) & 
        (InvestmentScore.calculation_date == latest_dates_subquery.c.max_date) &
        (InvestmentScore.omi_zone_id == None)
    ).filter(func.ST_Within(Municipality.centroid, bbox))

    # Zoom-based density logic (Population-based filtering) 
    # BUT always include high-scoring locations (>= 7.0) regardless of population
    high_score_filter = (InvestmentScore.overall_score >= 7.0)

    if zoom < 7:
        query = query.filter((Municipality.population > 100000) | high_score_filter)
    elif zoom < 9:
        query = query.filter((Municipality.population > 50000) | high_score_filter)
    elif zoom < 11:
        query = query.filter((Municipality.population > 5000) | high_score_filter)
    elif zoom < 13:
        query = query.filter((Municipality.population > 1000) | (Municipality.population == None) | high_score_filter)
    else:
        query = query.filter((Municipality.population > 100) | (Municipality.population == None) | high_score_filter)
    
    # CRITICAL: Prioritize Green scores (7+) and then high scores in general
    # This ensures "First Impression" shows high-potential spots first.
    query = query.order_by(InvestmentScore.overall_score.desc().nulls_last())
    
    # Limit results to prevent UI lag
    municipalities_data = query.limit(150).all()

    results = []
    for m, score in municipalities_data:
        coords = None
        if m.centroid:
            point = to_shape(m.centroid)
            coords = CoordinatesResponse(latitude=point.y, longitude=point.x)
        
        results.append(MunicipalityResponse(
            id=m.id,
            name=m.name,
            code=m.code,
            province_name=m.province.name if m.province else None,
            region_name=m.province.region.name if m.province and m.province.region else None,
            population=m.population,
            area_sqkm=m.area_sqkm,
            postal_codes=m.postal_codes,
            investment_score=score,
            coordinates=coords
        ))
    
    return results

@router.get("/featured", response_model=List[MunicipalityResponse])
def get_featured_locations(db: Session = Depends(get_db)):
    """
    Get curated featured locations for homepage showcase.
    
    Returns top-rated investment municipalities (high scores + large population)
    for prominent display on the application homepage. Results are cached for
    6 hours to optimize performance for high-traffic pages.
    
    **Selection Criteria:**
    - Population > 50,000 (major cities only)
    - Investment score available (calculated)
    - Centroid coordinates available (for map display)
    - Ordered by descending investment score
    
    **Returns:**
    - Top 10 municipalities meeting criteria
    - Full municipal data + coordinates
    - Latest investment scores
    
    **Caching:**
    - **TTL**: 6 hours (21600 seconds)
    - **Strategy**: In-memory cache (fast)
    - **Key**: "featured_cities_v1"
    
    **Example Response:**
    ```json
    [
      {
        "id": 15146,
        "name": "Milano",
        "province_name": "Milano",
        "region_name": "Lombardia",
        "score": 8.2,
        "coordinates": {
          "lat": 45.464,
          "lng": 9.19
        }
      },
      {...}
    ]
    ```
    
    **Use Cases:**
    - Homepage "Featured Cities" carousel
    - Quick navigation to high-opportunity markets
    - Marketing/promotional content
    """
    from app.core.cache import global_cache
    
    CACHE_KEY = "featured_cities_v1"
    # 6 hours in seconds = 6 * 60 * 60 = 21600
    TTL_SECONDS = 21600
    
    # Try cache first
    cached_data = global_cache.get(CACHE_KEY)
    if cached_data:
        return cached_data
        
    # If not in cache, query top-scored municipalities
    from app.models.score import InvestmentScore
    from sqlalchemy import func
    
    # Subquery to find the latest calculation date for each municipality
    latest_dates_subquery = db.query(
        InvestmentScore.municipality_id,
        func.max(InvestmentScore.calculation_date).label('max_date')
    ).group_by(InvestmentScore.municipality_id).subquery()
    
    # Query municipalities with population > 50k, ordered by investment score
    query = db.query(Municipality, InvestmentScore.overall_score).outerjoin(
        latest_dates_subquery,
        Municipality.id == latest_dates_subquery.c.municipality_id
    ).outerjoin(
        InvestmentScore, 
        (Municipality.id == InvestmentScore.municipality_id) & 
        (InvestmentScore.calculation_date == latest_dates_subquery.c.max_date) &
        (InvestmentScore.omi_zone_id == None)
    ).filter(
        Municipality.population > 50000,
        Municipality.centroid != None
    ).order_by(InvestmentScore.overall_score.desc().nulls_last()).limit(10)
    
    municipalities_data = query.all()
    
    results = []
    for m, score in municipalities_data:
        coords = None
        if m.centroid:
            point = to_shape(m.centroid)
            coords = CoordinatesResponse(latitude=point.y, longitude=point.x)
        
        results.append(MunicipalityResponse(
            id=m.id,
            name=m.name,
            code=m.code,
            province_name=m.province.name if m.province else None,
            region_name=m.province.region.name if m.province and m.province.region else None,
            population=m.population,
            area_sqkm=m.area_sqkm,
            postal_codes=m.postal_codes,
            investment_score=score,
            coordinates=coords
        ))
    
    # Cache the results
    global_cache.set(CACHE_KEY, results, TTL_SECONDS)
        
    return results

@router.get("/municipalities/{id}/omi-zones", response_model=List[OMIZoneResponse])
def get_municipality_omi_zones(id: int, db: Session = Depends(get_db)):
    """
    Get all OMI zones within a municipality.
    
    Returns the complete list of OMI (Osservatorio del Mercato Immobiliare) zones
    for a given municipality. OMI zones represent distinct urban areas with unique
    real estate market characteristics. Essential for granular investment analysis.
    
    **Parameters:**
    - **id**: Municipality unique identifier
    
    **Returns:**
    - Array of OMI zones with codes, names, and types
    - Zone classifications (central, semi-central, peripheral, suburban, etc.)
    
    **Example Response:**
    ```json
    [
      {
        "id": 4821,
        "zone_code": "B1",
        "zone_name": "Centro Storico",
        "zone_type": "central",
        "municipality_id": 15146,
        "municipality_name": "Milano"
      },
      {
        "id": 4822,
        "zone_code": "C1",
        "zone_name": "Navigli",
        "zone_type": "semi-central",
        "municipality_id": 15146,
        "municipality_name": "Milano"
      }
    ]
    ```
    
    **Use Cases:**
    - Neighborhood-level investment analysis
    - Comparing zones within same municipality
    - Detailed property price mapping
    """
    zones = db.query(OMIZone).filter(OMIZone.municipality_id == id).all()
    return zones


@router.get("/parcel", response_model=ParcelResponse)
def get_parcel_at(
    lat: float = Query(..., ge=-90, le=90, description="Latitude (WGS84)"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude (WGS84)"),
    db: Session = Depends(get_db)
):
    """
    Identify the cadastral parcel that contains a given coordinate.

    Performs a PostGIS ST_Intersects query against ingested Cartografia Catastale
    data (Agenzia delle Entrate, CC-BY 4.0).  Returns the parcel's foglio /
    particella identifiers and, when available, the pre-calculated linked OMI zone
    for instant price-range lookup.

    **Parameters:**
    - **lat**: Latitude in WGS84
    - **lon**: Longitude in WGS84

    **Example:**
    ```
    GET /locations/parcel?lat=41.9028&lon=12.4964
    ```

    **Error Responses:**
    - **404**: No cadastral parcel found at the given coordinates (data may not
      be ingested for that municipality yet).
    """
    from sqlalchemy import func

    point = func.ST_MakePoint(lon, lat)
    parcel = (
        db.query(CadastralParcel)
        .filter(func.ST_Intersects(CadastralParcel.geometry, func.ST_SetSRID(point, 4326)))
        .first()
    )

    if not parcel:
        raise HTTPException(status_code=404, detail="No cadastral parcel found at the given coordinates")

    linked_omi: OMIZoneResponse | None = None
    if parcel.omi_zone:
        linked_omi = OMIZoneResponse(
            id=parcel.omi_zone.id,
            zone_code=parcel.omi_zone.zone_code,
            zone_name=parcel.omi_zone.zone_name,
            zone_type=parcel.omi_zone.zone_type,
            municipality_id=parcel.omi_zone.municipality_id,
            municipality_name=parcel.municipality.name if parcel.municipality else None,
        )

    return ParcelResponse(
        foglio=parcel.foglio,
        particella=parcel.particella,
        municipality_id=parcel.municipality_id,
        municipality_name=parcel.municipality.name if parcel.municipality else None,
        linked_omi_zone=linked_omi,
    )
