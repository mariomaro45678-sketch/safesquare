"""
API endpoints for real estate listings and market pulse data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.listing import RealEstateListing
from app.services.market_pulse_service import MarketPulseService


router = APIRouter(prefix="/listings", tags=["listings"])


# Response Models
class MarketPulseResponse(BaseModel):
    """Market pulse metrics for a municipality."""
    municipality_id: int
    municipality_name: Optional[str] = None
    active_listings: int
    median_dom: Optional[float]
    absorption_rate_per_month: int
    inventory_months: Optional[float]
    avg_price_sqm: Optional[float]
    last_updated: str
    
    class Config:
        from_attributes = True


class ListingPreview(BaseModel):
    """Listing preview for recent listings endpoint."""
    source_id: str
    title: str
    price: Optional[float]
    size_sqm: Optional[int]
    price_per_sqm: Optional[float]
    days_on_market: int
    url: str
    
    class Config:
        from_attributes = True


class ScraperStatusResponse(BaseModel):
    """Scraper health/status information."""
    last_scrape_completed: Optional[str]
    total_listings_scraped: int
    active_listings: int
    success_rate: Optional[float]
    status: str


@router.get("/market-pulse/{municipality_id}", response_model=MarketPulseResponse)
async def get_market_pulse(
    municipality_id: int,
    platform: Optional[str] = Query(default=None, description="Filter by source platform (casa_it, market_simulator, etc). If not provided, uses all platforms."),
    db: Session = Depends(get_db)
):
    """
    Get real-time market pulse metrics for a municipality.

    **Metrics Included:**
    - Active listings count
    - Median days on market (DOM)
    - Absorption rate (sold per month)
    - Inventory months (supply/demand ratio)
    - Average price per sqm

    **Example Response:**
    ```json
    {
      "municipality_id": 1234,
      "municipality_name": "Roma",
      "active_listings": 4523,
      "median_dom": 88.0,
      "absorption_rate_per_month": 156,
      "inventory_months": 3.8,
      "avg_price_sqm": 4250.50,
      "last_updated": "2026-02-04"
    }
    ```
    """
    # If no platform specified, calculate metrics across all platforms
    if platform is None:
        # Direct query for all platforms
        from sqlalchemy import func
        from app.models.listing import RealEstateListing
        from datetime import date, timedelta
        import statistics

        # Active listings
        active_count = db.query(func.count(RealEstateListing.id)).filter(
            RealEstateListing.municipality_id == municipality_id,
            RealEstateListing.is_active == True
        ).scalar() or 0

        # Median DOM
        dom_values = db.query(RealEstateListing.days_on_market).filter(
            RealEstateListing.municipality_id == municipality_id,
            RealEstateListing.is_active == True,
            RealEstateListing.days_on_market > 0
        ).all()
        median_dom = round(statistics.median([d[0] for d in dom_values]), 1) if dom_values else None

        # Absorption rate (30 days)
        cutoff = date.today() - timedelta(days=30)
        absorption = db.query(func.count(RealEstateListing.id)).filter(
            RealEstateListing.municipality_id == municipality_id,
            RealEstateListing.is_active == False,
            RealEstateListing.date_removed >= cutoff
        ).scalar() or 0

        # Inventory months
        inventory = round(active_count / absorption, 2) if absorption > 0 else None

        # Avg price/sqm
        avg_price = db.query(func.avg(RealEstateListing.price_per_sqm)).filter(
            RealEstateListing.municipality_id == municipality_id,
            RealEstateListing.is_active == True,
            RealEstateListing.price_per_sqm.isnot(None)
        ).scalar()
        avg_price = round(avg_price, 2) if avg_price else None

        metrics = {
            'municipality_id': municipality_id,
            'active_listings': active_count,
            'median_dom': median_dom,
            'absorption_rate_per_month': absorption,
            'inventory_months': inventory,
            'avg_price_sqm': avg_price,
            'last_updated': date.today().isoformat()
        }
    else:
        service = MarketPulseService()
        try:
            metrics = service.get_market_pulse(municipality_id, platform)
        finally:
            service.close()

    # Get municipality name
    from app.models.geography import Municipality
    municipality = db.query(Municipality).filter(Municipality.id == municipality_id).first()

    if municipality:
        metrics['municipality_name'] = municipality.name

    return metrics


@router.get("/recent/{municipality_id}", response_model=List[ListingPreview])
async def get_recent_listings(
    municipality_id: int,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """
    Get recent active listings for a municipality.
    
    **Parameters:**
    - `municipality_id`: Municipality ID
    - `limit`: Max number of listings to return (default: 20, max: 100)
    
    **Returns:**
    List of listing previews ordered by most recently posted.
    """
    listings = db.query(RealEstateListing).filter(
        RealEstateListing.municipality_id == municipality_id,
        RealEstateListing.is_active == True
    ).order_by(
        RealEstateListing.date_posted.desc()
    ).limit(limit).all()
    
    return listings


@router.get("/scraper-status", response_model=ScraperStatusResponse)
async def get_scraper_status(db: Session = Depends(get_db)):
    """
    Get scraper health and status information.
    
    **Returns:**
    - Last successful scrape timestamp
    - Total listings in database
    - Active listings count
    - Overall success rate
    - Status (healthy/warning/error)
    """
    from sqlalchemy import func
    from app.models.listing import RealEstateListing
    
    total = db.query(func.count(RealEstateListing.id)).scalar() or 0
    active = db.query(func.count(RealEstateListing.id)).filter(
        RealEstateListing.is_active == True
    ).scalar() or 0
    
    # Get most recent listing date as proxy for last scrape
    last_listing = db.query(RealEstateListing).order_by(
        RealEstateListing.created_at.desc()
    ).first()
    
    last_scrape = last_listing.created_at.isoformat() if last_listing else None
    
    # Determine status
    if active > 0:
        status = "healthy"
    elif total > 0:
        status = "warning"  # Have data but nothing active
    else:
        status = "no_data"
    
    return {
        "last_scrape_completed": last_scrape,
        "total_listings_scraped": total,
        "active_listings": active,
        "success_rate": None,  # Would track from scraper logs
        "status": status
    }
