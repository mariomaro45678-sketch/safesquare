from pydantic import BaseModel, Field
from typing import Optional

class DemographicsResponse(BaseModel):
    """Demographics information"""
    municipality_id: int
    municipality_name: Optional[str] = None
    year: int
    population: int
    total_population: Optional[int] = None
    population_density: Optional[float] = Field(None, description="People per sq km")
    population_trend: Optional[float] = Field(None, description="Population growth/decline rate (%)")
    median_age: Optional[float] = None
    age_0_14_pct: Optional[float] = Field(None, description="Population aged 0-14 (%)")
    age_15_64_pct: Optional[float] = Field(None, description="Population aged 15-64 (%)")
    age_65_plus_pct: Optional[float] = Field(None, description="Population aged 65+ (%)")
    foreign_residents_pct: Optional[float] = Field(None, description="Foreign residents (%)")
    median_income_eur: Optional[float] = Field(None, description="Median income (€)")
    unemployment_rate: Optional[float] = Field(None, description="Unemployment rate (%)")
    education_tertiary_pct: Optional[float] = Field(None, description="Tertiary education (%)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "municipality_id": 1,
                "municipality_name": "Milano",
                "year": 2023,
                "population": 1396059,
                "population_density": 7679.0,
                "median_age": 46.8,
                "age_0_14_pct": 12.5,
                "age_15_64_pct": 63.2,
                "age_65_plus_pct": 24.3,
                "foreign_residents_pct": 19.2,
                "median_income_eur": 28500,
                "unemployment_rate": 5.8,
                "education_tertiary_pct": 32.5
            }
        }

class CrimeStatisticsResponse(BaseModel):
    """Crime statistics"""
    municipality_id: int
    municipality_name: Optional[str] = None
    year: int
    total_crimes: int
    total_crimes_per_1000: float = Field(..., description="Crimes per 1000 residents")
    violent_crimes: Optional[int] = None
    property_crimes: Optional[int] = None
    theft_rate: Optional[float] = Field(None, description="Thefts per 1000 residents")
    safety_index: Optional[float] = Field(None, ge=0, le=100, description="Overall safety index (0-100)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "municipality_id": 1,
                "municipality_name": "Milano",
                "year": 2023,
                "total_crimes": 58420,
                "total_crimes_per_1000": 41.8,
                "violent_crimes": 3250,
                "property_crimes": 42100,
                "theft_rate": 30.2,
                "safety_index": 65.0
            }
        }
