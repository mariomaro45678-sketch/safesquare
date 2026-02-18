from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import date
from app.models.property import PropertyType, TransactionType

# --- Geography Schemas ---

class MunicipalityBase(BaseModel):
    name: str
    code: str
    province_id: int

class MunicipalityOut(MunicipalityBase):
    id: int
    area_sqkm: Optional[float] = None
    population: Optional[int] = None
    postal_codes: Optional[List[str]] = None

    class Config:
        from_attributes = True

class OMIZoneBase(BaseModel):
    zone_code: str
    zone_name: str
    zone_type: str
    municipality_id: int

class OMIZoneOut(OMIZoneBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Property & Price Schemas ---

class PropertyPriceBase(BaseModel):
    year: int
    semester: int
    property_type: PropertyType
    transaction_type: TransactionType
    avg_price: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None

class PropertyPriceOut(PropertyPriceBase):
    id: int
    omi_zone_id: int
    price_change_yoy: Optional[float] = None
    rental_yield: Optional[float] = None

    class Config:
        from_attributes = True

# --- Scoring Schemas ---

class ComponentScores(BaseModel):
    price_trend: float
    affordability: float
    rental_yield: float
    demographics: float
    crime: float
    seismic: float
    flood: float
    landslide: float
    climate: float

class InvestmentScoreOut(BaseModel):
    overall_score: float
    calculation_date: date
    location: str
    component_scores: ComponentScores
    weights: Dict[str, float]
    municipality_id: Optional[int] = None
    omi_zone_id: Optional[int] = None

    class Config:
        from_attributes = True

# --- Risk Schemas ---

class RiskSummaryOut(BaseModel):
    municipality_id: int
    seismic_zone: Optional[int] = None
    seismic_hazard: Optional[str] = None
    flood_risk_score: Optional[float] = None
    landslide_risk_score: Optional[float] = None
    
# --- Search Schemas ---

class SearchResult(BaseModel):
    query: str
    geocoded: Optional[Dict[str, Any]] = None
    municipality: Optional[MunicipalityOut] = None
    omi_zone: Optional[OMIZoneOut] = None
    coordinates: Optional[Dict[str, float]] = None

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Address, municipality or postal code")
