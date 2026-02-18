import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseIngestor
from app.models.geography import Municipality
from app.models.risk import ClimateProjection

logger = logging.getLogger(__name__)

class ClimateIngestor(BaseIngestor):
    """
    Ingestor for Climate Projections.
    Expected source: Copernicus-derived CSV/Excel.
    """
    
    def fetch(self, source: str) -> pd.DataFrame:
        if source.endswith('.csv'):
            return pd.read_csv(source)
        elif source.endswith(('.xls', '.xlsx')):
            return pd.read_excel(source)
        else:
            raise ValueError(f"Unsupported file format: {source}")

    def transform(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Transforms Climate DataFrame into a list of database-ready records.
        """
        def _get_col(keywords: List[str]):
            for col in data.columns:
                if all(k.lower() in col.lower() for k in keywords):
                    return col
            return None

        col_mun_code = _get_col(["Codice", "Comune"]) or "Codice_Comune"
        col_scenario = _get_col(["Scenario"]) or "Scenario"
        col_year = _get_col(["Anno", "Target"]) or "Target_Year"
        
        transformed = []
        for _, row in data.iterrows():
            try:
                mun_code_raw = row.get(col_mun_code)
                if pd.isna(mun_code_raw): continue
                
                mun_code = str(int(float(mun_code_raw))).zfill(6)
                
                record = {
                    "municipality_code": mun_code,
                    "scenario": str(row.get(col_scenario, "RCP8.5")),
                    "target_year": int(row.get(col_year, 2050)),
                    "avg_temp_change": float(row.get("Avg_Temp_Change", 0)),
                    "max_temp_change": float(row.get("Max_Temp_Change", 0)),
                    "heatwave_days_increase": int(row.get("Heatwave_Days_Increase", 0)),
                    "avg_precipitation_change": float(row.get("Avg_Precipitation_Change", 0)),
                    "extreme_rainfall_increase": float(row.get("Extreme_Rainfall_Increase", 0)),
                    "drought_risk_increase": float(row.get("Drought_Risk_Increase", 0)),
                    "sea_level_rise_cm": float(row.get("Sea_Level_Rise_Cm", 0)),
                    "flood_risk_multiplier": float(row.get("Flood_Risk_Multiplier", 1.0)),
                }
                transformed.append(record)
            except Exception as e:
                logger.warning(f"Skipping climate row due to error: {e}")
            
        return transformed

    def load(self, transformed_data: List[Dict[str, Any]]) -> int:
        """
        Loads climate records into the database.
        """
        count = 0
        for data in transformed_data:
            # Resolve Municipality
            municipality = self.db.query(Municipality).filter(Municipality.code == data["municipality_code"]).first()
            if not municipality:
                continue
            
            # Check if record already exists for this scenario/year
            existing = self.db.query(ClimateProjection).filter(
                ClimateProjection.municipality_id == municipality.id,
                ClimateProjection.scenario == data["scenario"],
                ClimateProjection.target_year == data["target_year"]
            ).first()
            
            if not existing:
                projection = ClimateProjection(
                    municipality_id=municipality.id,
                    scenario=data["scenario"],
                    target_year=data["target_year"],
                    avg_temp_change=data["avg_temp_change"],
                    max_temp_change=data["max_temp_change"],
                    heatwave_days_increase=data["heatwave_days_increase"],
                    avg_precipitation_change=data["avg_precipitation_change"],
                    extreme_rainfall_increase=data["extreme_rainfall_increase"],
                    drought_risk_increase=data["drought_risk_increase"],
                    sea_level_rise_cm=data["sea_level_rise_cm"],
                    flood_risk_multiplier=data["flood_risk_multiplier"]
                )
                self.db.add(projection)
                count += 1
            
        self.db.commit()
        logger.info(f"Climate Ingestion complete. Records added: {count}")
        return count
