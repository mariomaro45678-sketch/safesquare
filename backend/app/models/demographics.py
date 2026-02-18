from sqlalchemy import Column, Integer, ForeignKey, Float, Date, JSON, String
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Demographics(Base, TimestampMixin):
    """Demographic and socioeconomic data from ISTAT"""
    __tablename__ = "demographics"
    
    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    
    # Time period
    year = Column(Integer, nullable=False)
    reference_date = Column(Date)
    
    # Population data
    total_population = Column(Integer)
    population_density = Column(Float)  # per sqkm
    male_population = Column(Integer)
    female_population = Column(Integer)
    
    # Age distribution
    age_0_14 = Column(Integer)
    age_15_64 = Column(Integer)
    age_65_plus = Column(Integer)
    median_age = Column(Float)
    
    # Households
    total_households = Column(Integer)
    avg_household_size = Column(Float)
    
    # Economic indicators
    avg_income_euro = Column(Float)
    unemployment_rate = Column(Float)
    
    # Migration
    immigration_rate = Column(Float)
    emigration_rate = Column(Float)
    
    # Education
    higher_education_rate = Column(Float)  # % with university degree
    
    # Relationships
    municipality = relationship("Municipality", back_populates="demographics")
    
    def __repr__(self):
        return f"<Demographics {self.municipality_id} {self.year}>"


class CrimeStatistics(Base, TimestampMixin):
    """Crime data from ISTAT"""
    __tablename__ = "crime_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    
    # Time period
    year = Column(Integer, nullable=False)
    
    # Granularity (Phase 6b)
    granularity_level = Column(String(50), default='municipality') # 'municipality', 'sub_municipal'
    sub_municipal_area = Column(String(100), nullable=True) # e.g. "Municipio I", "NIL Duomo"
    
    # Crime counts (per 1000 residents)
    total_crimes_per_1000 = Column(Float)
    violent_crimes_per_1000 = Column(Float)
    property_crimes_per_1000 = Column(Float)
    
    # Crime index (normalized 0-100, higher = more crime)
    crime_index = Column(Float)
    
    # Granular rates (Real Estate sensitive)
    # burglary_rate = Column(Float)
    # vandalism_rate = Column(Float)
    # theft_rate = Column(Float)
    
    # Additional info
    # crime_metadata = Column(JSON)
    
    # Relationships
    municipality = relationship("Municipality", back_populates="crime_stats")
    
    def __repr__(self):
        return f"<CrimeStats {self.municipality_id} {self.year}>"
