from sqlalchemy import Column, Integer, String, BigInteger, Enum as SQLAEnum
from geoalchemy2 import Geometry
from .base import Base, TimestampMixin
import enum

class ServiceType(enum.Enum):
    HOSPITAL = "hospital"
    SCHOOL = "school"
    SUPERMARKET = "supermarket"
    PHARMACY = "pharmacy"
    PARK = "park"

class ServiceNode(Base, TimestampMixin):
    """General services and amenities (OpenStreetMap)"""
    __tablename__ = "service_nodes"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(BigInteger, unique=True, index=True)
    name = Column(String(255), nullable=True)
    
    service_type = Column(SQLAEnum(ServiceType), nullable=False)
    sub_type = Column(String(100), nullable=True) # e.g. "primary", "secondary", "specialized"
    
    geometry = Column(Geometry('POINT', srid=4326))
    
    def __repr__(self):
        return f"<ServiceNode {self.name} ({self.service_type})>"
