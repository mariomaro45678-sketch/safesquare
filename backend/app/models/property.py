from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, Enum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum

class PropertyType(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    AGRICULTURAL = "agricultural"

class TransactionType(str, enum.Enum):
    SALE = "sale"
    RENT = "rent"

class PropertyPrice(Base, TimestampMixin):
    """Property price data from OMI"""
    __tablename__ = "property_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    omi_zone_id = Column(Integer, ForeignKey("omi_zones.id"), nullable=False)
    
    # Time period
    year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)  # 1 or 2
    reference_date = Column(Date, nullable=False)
    
    # Property characteristics
    property_type = Column(Enum(PropertyType), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    property_state = Column(String(50))  # e.g., "Ottimo", "Normale", "Scarso"
    
    # Price data (€/sqm)
    min_price = Column(Float)
    max_price = Column(Float)
    avg_price = Column(Float, nullable=False)
    
    # Rental Data (New Phase 6)
    min_rent = Column(Float, nullable=True) # Monthly Rent / Sqm (or Annual if source differs)
    max_rent = Column(Float, nullable=True)
    avg_rent = Column(Float, nullable=True)
    
    # Market indicators
    rental_yield = Column(Float)  # Calculated rental yield percentage
    price_change_yoy = Column(Float)  # Year-over-year change percentage
    
    # Relationships
    omi_zone = relationship("OMIZone", back_populates="property_prices")
    
    def __repr__(self):
        return f"<PropertyPrice {self.omi_zone_id} {self.year}S{self.semester}>"
