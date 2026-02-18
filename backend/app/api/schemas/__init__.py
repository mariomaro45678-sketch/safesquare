from .location import (
    LocationSearchRequest,
    LocationSearchResponse,
    MunicipalityResponse,
    OMIZoneResponse,
    CoordinatesResponse
)
from .property import (
    PropertyPriceResponse,
    PropertyPriceHistoryResponse,
    PropertyStatistics
)
from .score import (
    InvestmentScoreResponse,
    ScoreComponentsResponse,
    ScoreCalculationRequest
)
from .risk import (
    RiskSummaryResponse,
    SeismicRiskResponse,
    FloodRiskResponse,
    LandslideRiskResponse,
    ClimateProjectionResponse
)
from .demographics import (
    DemographicsResponse,
    CrimeStatisticsResponse
)

__all__ = [
    "LocationSearchRequest",
    "LocationSearchResponse",
    "MunicipalityResponse",
    "OMIZoneResponse",
    "CoordinatesResponse",
    "PropertyPriceResponse",
    "PropertyPriceHistoryResponse",
    "PropertyStatistics",
    "InvestmentScoreResponse",
    "ScoreComponentsResponse",
    "ScoreCalculationRequest",
    "RiskSummaryResponse",
    "SeismicRiskResponse",
    "FloodRiskResponse",
    "LandslideRiskResponse",
    "ClimateProjectionResponse",
    "DemographicsResponse",
    "CrimeStatisticsResponse",
]
