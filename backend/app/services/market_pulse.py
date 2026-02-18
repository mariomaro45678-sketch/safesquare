from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.listing import RealEstateListing
from datetime import date, timedelta

class MarketPulseService:
    @staticmethod
    def get_metrics(db: Session, municipality_id: int):
        """
        Calculates dynamic market metrics from listings.
        """
        # Active Listings
        active_query = db.query(RealEstateListing).filter(
            RealEstateListing.municipality_id == municipality_id,
            RealEstateListing.is_active == True
        )
        active_count = active_query.count()
        
        # Avg Price (Active)
        avg_price_sqm = db.query(func.avg(RealEstateListing.price_per_sqm)).filter(
            RealEstateListing.municipality_id == municipality_id,
            RealEstateListing.is_active == True
        ).scalar() or 0
        
        # DOM (Days On Market) - Average for Active Listings
        avg_dom_active = db.query(func.avg(RealEstateListing.days_on_market)).filter(
            RealEstateListing.municipality_id == municipality_id,
            RealEstateListing.is_active == True
        ).scalar() or 0
        
        # SOLD Metrics (Last 90 Days)
        cutoff = date.today() - timedelta(days=90)
        sold_query = db.query(RealEstateListing).filter(
            RealEstateListing.municipality_id == municipality_id,
            RealEstateListing.is_active == False,
            RealEstateListing.date_removed >= cutoff
        )
        sold_count = sold_query.count()
        
        avg_dom_sold = db.query(func.avg(RealEstateListing.days_on_market)).filter(
            RealEstateListing.municipality_id == municipality_id,
            RealEstateListing.is_active == False,
            RealEstateListing.date_removed >= cutoff
        ).scalar() or 0
        
        # Absorption Rate (Monthly)
        # Sales per month / Active Inventory
        # Sold 90 days = X -> Sales/Month = X/3
        sales_per_month = sold_count / 3.0
        absorption_rate_months = (active_count / sales_per_month) if sales_per_month > 0 else 99.0
        
        return {
            "active_listings": active_count,
            "sold_last_90d": sold_count,
            "avg_price_sqm": round(avg_price_sqm, 2),
            "avg_dom_active": round(avg_dom_active, 1),
            "avg_dom_sold": round(avg_dom_sold, 1),
            "absorption_months": round(absorption_rate_months, 1) # Months to sell current inventory
        }
