import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseIngestor
from app.models.geography import Municipality
from app.models.demographics import CrimeStatistics

logger = logging.getLogger(__name__)

class CrimeIngestor(BaseIngestor):
    """
    Ingestor for Crime Statistics.
    Expected source: CSV or Excel from ISTAT.
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
        Transforms Crime DataFrame into a list of database-ready records.
        """
        def _get_col(keywords: List[str]):
            for col in data.columns:
                if all(k.lower() in col.lower() for k in keywords):
                    return col
            return None

        col_mun_code = _get_col(["Codice", "Comune"]) or "Codice_Comune"
        col_year = _get_col(["Anno"]) or "Anno"
        col_total = _get_col(["Totale", "Reati"]) or "Total_Crimes_Per_1000"
        col_violent = _get_col(["Violenti"]) or "Violent_Crimes_Per_1000"
        col_property = _get_col(["Patrimonio"]) or "Property_Crimes_Per_1000"
        col_burglary = _get_col(["Burglary"]) or "Burglary_Rate"
        col_vandalism = _get_col(["Vandalism"]) or "Vandalism_Rate"
        col_theft = _get_col(["Theft"]) or "Theft_Rate"

        transformed = []
        for _, row in data.iterrows():
            try:
                mun_code_raw = row.get(col_mun_code)
                if pd.isna(mun_code_raw): continue
                
                mun_code = str(int(float(mun_code_raw))).zfill(6)
                
                record = {
                    "municipality_code": mun_code,
                    "year": int(row.get(col_year, 2022)),
                    "total_crimes_per_1000": float(row.get(col_total, 0)),
                    "violent_crimes_per_1000": float(row.get(col_violent, 0)),
                    "property_crimes_per_1000": float(row.get(col_property, 0)),
                    "burglary_rate": float(row.get(col_burglary, 0)),
                    "vandalism_rate": float(row.get(col_vandalism, 0)),
                    "theft_rate": float(row.get(col_theft, 0)),
                }
                
                # Derive crime index (normalized 0-100)
                record["crime_index"] = min(100.0, record["total_crimes_per_1000"] * 2) 
                
                transformed.append(record)
            except Exception as e:
                logger.warning(f"Skipping crime row due to error: {e}")
            
        return transformed

    def load(self, transformed_data: List[Dict[str, Any]]) -> int:
        """
        Loads crime records into the database.
        """
        count = 0
        for data in transformed_data:
            # Resolve Municipality
            municipality = self.db.query(Municipality).filter(Municipality.code == data["municipality_code"]).first()
            if not municipality:
                continue
            
            # Check if record already exists for this year
            existing = self.db.query(CrimeStatistics).filter(
                CrimeStatistics.municipality_id == municipality.id,
                CrimeStatistics.year == data["year"]
            ).first()
            
            if not existing:
                crime = CrimeStatistics(
                    municipality_id=municipality.id,
                    year=data["year"],
                    total_crimes_per_1000=data["total_crimes_per_1000"],
                    violent_crimes_per_1000=data["violent_crimes_per_1000"],
                    property_crimes_per_1000=data["property_crimes_per_1000"],
                    burglary_rate=data["burglary_rate"],
                    vandalism_rate=data["vandalism_rate"],
                    theft_rate=data["theft_rate"],
                    crime_index=data["crime_index"]
                )
                self.db.add(crime)
                count += 1
            else:
                # Update existing with new granular data
                existing.total_crimes_per_1000 = data["total_crimes_per_1000"]
                existing.violent_crimes_per_1000 = data["violent_crimes_per_1000"]
                existing.property_crimes_per_1000 = data["property_crimes_per_1000"]
                existing.burglary_rate = data["burglary_rate"]
                existing.vandalism_rate = data["vandalism_rate"]
                existing.theft_rate = data["theft_rate"]
                existing.crime_index = data["crime_index"]
                count += 1
            
        self.db.commit()
        logger.info(f"Crime Ingestion complete. Records added/updated: {count}")
        return count
