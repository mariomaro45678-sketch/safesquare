from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class RealEstateListing(Base, TimestampMixin):
    """
    Individual Property Listing (Active or Historical).
    Used to calculate Real-Time Market Pulse metrics.
    """
    __tablename__ = "real_estate_listings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Link to our geography
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    omi_zone_id = Column(Integer, ForeignKey("omi_zones.id"), nullable=True) # If we can map it
    
    # Listing Details
    source_id = Column(String(100), unique=True, index=True) # e.g. "imm_12345"
    source_platform = Column(String(50)) # "immobiliare", "idealista"
    listing_type = Column(String(20), default='sale') # "sale", "rent"
    url = Column(String(500))
    
    title = Column(String(200))
    price = Column(Float)
    size_sqm = Column(Integer)
    price_per_sqm = Column(Float)
    
    # Lifecycle
    date_posted = Column(Date)
    date_removed = Column(Date, nullable=True) # Null = Active
    is_active = Column(Boolean, default=True)
    
    # Metrics
    days_on_market = Column(Integer, default=0)
    views = Column(Integer, default=0)
    
    # Relationships
    municipality = relationship("Municipality")
    omi_zone = relationship("OMIZone")

    def __repr__(self):
        return f"<Listing {self.source_id} €{self.price}>"
