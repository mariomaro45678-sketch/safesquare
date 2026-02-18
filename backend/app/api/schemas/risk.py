from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import date

class SeismicRiskResponse(BaseModel):
    """Seismic risk information"""
    municipality_id: int
    municipality_name: Optional[str] = None
    seismic_zone: int = Field(..., ge=1, le=4, description="Italian seismic zone (1=highest, 4=lowest)")
    hazard_level: str = Field(..., description="Risk level description")
    risk_score: float = Field(..., ge=0, le=100, description="Normalized risk score (0=low, 100=high)")
    historical_earthquakes_count: Optional[int] = None
    max_historical_magnitude: Optional[float] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "municipality_id": 1,
                "municipality_name": "Milano",
                "seismic_zone": 4,
                "hazard_level": "Low",
                "risk_score": 15.0,
                "historical_earthquakes_count": 3,
                "max_historical_magnitude": 4.2
            }
        }

class FloodRiskResponse(BaseModel):
    """Flood risk information"""
    municipality_id: int
    municipality_name: Optional[str] = None
    hazard_level: str
    risk_score: float = Field(..., ge=0, le=100)
    area_at_risk_sqkm: Optional[float] = None
    population_exposed: Optional[int] = None
    risk_probability_high: Optional[float] = Field(None, description="Probability of high risk flooding (%)")
    risk_probability_medium: Optional[float] = Field(None, description="Probability of medium risk flooding (%)")
    risk_probability_low: Optional[float] = Field(None, description="Probability of low risk flooding (%)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "municipality_id": 1,
                "municipality_name": "Milano",
                "hazard_level": "Medium",
                "risk_score": 35.0,
                "area_at_risk_sqkm": 8.5,
                "population_exposed": 25000,
                "risk_probability_high": 5.0,
                "risk_probability_medium": 15.0,
                "risk_probability_low": 30.0
            }
        }

class LandslideRiskResponse(BaseModel):
    """Landslide risk information"""
    municipality_id: int
    municipality_name: Optional[str] = None
    hazard_level: str
    risk_score: float = Field(..., ge=0, le=100)
    area_at_risk_sqkm: Optional[float] = None
    susceptibility_class: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "municipality_id": 1,
                "municipality_name": "Milano",
                "hazard_level": "Low",
                "risk_score": 10.0,
                "area_at_risk_sqkm": 2.3,
                "susceptibility_class": "Low"
            }
        }

class ClimateProjectionResponse(BaseModel):
    """Climate change projection"""
    municipality_id: int
    municipality_name: Optional[str] = None
    scenario: str = Field(..., description="Climate scenario (e.g., RCP4.5, RCP8.5)")
    target_year: int
    avg_temp_change: Optional[float] = Field(None, description="Average temperature increase (°C)")
    extreme_rainfall_increase: Optional[float] = Field(None, description="Extreme rainfall increase (%)")
    flood_risk_multiplier: Optional[float] = Field(None, description="Flood risk multiplier")
    heat_days_increase: Optional[int] = Field(None, description="Additional days over 35°C per year")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "municipality_id": 1,
                "municipality_name": "Milano",
                "scenario": "RCP8.5",
                "target_year": 2050,
                "avg_temp_change": 2.8,
                "extreme_rainfall_increase": 25.0,
                "flood_risk_multiplier": 1.4,
                "heat_days_increase": 18
            }
        }

class AirQualityResponse(BaseModel):
    """Air quality information"""
    municipality_id: int
    pm25_avg: Optional[float] = None
    pm10_avg: Optional[float] = None
    aqi_index: Optional[float] = None
    health_risk_level: Optional[str] = None
    data_source: Optional[str] = None
    
    class Config:
        from_attributes = True

class RiskSummaryResponse(BaseModel):
    """Combined risk summary for a location"""
    municipality_id: int
    municipality_name: str
    seismic_risk: Optional[SeismicRiskResponse] = None
    flood_risk: Optional[FloodRiskResponse] = None
    landslide_risk: Optional[LandslideRiskResponse] = None
    climate_projection: Optional[ClimateProjectionResponse] = None
    air_quality: Optional[AirQualityResponse] = None
    overall_risk_level: str = Field(..., description="Overall risk assessment")
    total_risk_score: float = Field(..., ge=0, le=100, description="Combined risk score")
    
    # Map layers (GeoJSON)
    seismic_map_data: Optional[Any] = None
    flood_map_data: Optional[Any] = None
    landslide_map_data: Optional[Any] = None
    climate_map_data: Optional[Any] = None
    air_quality_map_data: Optional[Any] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "municipality_id": 1,
                "municipality_name": "Milano",
                "seismic_risk": {
                    "seismic_zone": 4,
                    "hazard_level": "Low",
                    "risk_score": 15.0
                },
                "flood_risk": {
                    "hazard_level": "Medium",
                    "risk_score": 35.0
                },
                "landslide_risk": {
                    "hazard_level": "Low",
                    "risk_score": 10.0
                },
                "climate_projection": {
                    "scenario": "RCP8.5",
                    "target_year": 2050,
                    "avg_temp_change": 2.8
                },
                "overall_risk_level": "Moderate",
                "total_risk_score": 20.0
            }
        }
