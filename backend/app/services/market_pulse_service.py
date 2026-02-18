"""
Market Pulse Service - Real-time listing metrics aggregation.

Calculates:
- Active listings count
- Median days on market (DOM)
- Absorption rate (sold per month)
- Inventory turnover ratio
"""

import statistics
from datetime import date, timedelta
from typing import Dict, Optional
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.listing import RealEstateListing
from app.core.database import SessionLocal


class MarketPulseService:
    """Calculate real-time market metrics from listing data."""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def get_market_pulse(self, municipality_id: int, platform: str = 'casa_it') -> Dict:
        """
        Get complete market pulse metrics for a municipality.
        
        Args:
            municipality_id: Municipality ID
            platform: Source platform
        
        Returns:
            Dict with all metrics
        """
        return {
            'municipality_id': municipality_id,
            'active_listings': self.get_active_listings_count(municipality_id, platform),
            'median_dom': self.get_median_dom(municipality_id, platform),
            'absorption_rate_per_month': self.get_absorption_rate(municipality_id, platform),
            'inventory_months': self.get_inventory_months(municipality_id, platform),
            'avg_price_sqm': self.get_avg_price_sqm(municipality_id, platform),
            'last_updated': date.today().isoformat()
        }
    
    def get_active_listings_count(self, municipality_id: int, platform: str = 'casa_it') -> int:
        """Count of currently active listings."""
        return self.db.query(RealEstateListing).filter(
            and_(
                RealEstateListing.municipality_id == municipality_id,
                RealEstateListing.source_platform == platform,
                RealEstateListing.is_active == True
            )
        ).count()
    
    def get_median_dom(self, municipality_id: int, platform: str = 'casa_it') -> Optional[float]:
        """
        Median days on market for active listings.
        
        Returns:
            Median DOM or None if no data
        """
        dom_values = self.db.query(RealEstateListing.days_on_market).filter(
            and_(
                RealEstateListing.municipality_id == municipality_id,
                RealEstateListing.source_platform == platform,
                RealEstateListing.is_active == True,
                RealEstateListing.days_on_market > 0
            )
        ).all()
        
        if not dom_values:
            return None
        
        dom_list = [d[0] for d in dom_values]
        return round(statistics.median(dom_list), 1)
    
    def get_absorption_rate(self, municipality_id: int, platform: str = 'casa_it', days: int = 30) -> int:
        """
        Number of listings sold (removed) in the last N days.
        
        Args:
            municipality_id: Municipality ID
            platform: Source platform
            days: Lookback period (default 30 days)
        
        Returns:
            Count of listings removed in period
        """
        cutoff_date = date.today() - timedelta(days=days)
        
        return self.db.query(RealEstateListing).filter(
            and_(
                RealEstateListing.municipality_id == municipality_id,
                RealEstateListing.source_platform == platform,
                RealEstateListing.is_active == False,
                RealEstateListing.date_removed >= cutoff_date,
                RealEstateListing.date_removed.isnot(None)
            )
        ).count()
    
    def get_inventory_months(self, municipality_id: int, platform: str = 'casa_it') -> Optional[float]:
        """
        Months of inventory (active / monthly absorption rate).
        
        Lower is better (hot market).
        
        Returns:
            Months of inventory or None
        """
        active = self.get_active_listings_count(municipality_id, platform)
        absorption = self.get_absorption_rate(municipality_id, platform, days=30)
        
        if absorption == 0:
            return None  # No sales data yet
        
        return round(active / absorption, 2)
    
    def get_avg_price_sqm(self, municipality_id: int, platform: str = 'casa_it') -> Optional[float]:
        """
        Average price per sqm for active listings.
        
        Returns:
            Avg price/sqm or None
        """
        result = self.db.query(
            func.avg(RealEstateListing.price_per_sqm)
        ).filter(
            and_(
                RealEstateListing.municipality_id == municipality_id,
                RealEstateListing.source_platform == platform,
                RealEstateListing.is_active == True,
                RealEstateListing.price_per_sqm.isnot(None)
            )
        ).scalar()
        
        return round(result, 2) if result else None
    
    def close(self):
        """Close database connection."""
        self.db.close()
