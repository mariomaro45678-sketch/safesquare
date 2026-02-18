from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime

class CoordinatesResponse(BaseModel):
    """Geographic coordinates"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 45.4642,
                "longitude": 9.1900
            }
        }

class MunicipalityResponse(BaseModel):
    """Municipality information"""
    id: int
    name: str
    code: str = Field(..., description="ISTAT code")
    province_name: Optional[str] = None
    region_name: Optional[str] = None
    population: Optional[int] = None
    area_sqkm: Optional[float] = None
    postal_codes: Optional[str] = None
    investment_score: Optional[float] = None
    coordinates: Optional[CoordinatesResponse] = None
    dist_train_station_km: Optional[float] = None
    dist_highway_exit_km: Optional[float] = None
    hospital_count: Optional[int] = 0
    school_count: Optional[int] = 0
    province_code: Optional[str] = None
    altitude: Optional[int] = None
    supermarket_count: Optional[int] = 0
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Milano",
                "code": "015146",
                "province_name": "Milano",
                "region_name": "Lombardia",
                "population": 1396059,
                "area_sqkm": 181.8,
                "postal_codes": "20121-20162",
                "coordinates": {
                    "latitude": 45.4642,
                    "longitude": 9.1900
                }
            }
        }

class OMIZoneResponse(BaseModel):
    """OMI zone information"""
    id: int
    zone_code: str
    zone_name: Optional[str] = None
    zone_type: Optional[str] = None
    municipality_id: int
    municipality_name: Optional[str] = None
    coordinates: Optional[CoordinatesResponse] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "zone_code": "B1",
                "zone_name": "Centro Storico",
                "zone_type": "Centro",
                "municipality_id": 1,
                "municipality_name": "Milano",
                "coordinates": {
                    "latitude": 45.4642,
                    "longitude": 9.1900
                }
            }
        }

class LocationSearchRequest(BaseModel):
    """Request for location search"""
    query: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Search query (address, postal code, municipality name, or OMI zone)"
    )
    
    @field_validator('query')
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Via Dante 1, Milano"
            }
        }

class LocationSearchResponse(BaseModel):
    """Response for location search"""
    query: str
    found: bool
    geocoded: Optional[Dict[str, Any]] = None
    municipality: Optional[MunicipalityResponse] = None
    omi_zone: Optional[OMIZoneResponse] = None
    coordinates: Optional[CoordinatesResponse] = None
    message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Via Dante 1, Milano",
                "found": True,
                "geocoded": {
                    "display_name": "Via Dante, Milano, MI, Italy"
                },
                "municipality": {
                    "id": 1,
                    "name": "Milano",
                    "code": "015146"
                },
                "omi_zone": {
                    "id": 1,
                    "zone_code": "B1",
                    "zone_name": "Centro Storico"
                },
                "coordinates": {
                    "latitude": 45.4642,
                    "longitude": 9.1900
                },
                "message": "Location found successfully"
            }
        }


class ParcelResponse(BaseModel):
    """Cadastral parcel lookup result.

    Data source: Agenzia delle Entrate — Cartografia Catastale (CC-BY 4.0).
    """
    foglio: str = Field(..., description="Map sheet identifier")
    particella: str = Field(..., description="Parcel number within the sheet")
    municipality_id: int
    municipality_name: Optional[str] = None
    linked_omi_zone: Optional[OMIZoneResponse] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "foglio": "123",
                "particella": "456",
                "municipality_id": 58091,
                "municipality_name": "Roma",
                "linked_omi_zone": {
                    "id": 42,
                    "zone_code": "B1_058091",
                    "zone_name": "Centro Storico",
                    "zone_type": "Centro",
                    "municipality_id": 58091,
                    "municipality_name": "Roma"
                }
            }
        }


class SearchResult(BaseModel):
    """Search result for municipality search."""
    id: int
    name: str
    province_name: Optional[str] = None
    region_name: Optional[str] = None
    population: Optional[int] = None
    investment_score: Optional[float] = None
    coordinates: Optional[CoordinatesResponse] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Milano",
                "province_name": "Milano",
                "region_name": "Lombardia",
                "population": 1396059,
                "investment_score": 7.5,
                "coordinates": {"latitude": 45.4642, "longitude": 9.1900}
            }
        }


class DiscoveryResult(BaseModel):
    """Discovery result for top municipalities."""
    id: int
    name: str
    province_name: Optional[str] = None
    region_name: Optional[str] = None
    population: Optional[int] = None
    investment_score: Optional[float] = None
    price_trend_score: Optional[float] = None
    crime_score: Optional[float] = None
    demographics_score: Optional[float] = None
    connectivity_score: Optional[float] = None
    coordinates: Optional[CoordinatesResponse] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Milano",
                "province_name": "Milano",
                "region_name": "Lombardia",
                "population": 1396059,
                "investment_score": 7.5,
                "price_trend_score": 8.0,
                "crime_score": 6.5,
                "demographics_score": 7.8,
                "connectivity_score": 8.2,
                "coordinates": {"latitude": 45.4642, "longitude": 9.1900}
            }
        }
