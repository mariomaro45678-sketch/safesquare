from sqlalchemy import Column, Integer, String, BigInteger, Enum as SQLAEnum
from geoalchemy2 import Geometry
from .base import Base, TimestampMixin
import enum

class TransportType(enum.Enum):
    TRAIN_STATION = "train_station"
    HIGHWAY_EXIT = "highway_exit"
    AIRPORT = "airport"

class TransportNode(Base, TimestampMixin):
    """Transport infrastructure nodes (OpenStreetMap)"""
    __tablename__ = "transport_nodes"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(BigInteger, unique=True, index=True)
    name = Column(String(200), nullable=True)
    
    node_type = Column(SQLAEnum(TransportType), nullable=False)
    sub_type = Column(String(50), nullable=True) # e.g. "high_speed", "regional"
    
    geometry = Column(Geometry('POINT', srid=4326))
    
    def __repr__(self):
        return f"<TransportNode {self.name} ({self.node_type})>"
