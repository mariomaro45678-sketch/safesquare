import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date
from .base import BaseIngestor
from app.models.geography import Municipality
from app.models.demographics import Demographics

logger = logging.getLogger(__name__)

class ISTATDemographicsIngestor(BaseIngestor):
    """
    Ingestor for ISTAT demographic and socioeconomic data.
    Expected source: Path to a CSV or Excel file or a DataFrame.
    """
    
    def fetch(self, source: Any) -> pd.DataFrame:
        if isinstance(source, pd.DataFrame):
            return source
        if source.endswith('.csv'):
            return pd.read_csv(source)
        elif source.endswith(('.xls', '.xlsx')):
            return pd.read_excel(source)
        else:
            raise ValueError(f"Unsupported file format: {source}")

    def transform(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Transforms ISTAT DataFrame into Demographics records.
        Using column detection for flexibility.
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
        col_year = _get_col(["Anno"])
        col_pop = _get_col(["Popolazione", "Totale"]) or _get_col_loose(["Popolazione"])
        col_income = _get_col(["Reddito", "Medio"]) or _get_col_loose(["Reddito"])
        col_unemp = _get_col(["Tasso", "Disoccupazione"]) or _get_col_loose(["Disoccupazione"])

        logger.info(f"Detected columns: MunCode={col_mun_code}, Year={col_year}, Pop={col_pop}, Income={col_income}, Unemp={col_unemp}")
        logger.info(f"Available columns: {data.columns.tolist()}")
        if not data.empty:
            logger.info(f"First row sample: {data.iloc[0].to_dict()}")

        transformed = []
        for _, row in data.iterrows():
            try:
                mun_code_raw = row.get(col_mun_code)
                if pd.isna(mun_code_raw):
                    continue
                
                # Handle float/int codes (like 15146.0 -> "015146")
                if isinstance(mun_code_raw, (float, int)):
                    mun_code = str(int(mun_code_raw)).zfill(6)
                else:
                    mun_code = str(mun_code_raw).strip().zfill(6)

                year_val = row.get(col_year) if col_year else 2022
                year = int(year_val) if not pd.isna(year_val) else 2022
                if year == 0:
                    year = 2022

                record = {
                    "municipality_code": mun_code,
                    "year": year,
                    "total_population": int(row.get(col_pop, 0)),
                    "avg_income_euro": float(row.get(col_income, 0)),
                    "unemployment_rate": float(row.get(col_unemp, 0)),
                }
                transformed.append(record)
            except Exception as e:
                logger.warning(f"Skipping row due to error: {e}")
            
        return transformed

    def load(self, transformed_data: List[Dict[str, Any]]) -> int:
        """
        Loads demographics records into the database with optimizations.
        """
        count = 0
        
        # 1. Pre-fetch Municipalities for fast lookup
        municipalities = {m.code: m.id for m in self.db.query(Municipality.code, Municipality.id).all()}
        
        # 2. Pre-fetch existing demographics (mun_id, year) to avoid "exists" queries
        existing_keys = {
            (d.municipality_id, d.year) 
            for d in self.db.query(Demographics.municipality_id, Demographics.year).all()
        }
        
        chunk_size = 500
        for chunk in self.chunk_list(transformed_data, chunk_size):
            for data in chunk:
                mun_code = data["municipality_code"]
                mun_id = municipalities.get(mun_code)
                
                if not mun_id:
                    logger.warning(f"Municipality not found for code {mun_code}")
                    continue
                
                key = (mun_id, data["year"])
                if key not in existing_keys:
                    demo_record = Demographics(
                        municipality_id=mun_id,
                        year=data["year"],
                        reference_date=date(data["year"], 12, 31),
                        total_population=data["total_population"],
                        avg_income_euro=data["avg_income_euro"],
                        unemployment_rate=data["unemployment_rate"]
                    )
                    self.db.add(demo_record)
                    existing_keys.add(key)
                    count += 1
                else:
                    # Optional: Batch update existing records if needed
                    # For simplicity, we skip updating in this optimized version 
                    # unless explicitly required, or we could use bulk_update_mappings
                    pass
            
            self.db.commit()
            logger.info(f"Batched {chunk_size} demographics records...")
            
        logger.info(f"Demographics Ingestion complete. Records added: {count}")
        return count
