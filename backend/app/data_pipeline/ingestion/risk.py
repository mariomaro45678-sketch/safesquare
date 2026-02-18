import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseIngestor
from app.models.geography import Municipality
from app.models.risk import SeismicRisk, FloodRisk, LandslideRisk

logger = logging.getLogger(__name__)

class RiskIngestor(BaseIngestor):
    """
    Ingestor for environmental risk data (Seismic, Flood, Landslide).
    Source: ISPRA, INGV
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
        Transforms Risk DataFrame into a list of unified risk records.
        """
        def _get_col(keywords: List[str]):
            for col in data.columns:
                if all(k.lower() in col.lower() for k in keywords):
                    return col
            return None

        def _get_col_loose(keywords: List[str]):
            for col in data.columns:
                if any(k.lower() in col.lower() for k in keywords):
                    return col
            return None

        col_mun_code = _get_col(["Codice", "Comune"]) or _get_col_loose(["Comune"])
        col_risk_type = _get_col(["Tipo", "Rischio"]) or _get_col_loose(["Tipo"])
        col_level = _get_col(["Livello"]) or _get_col_loose(["Livello"])
        col_score = _get_col(["Score"]) or _get_col_loose(["Score"])

        logger.info(f"Detected columns: MunCode={col_mun_code}, RiskType={col_risk_type}, Level={col_level}, Score={col_score}")
        logger.info(f"Available columns: {data.columns.tolist()}")
        if not data.empty:
            logger.info(f"First row sample: {data.iloc[0].to_dict()}")

        transformed = []
        for _, row in data.iterrows():
            try:
                mun_code_raw = row.get(col_mun_code)
                if pd.isna(mun_code_raw): continue
                
                mun_code = str(int(float(mun_code_raw))).zfill(6)
                
                record = {
                    "municipality_code": mun_code,
                    "risk_type": str(row.get(col_risk_type)).lower(),
                    "level": str(row.get(col_level)),
                    "score": float(row.get(col_score, 0)),
                    "pga": float(row.get("PGA", 0)), # Optional for seismic
                    "area_pct": float(row.get("Area_Pct", 0)), # Optional for flood/landslide
                }
                transformed.append(record)
            except Exception as e:
                logger.warning(f"Skipping risk row due to error: {e}")
            
        return transformed

    def load(self, transformed_data: List[Dict[str, Any]]) -> int:
        """
        Loads risk records into the database with optimizations.
        """
        count = 0
        
        # 1. Pre-fetch Municipalities
        municipalities = {m.code: m.id for m in self.db.query(Municipality.code, Municipality.id).all()}
        
        # 2. Pre-fetch existing risk records (mun_id) to avoid duplicates
        existing_seismic = {r.municipality_id for r in self.db.query(SeismicRisk.municipality_id).all()}
        existing_flood = {r.municipality_id for r in self.db.query(FloodRisk.municipality_id).all()}
        existing_landslide = {r.municipality_id for r in self.db.query(LandslideRisk.municipality_id).all()}
        
        chunk_size = 500
        for chunk in self.chunk_list(transformed_data, chunk_size):
            for data in chunk:
                mun_id = municipalities.get(data["municipality_code"])
                if not mun_id:
                    continue
                
                risk_type = data["risk_type"]
                
                if "seismic" in risk_type and mun_id not in existing_seismic:
                    self._load_seismic(mun_id, data)
                    existing_seismic.add(mun_id)
                elif "flood" in risk_type and mun_id not in existing_flood:
                    self._load_flood(mun_id, data)
                    existing_flood.add(mun_id)
                elif "landslide" in risk_type and mun_id not in existing_landslide:
                    self._load_landslide(mun_id, data)
                    existing_landslide.add(mun_id)
                
                count += 1
            
            self.db.commit()
            logger.info(f"Batched {chunk_size} risk records...")
            
        logger.info(f"Risk Ingestion complete. Records processed: {count}")
        return count

    def _load_seismic(self, mun_id: int, data: Dict[str, Any]):
        risk = SeismicRisk(
            municipality_id=mun_id,
            seismic_zone=int(data["score"] / 25) + 1, # Mock zone mapping
            peak_ground_acceleration=data["pga"],
            hazard_level=data["level"],
            risk_score=data["score"]
        )
        self.db.add(risk)

    def _load_flood(self, mun_id: int, data: Dict[str, Any]):
        risk = FloodRisk(
            municipality_id=mun_id,
            high_hazard_area_pct=data["area_pct"],
            risk_level=data["level"],
            risk_score=data["score"]
        )
        self.db.add(risk)

    def _load_landslide(self, mun_id: int, data: Dict[str, Any]):
        risk = LandslideRisk(
            municipality_id=mun_id,
            high_hazard_area_pct=data["area_pct"],
            risk_level=data["level"],
            risk_score=data["score"]
        )
        self.db.add(risk)
