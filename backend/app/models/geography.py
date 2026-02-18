from sqlalchemy import Column, Integer, String, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from .base import Base, TimestampMixin

class Region(Base, TimestampMixin):
    """Italian Regions (Regioni)"""
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=False, unique=True)  # ISTAT code
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    
    # Relationships
    provinces = relationship("Province", back_populates="region", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Region {self.name}>"


class Province(Base, TimestampMixin):
    """Italian Provinces (Province)"""
    __tablename__ = "provinces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False, unique=True)  # ISTAT code
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    
    # Phase 6: Regional Baseline (Capital's Rent)
    avg_rent_sqm = Column(Float, nullable=True) # Annual Euros per Sqm (Baseline for Province)
    
    # Relationships
    region = relationship("Region", back_populates="provinces")
    municipalities = relationship("Municipality", back_populates="province", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Province {self.name}>"


class Municipality(Base, TimestampMixin):
    """Italian Municipalities (Comuni)"""
    __tablename__ = "municipalities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False, unique=True)  # ISTAT code
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    
    # Geographic data
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    centroid = Column(Geometry('POINT', srid=4326))
    area_sqkm = Column(Float)
    
    # Basic info
    population = Column(Integer)
    postal_codes = Column(String(500))  # Comma-separated list

    # Infrastructure / Services Stats
    dist_train_station_km = Column(Float, nullable=True)
    dist_highway_exit_km = Column(Float, nullable=True)
    hospital_count = Column(Integer, default=0)
    school_count = Column(Integer, default=0)
    supermarket_count = Column(Integer, default=0)

    # Digital Connectivity
    mobile_tower_count = Column(Integer, default=0)
    broadband_ftth_coverage = Column(Float, default=0.0) # Percentage
    broadband_speed_100mbps = Column(Float, default=0.0)
    
    # Phase 6: Rental Market (City Level)
    avg_rent_sqm = Column(Float, nullable=True) # Annual Euros per Sqm (Aggregated) # Percentage of households with >100Mbps
    
    # Relationships
    province = relationship("Province", back_populates="municipalities")
    omi_zones = relationship("OMIZone", back_populates="municipality", cascade="all, delete-orphan")
    demographics = relationship("Demographics", back_populates="municipality", cascade="all, delete-orphan")
    crime_stats = relationship("CrimeStatistics", back_populates="municipality", cascade="all, delete-orphan")
    seismic_risks = relationship("SeismicRisk", back_populates="municipality", cascade="all, delete-orphan")
    flood_risks = relationship("FloodRisk", back_populates="municipality", cascade="all, delete-orphan")
    landslide_risks = relationship("LandslideRisk", back_populates="municipality", cascade="all, delete-orphan")
    climate_projections = relationship("ClimateProjection", back_populates="municipality", cascade="all, delete-orphan")
    air_quality = relationship("AirQuality", back_populates="municipality", cascade="all, delete-orphan")
    investment_scores = relationship("InvestmentScore", back_populates="municipality", cascade="all, delete-orphan")
    cadastral_parcels = relationship("CadastralParcel", back_populates="municipality", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Municipality {self.name}>"


class OMIZone(Base, TimestampMixin):
    """OMI Micro-zones for property pricing"""
    __tablename__ = "omi_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_code = Column(String(20), nullable=False, unique=True)  # OMI zone identifier
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    
    # Zone details
    zone_name = Column(String(200))
    zone_type = Column(String(50))  # e.g., "Centro", "Periferia", "Semicentro"
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    centroid = Column(Geometry('POINT', srid=4326))
    
    # Relationships
    municipality = relationship("Municipality", back_populates="omi_zones")
    property_prices = relationship("PropertyPrice", back_populates="omi_zone", cascade="all, delete-orphan")
    investment_scores = relationship("InvestmentScore", back_populates="omi_zone", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<OMIZone {self.zone_code}>"


class CadastralParcel(Base, TimestampMixin):
    """Cadastral parcels from Agenzia delle Entrate Cartografia Catastale.

    Source: https://www.agenziaentrate.gov.it/portale/download-massivo-cartografia-catastale
    License: CC-BY 4.0 — attribution required in UI.
    """
    __tablename__ = "cadastral_parcels"

    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    omi_zone_id = Column(Integer, ForeignKey("omi_zones.id"), nullable=True)  # pre-calculated spatial join

    foglio = Column(String(20), nullable=False)       # map sheet identifier
    particella = Column(String(30), nullable=False)   # parcel number within the sheet
    geometry = Column(Geometry('POLYGON', srid=4326), nullable=False)

    __table_args__ = (
        UniqueConstraint('municipality_id', 'foglio', 'particella', name='uq_cadastral_parcel'),
    )

    # Relationships
    municipality = relationship("Municipality", back_populates="cadastral_parcels")
    omi_zone = relationship("OMIZone")

    def __repr__(self):
        return f"<CadastralParcel {self.foglio}/{self.particella}>"
