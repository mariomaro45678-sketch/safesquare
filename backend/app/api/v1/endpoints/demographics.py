from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.api.schemas.demographics import DemographicsResponse, CrimeStatisticsResponse
from app.core.database import get_db
from app.models.demographics import Demographics, CrimeStatistics
from app.models.geography import Municipality

router = APIRouter()

@router.get("/municipality/{id}", response_model=DemographicsResponse)
def get_municipality_demographics(id: int, db: Session = Depends(get_db)):
    """
    Get demographic data for a municipality.
    
    Returns comprehensive population statistics including age distribution, density,
    income levels, employment, and education metrics. Essential for understanding
    local market liquidity and investment potential.
    
    **Parameters:**
    - **id**: Municipality unique identifier
    
    **Returns:**
    - **municipality_id**: Municipality identifier
    - **municipality_name**: Municipality name
    - **year**: Data reference year
    - **population**: Total population count
    - **population_density**: Residents per square kilometer
    - **median_age**: Median age of population
    - **age_0_14_pct**: Percentage of population aged 0-14 (youth)
    - **age_15_64_pct**: Percentage of population aged 15-64 (working age)
    - **age_65_plus_pct**: Percentage of population aged 65+ (elderly)
    - **median_income_eur**: Median annual income in euros
    - **unemployment_rate**: Unemployment rate percentage
    - **education_tertiary_pct**: Percentage with tertiary education
    
    **Example Response:**
    ```json
    {
      "municipality_id": 15146,
      "municipality_name": "Milano",
      "year": 2023,
      "population": 1352000,
      "population_density": 7400,
      "median_age": 45.2,
      "age_0_14_pct": 12.5,
      "age_15_64_pct": 63.8,
      "age_65_plus_pct": 23.7,
      "median_income_eur": 32500,
      "unemployment_rate": 6.2,
      "education_tertiary_pct": 28.4
    }
    ```
    
    **Error Responses:**
    - **404**: Municipality not found or demographic data not available
    """
    muni = db.query(Municipality).filter(Municipality.id == id).first()
    if not muni:
        raise HTTPException(status_code=404, detail="Municipality not found")

    demo = db.query(Demographics).filter(Demographics.municipality_id == id).order_by(desc(Demographics.year)).first()
    if not demo:
        raise HTTPException(status_code=404, detail="Demographic data not found for this municipality")

    # Calculate population trend
    previous_demo = db.query(Demographics).filter(
        Demographics.municipality_id == id,
        Demographics.year < demo.year
    ).order_by(desc(Demographics.year)).first()
    
    population_trend = None
    if previous_demo and previous_demo.total_population and demo.total_population:
        population_trend = ((demo.total_population - previous_demo.total_population) / previous_demo.total_population) * 100

    # Map to schema (some calculated fields)
    total = demo.total_population or 1
    return DemographicsResponse(
        municipality_id=id,
        municipality_name=muni.name,
        year=demo.year,
        population=demo.total_population,
        total_population=demo.total_population,
        population_density=demo.population_density,
        population_trend=population_trend,
        median_age=demo.median_age,
        age_0_14_pct=(demo.age_0_14 / total * 100) if demo.age_0_14 else None,
        age_15_64_pct=(demo.age_15_64 / total * 100) if demo.age_15_64 else None,
        age_65_plus_pct=(demo.age_65_plus / total * 100) if demo.age_65_plus else None,
        foreign_residents_pct=None, # Not explicitly in model yet
        median_income_eur=demo.avg_income_euro,
        unemployment_rate=demo.unemployment_rate,
        education_tertiary_pct=demo.higher_education_rate
    )

@router.get("/crime/municipality/{id}", response_model=CrimeStatisticsResponse)
def get_municipality_crime(id: int, db: Session = Depends(get_db)):
    """
    Get crime statistics for a municipality.
    
    Returns safety metrics including crime rates, theft statistics, and calculated
    safety indices. Critical for investment risk assessment and neighborhood evaluation.
    
    **Parameters:**
    - **id**: Municipality unique identifier
    
    **Returns:**
    - **municipality_id**: Municipality identifier
    - **municipality_name**: Municipality name
    - **year**: Data reference year
    - **total_crimes**: Total number of reported crimes
    - **total_crimes_per_1000**: Crime rate per 1,000 residents (normalized)
    - **violent_crimes**: Count of violent crimes
    - **property_crimes**: Count of property crimes
    - **theft_rate**: Theft incidents per 1,000 residents
    - **safety_index**: Overall safety index (0-100, higher is safer)
    
    **Example Response:**
    ```json
    {
      "municipality_id": 58091,
      "municipality_name": "Roma",
      "year": 2023,
      "total_crimes": 89450,
      "total_crimes_per_1000": 31.2,
      "violent_crimes": null,
      "property_crimes": null,
      "theft_rate": 18.5,
      "safety_index": 52.3
    }
    ```
    
    **Error Responses:**
    - **404**: Municipality not found or crime statistics not available
    """
    muni = db.query(Municipality).filter(Municipality.id == id).first()
    if not muni:
        raise HTTPException(status_code=404, detail="Municipality not found")

    crime = db.query(CrimeStatistics).filter(CrimeStatistics.municipality_id == id).order_by(desc(CrimeStatistics.year)).first()
    if not crime:
        raise HTTPException(status_code=404, detail="Crime statistics not found for this municipality")

    return CrimeStatisticsResponse(
        municipality_id=id,
        municipality_name=muni.name,
        year=crime.year,
        total_crimes=int((crime.total_crimes_per_1000 or 0) * (muni.population or 0) / 1000),
        total_crimes_per_1000=crime.total_crimes_per_1000 or 0,
        violent_crimes=None,
        property_crimes=None,
        theft_rate=crime.property_crimes_per_1000,
        safety_index=100 - (crime.crime_index or 50)
    )
