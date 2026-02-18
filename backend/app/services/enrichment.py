from sqlalchemy.orm import Session
from app.models.geography import Municipality, OMIZone
from app.models.property import PropertyPrice
from app.models.score import InvestmentScore
from datetime import date
from typing import List, Optional

class DataEnrichmentService:
    """
    Service to calculate investment scores and enrich property data 
    with risk and demographic information.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def calculate_municipality_scores(self, municipality_id: int) -> Optional[InvestmentScore]:
        """
        Calculates the overall investment score for a municipality.
        Combines price trends, demographics, and risk factors.
        """
        municipality = self.db.query(Municipality).filter(Municipality.id == municipality_id).first()
        if not municipality:
            return None
        
        # 1. Price Trend Score (Placeholder logic)
        price_score = self._calculate_price_trend_score(municipality_id)
        
        # 2. Risk Score (Placeholder logic)
        risk_score = self._calculate_risk_score(municipality_id)
        
        # 3. Demographic Score (Placeholder logic)
        dem_score = self._calculate_demographic_score(municipality_id)
        
        # 4. Overall Score (Weighted average)
        overall = (price_score * 0.4) + (dem_score * 0.3) + (risk_score * 0.3)
        
        investment_score = InvestmentScore(
            municipality_id=municipality_id,
            overall_score=overall,
            calculation_date=date.today(),
            price_trend_score=price_score,
            demographics_score=dem_score,
            seismic_risk_score=risk_score, # For simplicity
            weights={
                "price": 0.4,
                "demographics": 0.3,
                "risk": 0.3
            }
        )
        
        self.db.add(investment_score)
        self.db.commit()
        return investment_score

    def _calculate_price_trend_score(self, municipality_id: int) -> float:
        # Placeholder: Return a random score between 0 and 100 for now
        import random
        return random.uniform(50, 90)

    def _calculate_risk_score(self, municipality_id: int) -> float:
        # Placeholder: Lower is better for risk, but we invert it for the score
        return 75.0

    def _calculate_demographic_score(self, municipality_id: int) -> float:
        # Placeholder
        return 80.0
