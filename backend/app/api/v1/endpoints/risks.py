from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.risk import SeismicRisk, FloodRisk, LandslideRisk, ClimateProjection, AirQuality
from app.api.schemas.risk import (
    RiskSummaryResponse, 
    SeismicRiskResponse, 
    FloodRiskResponse, 
    LandslideRiskResponse, 
    ClimateProjectionResponse,
    AirQualityResponse
)
from app.models.geography import Municipality
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
import json

router = APIRouter()

@router.get("/municipality/{id}", response_model=RiskSummaryResponse)
def get_municipality_risks(id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive multi-hazard environmental risk assessment for a municipality.
    
    Combines seismic, flood, landslide, climate projection, and air quality data
    into a unified risk profile. Includes GeoJSON map data for spatial visualization
    of each risk layer. Essential for understanding long-term investment exposure.
    
    **Parameters:**
    - **id**: Municipality unique identifier
    
    **Returns Multi-Hazard Assessment:**
    - **seismic_risk**: Earthquake risk (zone classification, PGA values)
    - **flood_risk**: Flooding hazard (area at risk, population exposed)
    - **landslide_risk**: Landslide susceptibility (hazard level, affected area)
    - **climate_projection**: 2050 climate scenarios (temperature increase, heatwave days)
    - **air_quality**: Current air pollution levels (PM2.5, PM10, NO2)
    - **overall_risk_level**: Aggregated risk classification (Low/Moderate/High/Very High)
    - **total_risk_score**: Composite risk score (0-100)
    
    **Map Data (GeoJSON):**
    Each risk type includes `*_map_data` field with GeoJSON FeatureCollection
    for rendering on interactive maps. Geometry includes municipality boundaries
    or centroids with risk scores as properties.
    
    **Example Response:**
    ```json
    {
      "municipality_id": 58091,
      "municipality_name": "Roma",
      "seismic_risk": {
        "seismic_zone": 3,
        "hazard_level": "Moderate",
        "risk_score": 45.0,
        "pga_value": 0.15
      },
      "flood_risk": {
        "hazard_level": "Low",
        "risk_score": 25.0,
        "area_at_risk_sqkm": 12.5,
        "population_exposed": 15000
      },
      "climate_projection": {
        "target_year": 2050,
        "scenario": "SSP5-8.5",
        "temp_increase_c": 2.8,
        "heatwave_days_increase": 22
      },
      "air_quality": {
        "year": 2023,
        "pm25_avg": 18.5,
        "pm10_avg": 28.2,
        "no2_avg": 35.1,
        "aqi_category": "Moderate"
      },
      "overall_risk_level": "Moderate",
      "total_risk_score": 42.5,
      "seismic_map_data": {
        "type": "FeatureCollection",
        "features": [...]
      }
    }
    ```
    
    **Risk Score Interpretation:**
    - **0-25**: Low risk - Favorable conditions
    - **25-50**: Moderate risk - Some considerations needed
    - **50-75**: High risk - Significant mitigation required
    - **75-100**: Very High risk - Major concerns for long-term investment
    
    **Error Responses:**
    - **404**: Municipality not found
    """
    muni = db.query(Municipality).filter(Municipality.id == id).first()
    if not muni:
        raise HTTPException(status_code=404, detail="Municipality not found")

    seismic = db.query(SeismicRisk).filter(SeismicRisk.municipality_id == id).first()
    flood = db.query(FloodRisk).filter(FloodRisk.municipality_id == id).first()
    landslide = db.query(LandslideRisk).filter(LandslideRisk.municipality_id == id).first()
    
    # Get the latest high-emissions projection (SSP5-8.5 or RCP8.5)
    climate = db.query(ClimateProjection).filter(
        ClimateProjection.municipality_id == id,
        ClimateProjection.scenario.in_(["SSP5-8.5", "RCP8.5"]),
        ClimateProjection.target_year == 2050
    ).order_by(ClimateProjection.scenario.desc()).first() # SSP5 usually sorts higher than RCP
    
    # Get Air Quality data
    aq = db.query(AirQuality).filter(AirQuality.municipality_id == id).order_by(AirQuality.year.desc()).first()
    
    # Calculate overall risk level (simplified)
    # Using a 0-100 scale: 0-25 Low, 25-50 Moderate, 50-75 High, 75-100 Very High
    risk_objects = [seismic, flood, landslide]
    scores = [s.risk_score for s in risk_objects if s and s.risk_score is not None]
    
    # Add climate risk proxy (heat days / 40 * 100)
    if climate and climate.heatwave_days_increase:
        climate_risk_score = min(100, (climate.heatwave_days_increase / 40) * 100)
        scores.append(climate_risk_score)
    else:
        climate_risk_score = 0
        
    # Add air quality risk proxy (PM2.5 / 25 * 100)
    if aq and aq.pm25_avg:
        aq_risk_score = min(100, (aq.pm25_avg / 25) * 100)
        scores.append(aq_risk_score)
    else:
        aq_risk_score = 0

    avg_score = sum(scores) / len(scores) if scores else 0
    
    if avg_score < 25:
        level = "Low"
    elif avg_score < 50:
        level = "Moderate"
    elif avg_score < 75:
        level = "High"
    else:
        level = "Very High"

    # Generate map data for spatial visualization
    def _create_geojson(muni, score, risk_type):
        geom = muni.geometry or muni.centroid
        if not geom:
            return None
        return {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "name": muni.name,
                    "risk_score": score,
                    "risk_type": risk_type,
                    "hazard_level": "High" if score > 70 else "Moderate" if score > 40 else "Low"
                },
                "geometry": mapping(to_shape(geom))
            }]
        }

    return {
        "municipality_id": id,
        "municipality_name": muni.name,
        "seismic_risk": SeismicRiskResponse.from_orm(seismic) if seismic else None,
        "flood_risk": FloodRiskResponse(
            municipality_id=id,
            hazard_level=flood.risk_level,
            risk_score=flood.risk_score,
            area_at_risk_sqkm=flood.high_hazard_area_pct * muni.area_sqkm / 100 if flood.high_hazard_area_pct and muni.area_sqkm else None,
            population_exposed=flood.population_exposed
        ) if flood else None,
        "landslide_risk": LandslideRiskResponse(
            municipality_id=id,
            hazard_level=landslide.risk_level,
            risk_score=landslide.risk_score,
            area_at_risk_sqkm=landslide.high_hazard_area_pct * muni.area_sqkm / 100 if landslide.high_hazard_area_pct and muni.area_sqkm else None
        ) if landslide else None,
        "climate_projection": ClimateProjectionResponse.from_orm(climate) if climate else None,
        "air_quality": AirQualityResponse.from_orm(aq) if aq else None,
        "overall_risk_level": level,
        "total_risk_score": avg_score,
        "seismic_map_data": _create_geojson(muni, seismic.risk_score, "seismic") if seismic else None,
        "flood_map_data": _create_geojson(muni, flood.risk_score, "flood") if flood else None,
        "landslide_map_data": _create_geojson(muni, landslide.risk_score, "landslide") if landslide else None,
        "climate_map_data": _create_geojson(muni, climate_risk_score, "climate") if climate else None,
        "air_quality_map_data": _create_geojson(muni, aq_risk_score, "air_quality") if aq else None
    }
