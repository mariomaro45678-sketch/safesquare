from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List, Any
from datetime import date
from app.api.schemas.location import CoordinatesResponse

class ScoreComponentsResponse(BaseModel):
    """Individual score components"""
    price_trend: float = Field(..., ge=0, le=10, description="Price trend score (0-10)")
    affordability: float = Field(..., ge=0, le=10, description="Affordability score (0-10)")
    rental_yield: float = Field(..., ge=0, le=10, description="Rental yield score (0-10)")
    demographics: float = Field(..., ge=0, le=10, description="Demographics score (0-10)")
    crime: float = Field(..., ge=0, le=10, description="Crime safety score (0-10)")
    seismic: float = Field(..., ge=0, le=10, description="Seismic risk score (0-10)")
    flood: float = Field(..., ge=0, le=10, description="Flood risk score (0-10)")
    landslide: float = Field(..., ge=0, le=10, description="Landslide risk score (0-10)")
    climate: float = Field(..., ge=0, le=10, description="Climate risk score (0-10)")
    connectivity: float = Field(default=5.0, ge=0, le=10, description="Connectivity score (0-10)")
    digital_connectivity: float = Field(default=5.0, ge=0, le=10, description="Digital connectivity score (0-10)")
    services: float = Field(default=5.0, ge=0, le=10, description="Services score (0-10)")
    air_quality: float = Field(default=5.0, ge=0, le=10, description="Air quality score (0-10)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "price_trend": 7.5,
                "affordability": 6.0,
                "rental_yield": 7.2,
                "demographics": 8.5,
                "crime": 7.8,
                "seismic": 9.0,
                "flood": 8.5,
                "landslide": 9.5,
                "climate": 6.5
            }
        }

class InvestmentScoreResponse(BaseModel):
    """Investment score response"""
    overall_score: float = Field(..., ge=0, le=10, description="Overall investment score (0-10)")
    score_category: str = Field(..., description="Score category label")
    municipality_id: Optional[int] = None
    municipality_name: Optional[str] = None
    omi_zone_id: Optional[int] = None
    omi_zone_code: Optional[str] = None
    component_scores: ScoreComponentsResponse
    weights: Dict[str, float] = Field(..., description="Weights used in calculation")
    calculation_date: date
    recommendation: str = Field(..., description="Investment recommendation")
    confidence: float = Field(default=0.75, ge=0, le=1, description="Calculation confidence score (0-1)")
    risk_factors: list[str] = Field(default_factory=list, description="Key risk factors to consider")
    strengths: list[str] = Field(default_factory=list, description="Key strengths")
    
    @field_validator('score_category', mode='before')
    @classmethod
    def determine_category(cls, v, info):
        """Determine score category based on overall score"""
        if v:  # If already provided, use it
            return v
        
        # Otherwise calculate from overall_score
        score = info.data.get('overall_score', 5.0)
        if score >= 8.5:
            return "Excellent"
        elif score >= 7.0:
            return "Good"
        elif score >= 5.5:
            return "Fair"
        elif score >= 4.0:
            return "Below Average"
        else:
            return "Poor"
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "overall_score": 7.8,
                "score_category": "Good",
                "municipality_name": "Milano",
                "omi_zone_code": "B1",
                "component_scores": {
                    "price_trend": 7.5,
                    "affordability": 6.0,
                    "rental_yield": 7.2,
                    "demographics": 8.5,
                    "crime": 7.8,
                    "seismic": 9.0,
                    "flood": 8.5,
                    "landslide": 9.5,
                    "climate": 6.5
                },
                "weights": {
                    "price_trend": 0.20,
                    "affordability": 0.10,
                    "rental_yield": 0.15,
                    "demographics": 0.15,
                    "crime": 0.10,
                    "seismic": 0.10,
                    "flood": 0.08,
                    "landslide": 0.07,
                    "climate": 0.05
                },
                "calculation_date": "2024-01-29",
                "recommendation": "Good investment opportunity with strong fundamentals and low disaster risk.",
                "risk_factors": [
                    "Climate change may increase flood risk by 2050",
                    "Affordability is moderate for first-time buyers"
                ],
                "strengths": [
                    "Strong demographic growth",
                    "Low seismic risk zone",
                    "Positive price trend"
                ]
            }
        }

class OMIZoneScoreResponse(BaseModel):
    """OMI zone with score and geometry for map rendering."""
    zone_id: int = Field(..., description="OMI zone unique identifier")
    zone_code: str = Field(..., description="OMI zone code (e.g., B1, C3)")
    zone_name: Optional[str] = Field(None, description="OMI zone name (e.g., Centro Storico)")
    zone_type: Optional[str] = Field(None, description="Zone type (Centro, Periferia, etc.)")
    municipality_id: int = Field(..., description="Parent municipality ID")
    overall_score: Optional[float] = Field(None, ge=0, le=10, description="Investment score (0-10) or null if not calculated")
    score_category: Optional[str] = Field(None, description="Score category (Excellent/Good/Fair/Poor)")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Score confidence (0-1)")
    centroid: Optional[CoordinatesResponse] = Field(None, description="Zone centroid coordinates")
    geometry: Optional[Any] = Field(None, description="GeoJSON geometry for polygon rendering")

    @field_validator('score_category', mode='before')
    @classmethod
    def determine_category(cls, v, info):
        """Determine score category based on overall score"""
        if v:
            return v
        score = info.data.get('overall_score')
        if score is None:
            return None
        if score >= 8.5:
            return "Excellent"
        elif score >= 7.0:
            return "Good"
        elif score >= 5.5:
            return "Fair"
        elif score >= 4.0:
            return "Below Average"
        else:
            return "Poor"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "zone_id": 42,
                "zone_code": "B1",
                "zone_name": "Centro Storico",
                "zone_type": "Centro",
                "municipality_id": 5190,
                "overall_score": 7.2,
                "score_category": "Good",
                "confidence": 0.85,
                "centroid": {"latitude": 41.9028, "longitude": 12.4964},
                "geometry": {"type": "MultiPolygon", "coordinates": []}
            }
        }


class ScoreCalculationRequest(BaseModel):
    """Request to calculate investment score"""
    municipality_id: Optional[int] = None
    omi_zone_id: Optional[int] = None
    custom_weights: Optional[Dict[str, float]] = None
    
    @field_validator('custom_weights')
    @classmethod
    def validate_weights(cls, v):
        """Ensure weights sum to 1.0 if provided"""
        if v is not None:
            total = sum(v.values())
            if not (0.99 <= total <= 1.01):  # Allow small floating point errors
                raise ValueError(f"Weights must sum to 1.0, got {total}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "municipality_id": 1,
                "custom_weights": {
                    "price_trend": 0.25,
                    "rental_yield": 0.20,
                    "seismic": 0.15,
                    "flood": 0.10,
                    "demographics": 0.10,
                    "crime": 0.10,
                    "landslide": 0.05,
                    "affordability": 0.03,
                    "climate": 0.02
                }
            }
        }
