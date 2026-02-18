from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.scoring_engine import ScoringEngine
from app.api.schemas.score import InvestmentScoreResponse, ScoreComponentsResponse, ScoreCalculationRequest, OMIZoneScoreResponse
from app.models.score import InvestmentScore
from app.models.geography import Municipality, OMIZone
import logging
from datetime import date
from app.core.constants import CACHE_TTL_SCORES

logger = logging.getLogger(__name__)

router = APIRouter()
engine = ScoringEngine()

@router.post("/calculate", response_model=InvestmentScoreResponse)
async def calculate_investment_score(
    request: ScoreCalculationRequest, 
    db: Session = Depends(get_db)
):
    """
    Calculate and save investment score for a municipality or OMI zone.
    
    Executes the full scoring engine algorithm using Z-score normalization across
    13 investment pillars (price trends, affordability, rental yield, demographics,
    crime, connectivity, digital infrastructure, services, and environmental risks).
    
    **Scoring Methodology:**
    - Uses statistical Z-score normalization against national averages
    - Applies empirical calibration (pivot: 6.5, contrast multiplier: 3.0x)
    - Generates component scores, overall score, and confidence metric
    - Persists results to database with customizable weights
    
    **Request Body:**
    ```json
    {
      "municipality_id": 15146,
      "omi_zone_id": null,
      "custom_weights": {
        "price_trend": 0.15,
        "climate": 0.15
      }
    }
    ```
    
    **Parameters:**
    - **municipality_id**: Municipality to score (mutually exclusive with omi_zone_id)
    - **omi_zone_id**: OMI zone to score (mutually exclusive with municipality_id)
    - **custom_weights**: Optional weight overrides (must sum to ~1.0)
    
    **Returns:**
    - **overall_score**: Final investment score (1.0-10.0)
    - **confidence_score**: Data completeness metric (0.0-1.0)
    - **component_scores**: Individual pillar scores
    - **weights**: Applied weighting scheme
    - **data_sources**: Transparency links to source data
    
    **Example Response:**
    ```json
    {
      "overall_score": 8.2,
      "confidence_score": 0.85,
      "component_scores": {
        "price_trend": 7.8,
        "affordability": 6.5,
        "rental_yield": 8.1,
        "demographics": 9.2,
        "crime": 7.5,
        "connectivity": 8.8,
        "digital_connectivity": 9.1,
        "services": 8.4,
        "air_quality": 6.2,
        "seismic": 8.9,
        "flood": 7.3,
        "landslide": 8.5,
        "climate": 6.8
      },
      "weights": {...},
      "calculation_date": "2024-02-04"
    }
    ```
    
    **Error Responses:**
    - **404**: Municipality or OMI zone not found
    - **500**: Calculation error (insufficient data)
    """
    try:
        result = engine.calculate_score(
            db, 
            municipality_id=request.municipality_id,
            omi_zone_id=request.omi_zone_id,
            custom_weights=request.custom_weights
        )
        # Save to DB
        saved_score = engine.save_score(db, result)
        return _format_score_response(saved_score)
    except Exception as e:
        logger.error(f"Score calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/municipality/{id}", response_model=InvestmentScoreResponse)
def get_municipality_score(id: int, db: Session = Depends(get_db)):
    """
    Retrieve or calculate investment score for a municipality (with caching).
    
    Attempts to return cached score from memory (6 hours TTL) or database.
    If no cached score exists, calculates a new score using the scoring engine.
    Optimized for repeated API calls from frontend dashboards.
    
    **Caching Strategy:**
    1. Check in-memory cache (fast, 6-hour TTL)
    2. Check database for persisted scores (slower)
    3. Calculate new score if none exists (slowest)
    
    **Parameters:**
    - **id**: Municipality unique identifier
    
    **Returns:**
    - **overall_score**: Investment score (1-10)
    - **score_category**: Rating band (Excellent/Good/Fair/Poor)
    - **confidence**: Data quality metric (0-1)
    - **recommendation**: Human-readable investment advice
    - **strengths**: List of positive factors
    - **risk_factors**: List of concerns
    - **component_scores**: Detailed pillar breakdown
    
    **Example Response:**
    ```json
    {
      "overall_score": 7.8,
      "score_category": "Good",
      "municipality_id": 15146,
      "municipality_name": "Milano",
      "calculation_date": "2024-02-04",
      "confidence": 0.92,
      "recommendation": "Good investment potential with some manageable risks.",
      "strengths": [
        "Strong price growth trend",
        "High rental yield potential",
        "Positive demographic growth"
      ],
      "risk_factors": [
        "Significant long-term climate risk"
      ],
      "component_scores": {...}
    }
    ```
    
    **Score Categories:**
    - **8.0-10.0**: Excellent - Top-tier investment opportunity
    - **6.0-7.9**: Good - Solid fundamentals
    - **4.0-5.9**: Fair - Mixed signals, due diligence required
    - **1.0-3.9**: Poor - Significant challenges
    
    **Error Responses:**
    - **404**: Municipality not found
    - **500**: Scoring engine error
    """
    from app.core.cache import global_cache
    
    CACHE_KEY = f"score_municipality_{id}"
    TTL_SECONDS = CACHE_TTL_SCORES # 6 hours
    
    # Try memory cache first
    cached_response = global_cache.get(CACHE_KEY)
    if cached_response:
        return cached_response

    # Try DB cache (InvestmentScore table)
    cached = db.query(InvestmentScore).filter(
        InvestmentScore.municipality_id == id,
        InvestmentScore.omi_zone_id == None
    ).order_by(InvestmentScore.calculation_date.desc()).first()
    
    if cached:
        response = _format_score_response(cached)
        global_cache.set(CACHE_KEY, response, TTL_SECONDS)
        return response
        
    try:
        result = engine.calculate_score(db, municipality_id=id)
        # Create a temporary InvestmentScore object for formatting
        temp_score = InvestmentScore(
            municipality_id=id,
            overall_score=result['overall_score'],
            calculation_date=result['calculation_date'],
            price_trend_score=result['component_scores']['price_trend'],
            affordability_score=result['component_scores']['affordability'],
            rental_yield_score=result['component_scores']['rental_yield'],
            demographics_score=result['component_scores']['demographics'],
            crime_score=result['component_scores']['crime'],
            connectivity_score=result['component_scores']['connectivity'],
            digital_connectivity_score=result['component_scores']['digital_connectivity'],
            services_score=result['component_scores']['services'],
            air_quality_score=result['component_scores']['air_quality'],
            seismic_risk_score=result['component_scores']['seismic'],
            flood_risk_score=result['component_scores']['flood'],
            landslide_risk_score=result['component_scores']['landslide'],
            climate_risk_score=result['component_scores']['climate'],
            weights=result['weights']
        )
        response = _format_score_response(temp_score)
        global_cache.set(CACHE_KEY, response, TTL_SECONDS)
        return response
    except Exception as e:
        logger.error(f"Scoring error for municipality {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/omi-zone/{id}", response_model=InvestmentScoreResponse)
def get_omi_zone_score(id: int, db: Session = Depends(get_db)):
    """
    Retrieve or calculate investment score for an OMI zone.
    
    Similar to municipality scoring but provides granular, neighborhood-level
    investment analysis. OMI zones represent distinct urban areas with unique
    market dynamics (e.g., "Centro Storico" vs "Periferia" in Rome).
    
    **Parameters:**
    - **id**: OMI zone unique identifier
    
    **Returns:**
    - Complete scoring breakdown at OMI zone granularity
    - Includes municipality-level factors (demographics, risks)
    - Zone-specific factors (property prices, crime if available)
    
    **Use Cases:**
    - Hyperlocal investment targeting
    - Neighborhood comparison within same city
    - Identifying value pockets in major metros
    
    **Example Response:**
    ```json
    {
      "overall_score": 6.5,
      "score_category": "Good",
      "omi_zone_id": 4821,
      "omi_zone_code": "C3",
      "municipality_name": "Roma",
      "calculation_date": "2024-02-04",
      "component_scores": {...}
    }
    ```
    
    **Error Responses:**
    - **404**: OMI zone not found
    - **500**: Scoring engine error
    """
    cached = db.query(InvestmentScore).filter(
        InvestmentScore.omi_zone_id == id
    ).order_by(InvestmentScore.calculation_date.desc()).first()
    
    if cached:
        return _format_score_response(cached)
        
    try:
        result = engine.calculate_score(db, omi_zone_id=id)
        temp_score = InvestmentScore(
            omi_zone_id=id,
            overall_score=result['overall_score'],
            calculation_date=result['calculation_date'],
            price_trend_score=result['component_scores']['price_trend'],
            affordability_score=result['component_scores']['affordability'],
            rental_yield_score=result['component_scores']['rental_yield'],
            demographics_score=result['component_scores']['demographics'],
            crime_score=result['component_scores']['crime'],
            connectivity_score=result['component_scores']['connectivity'],
            digital_connectivity_score=result['component_scores']['digital_connectivity'],
            services_score=result['component_scores']['services'],
            air_quality_score=result['component_scores']['air_quality'],
            seismic_risk_score=result['component_scores']['seismic'],
            flood_risk_score=result['component_scores']['flood'],
            landslide_risk_score=result['component_scores']['landslide'],
            climate_risk_score=result['component_scores']['climate'],
            weights=result['weights']
        )
        return _format_score_response(temp_score)
    except Exception as e:
        logger.error(f"Scoring error for OMI zone {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/municipality/{id}/omi-zones", response_model=List[OMIZoneScoreResponse])
def get_municipality_omi_zone_scores(id: int, db: Session = Depends(get_db)):
    """
    Batch retrieve investment scores for all OMI zones in a municipality.

    Returns zone details, scores, and GeoJSON geometry for map rendering.
    Optimized endpoint for large municipalities with multiple micro-zones.

    **Use Cases:**
    - Display neighborhood score cards on municipality detail page
    - Render color-coded zone polygons on map
    - Compare investment potential across neighborhoods

    **Parameters:**
    - **id**: Municipality unique identifier

    **Returns:**
    - Array of OMI zones with:
      - Zone details (code, name, type)
      - Investment score (if calculated, null otherwise)
      - Centroid coordinates for markers
      - GeoJSON geometry for polygon rendering

    **Example Response:**
    ```json
    [
      {
        "zone_id": 42,
        "zone_code": "B1",
        "zone_name": "Centro Storico",
        "zone_type": "Centro",
        "municipality_id": 5190,
        "overall_score": 7.2,
        "score_category": "Good",
        "confidence": 0.85,
        "centroid": {"latitude": 41.9028, "longitude": 12.4964},
        "geometry": {"type": "MultiPolygon", "coordinates": [...]}
      }
    ]
    ```

    **Error Responses:**
    - **404**: Municipality not found
    """
    from geoalchemy2.shape import to_shape
    from shapely.geometry import mapping

    # Verify municipality exists
    mun = db.query(Municipality).filter(Municipality.id == id).first()
    if not mun:
        raise HTTPException(status_code=404, detail="Municipality not found")

    # Get all OMI zones for this municipality
    zones = db.query(OMIZone).filter(OMIZone.municipality_id == id).all()

    results = []
    for zone in zones:
        # Get cached score (most recent)
        cached = db.query(InvestmentScore).filter(
            InvestmentScore.omi_zone_id == zone.id
        ).order_by(InvestmentScore.calculation_date.desc()).first()

        # Convert geometry to GeoJSON
        geojson = None
        if zone.geometry:
            try:
                geojson = mapping(to_shape(zone.geometry))
            except Exception as e:
                logger.warning(f"Failed to convert geometry for zone {zone.id}: {e}")

        # Extract centroid coordinates
        centroid_coords = None
        if zone.centroid:
            try:
                centroid_shape = to_shape(zone.centroid)
                centroid_coords = {
                    "latitude": centroid_shape.y,
                    "longitude": centroid_shape.x
                }
            except Exception as e:
                logger.warning(f"Failed to extract centroid for zone {zone.id}: {e}")

        results.append({
            "zone_id": zone.id,
            "zone_code": zone.zone_code,
            "zone_name": zone.zone_name,
            "zone_type": zone.zone_type,
            "municipality_id": id,
            "overall_score": cached.overall_score if cached else None,
            "confidence": cached.confidence_score if cached else None,
            "centroid": centroid_coords,
            "geometry": geojson
        })

    return results


def _format_score_response(model: InvestmentScore):
    """Maps DB model fields to the enhanced InvestmentScoreResponse schema."""
    overall = model.overall_score
    
    # Generate insights
    strengths = []
    risks = []
    
    if model.price_trend_score > 7: strengths.append("Strong price growth trend")
    if model.rental_yield_score > 6: strengths.append("High rental yield potential")
    if model.seismic_risk_score > 8: strengths.append("Low seismic risk zone")
    if model.demographics_score > 7: strengths.append("Positive demographic growth")
    
    if model.affordability_score < 4: risks.append("Very high property entry prices")
    if model.climate_risk_score < 4: risks.append("Significant long-term climate risk")
    if model.crime_score < 4: risks.append("Higher than average crime statistics")
    
    # Recommendation logic
    if overall >= 8:
        recommend = "Excellent investment candidate with strong fundamentals."
    elif overall >= 6:
        recommend = "Good investment potential with some manageable risks."
    elif overall >= 4:
        recommend = "Moderate investment case, careful due diligence required."
    else:
        recommend = "High-risk investment candidate, fundamentals are weak."

    # Calculate confidence based on how many components have non-default data
    # (assuming 5.0 is the fallback for missing data)
    components = [
        model.price_trend_score, model.affordability_score, model.rental_yield_score,
        model.demographics_score, model.crime_score, model.seismic_risk_score,
        model.flood_risk_score, model.landslide_risk_score, model.climate_risk_score
    ]
    actual_data_points = sum(1 for c in components if c is not None and c != 5.0)
    confidence = max(0.4, min(1.0, actual_data_points / len(components))) if len(components) > 0 else 0.5

    return {
        "overall_score": overall,
        "score_category": None,  # Determined by Pydantic validator
        "municipality_id": model.municipality_id,
        "municipality_name": model.municipality.name if model.municipality else None,
        "omi_zone_id": model.omi_zone_id,
        "omi_zone_code": model.omi_zone.zone_code if model.omi_zone else None,
        "calculation_date": model.calculation_date,
        "weights": model.weights,
        "recommendation": recommend,
        "confidence": confidence,
        "strengths": strengths,
        "risk_factors": risks,
        "component_scores": {
            "price_trend": model.price_trend_score or 5.0,
            "affordability": model.affordability_score or 5.0,
            "rental_yield": model.rental_yield_score or 5.0,
            "demographics": model.demographics_score or 5.0,
            "crime": model.crime_score or 5.0,
            "connectivity": model.connectivity_score or 5.0,
            "digital_connectivity": model.digital_connectivity_score or 5.0,
            "services": model.services_score or 5.0,
            "air_quality": model.air_quality_score or 5.0,
            "seismic": model.seismic_risk_score or 5.0,
            "flood": model.flood_risk_score or 5.0,
            "landslide": model.landslide_risk_score or 5.0,
            "climate": model.climate_risk_score or 5.0
        }
    }
