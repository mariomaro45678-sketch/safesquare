from sqlalchemy import Column, Integer, String, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class SeismicRisk(Base, TimestampMixin):
    """Seismic hazard data from INGV"""
    __tablename__ = "seismic_risk"
    
    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    
    # Classification
    seismic_zone = Column(Integer)  # 1-4 (1=highest risk, 4=lowest)
    peak_ground_acceleration = Column(Float)  # PGA value
    
    # Risk indicators
    hazard_level = Column(String(20))  # "Very High", "High", "Medium", "Low"
    risk_score = Column(Float)  # Normalized 0-100
    
    # Historical data
    historical_earthquakes_count = Column(Integer)
    max_historical_magnitude = Column(Float)
    
    # Additional data
    risk_metadata = Column(JSON)
    
    # Relationships
    municipality = relationship("Municipality", back_populates="seismic_risks")
    
    def __repr__(self):
        return f"<SeismicRisk {self.municipality_id} Zone{self.seismic_zone}>"


class FloodRisk(Base, TimestampMixin):
    """Flood hazard data from ISPRA"""
    __tablename__ = "flood_risk"
    
    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    
    # Hazard levels
    high_hazard_area_pct = Column(Float)  # % of municipality in high hazard zone
    medium_hazard_area_pct = Column(Float)
    low_hazard_area_pct = Column(Float)
    
    # Risk indicators
    risk_level = Column(String(20))  # "Very High", "High", "Medium", "Low", "Negligible"
    risk_score = Column(Float)  # Normalized 0-100
    
    # Exposure
    population_exposed = Column(Integer)
    buildings_exposed = Column(Integer)
    
    # Additional data
    flood_types = Column(JSON)  # River, coastal, pluvial
    risk_metadata = Column(JSON)
    
    # Relationships
    municipality = relationship("Municipality", back_populates="flood_risks")
    
    def __repr__(self):
        return f"<FloodRisk {self.municipality_id}>"


class LandslideRisk(Base, TimestampMixin):
    """Landslide hazard data from ISPRA"""
    __tablename__ = "landslide_risk"
    
    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    
    # Hazard levels
    high_hazard_area_pct = Column(Float)
    medium_hazard_area_pct = Column(Float)
    low_hazard_area_pct = Column(Float)
    
    # Risk indicators
    risk_level = Column(String(20))
    risk_score = Column(Float)  # Normalized 0-100
    
    # Exposure
    population_exposed = Column(Integer)
    
    # Additional data
    landslide_count = Column(Integer)  # Historical landslides
    risk_metadata = Column(JSON)
    
    # Relationships
    municipality = relationship("Municipality", back_populates="landslide_risks")
    
    def __repr__(self):
        return f"<LandslideRisk {self.municipality_id}>"


class ClimateProjection(Base, TimestampMixin):
    """Climate projections from Copernicus"""
    __tablename__ = "climate_projections"
    
    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    
    # Projection details
    scenario = Column(String(20))  # e.g., "RCP4.5", "RCP8.5"
    target_year = Column(Integer)  # e.g., 2050, 2100
    
    # Temperature projections (°C change from baseline)
    avg_temp_change = Column(Float)
    max_temp_change = Column(Float)
    heatwave_days_increase = Column(Integer)
    
    # Precipitation projections (% change)
    avg_precipitation_change = Column(Float)
    extreme_rainfall_increase = Column(Float)
    drought_risk_increase = Column(Float)
    
    # Sea level (for coastal areas, cm)
    sea_level_rise_cm = Column(Float)
    
    # Flood risk increase
    flood_risk_multiplier = Column(Float)  # e.g., 1.5 = 50% increase
    
    # Additional data
    projection_metadata = Column(JSON)
    
    # Relationships
    municipality = relationship("Municipality", back_populates="climate_projections")
    
    def __repr__(self):
        return f"<ClimateProjection {self.municipality_id} {self.scenario} {self.target_year}>"


class AirQuality(Base, TimestampMixin):
    """Air quality data from ISPRA/Regional ARPAs"""
    __tablename__ = "air_quality"
    
    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    
    # Concentrations (annual average, μg/m³)
    pm25_avg = Column(Float)
    pm10_avg = Column(Float)
    no2_avg = Column(Float)
    o3_avg = Column(Float)
    
    # Quality indices
    aqi_index = Column(Float)  # Normalized index
    health_risk_level = Column(String(20)) # "Low", "Moderate", "High"
    
    # Metadata
    station_count = Column(Integer)
    data_source = Column(String(100))
    year = Column(Integer)
    
    # Relationships
    municipality = relationship("Municipality", back_populates="air_quality")

    def __repr__(self):
        return f"<AirQuality {self.municipality_id} AQI: {self.aqi_index}>"
