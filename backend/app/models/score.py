from sqlalchemy import Column, Integer, ForeignKey, Float, Date, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class InvestmentScore(Base, TimestampMixin):
    """Calculated investment scores (cached)"""
    __tablename__ = "investment_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"))
    omi_zone_id = Column(Integer, ForeignKey("omi_zones.id"))
    
    # Scoring
    overall_score = Column(Float, nullable=False)  # 1-10
    calculation_date = Column(Date, nullable=False)
    
    # Component scores (0-10 each)
    price_trend_score = Column(Float)
    affordability_score = Column(Float)
    rental_yield_score = Column(Float)
    demographics_score = Column(Float)
    crime_score = Column(Float)
    seismic_risk_score = Column(Float)
    flood_risk_score = Column(Float)
    landslide_risk_score = Column(Float)
    climate_risk_score = Column(Float)
    connectivity_score = Column(Float)
    digital_connectivity_score = Column(Float)
    services_score = Column(Float)
    air_quality_score = Column(Float)
    confidence_score = Column(Float) # 0-1 Confidence Badge
    
    # Weights used in calculation
    weights = Column(JSON)
    
    # Supporting data
    score_metadata = Column(JSON)
    
    # Relationships
    municipality = relationship("Municipality", back_populates="investment_scores")
    omi_zone = relationship("OMIZone", back_populates="investment_scores")
    
    def __repr__(self):
        zone_id = self.omi_zone_id or self.municipality_id
        return f"<InvestmentScore {zone_id}: {self.overall_score:.1f}>"
