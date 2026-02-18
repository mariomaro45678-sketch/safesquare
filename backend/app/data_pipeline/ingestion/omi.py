import pandas as pd
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import date
import logging
from .base import BaseIngestor
from app.models.geography import OMIZone
from app.models.property import PropertyPrice, PropertyType, TransactionType

logger = logging.getLogger(__name__)

class OMIIngestor(BaseIngestor):
    """
    Ingestor for OMI (Osservatorio del Mercato Immobiliare) data.
    Expected source: Path to a CSV or Excel file containing OMI price data.
    """
    
    def fetch(self, source: str) -> pd.DataFrame:
        """
        Reads OMI data from a file.
        """
        if source.endswith('.csv'):
            return pd.read_csv(source)
        elif source.endswith(('.xls', '.xlsx')):
            return pd.read_excel(source)
        else:
            raise ValueError(f"Unsupported file format: {source}")

    def transform(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Transforms OMI DataFrame into a list of PropertyPrice records.
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

        col_zone = _get_col(["Zona", "OMI"]) or _get_col(["Zona"]) or _get_col_loose(["Zona"])
        col_mun_code = _get_col(["Codice", "Comune"]) or _get_col_loose(["Codice"])
        col_year = _get_col(["Anno"]) or _get_col_loose(["Anno"]) or "Anno"
        col_sem = _get_col(["Semestre"]) or _get_col_loose(["Semestre"]) or "Semestre"
        col_type = _get_col(["Tipologia"]) or _get_col_loose(["Tipologia"]) or "Tipologia"
        col_market = _get_col(["Stato", "Mercato"]) or _get_col_loose(["Mercato"]) or "Stato_Mercato"
        col_min = _get_col(["Valore", "Minimo"]) or _get_col_loose(["Minimo", "Min"]) or "Valore_Minimo"
        col_max = _get_col(["Valore", "Massimo"]) or _get_col_loose(["Massimo", "Max"]) or "Valore_Massimo"
        col_avg = _get_col(["Valore", "Medio"]) or _get_col_loose(["Medio", "Avg"]) or "Valore_Medio"
        col_state = _get_col(["Stato", "Conservazione"]) or _get_col_loose(["Conservazione"]) or "Stato_Conservazione"

        logger.info(f"Detected OMI columns: Zone={col_zone}, MunCode={col_mun_code}, Year={col_year}, Sem={col_sem}, Type={col_type}, Market={col_market}, Min={col_min}, Max={col_max}, State={col_state}")
        logger.info(f"Available OMI columns: {data.columns.tolist()}")
        if not data.empty:
            logger.info(f"First OMI row sample: {data.iloc[0].to_dict()}")

        transformed = []
        for _, row in data.iterrows():
            try:
                # 1. Resolve Zone Code (prefer Zona_OMI string)
                zone_code_raw = row.get(col_zone)
                if pd.isna(zone_code_raw):
                    continue
                zone_code = str(zone_code_raw).strip()
                
                # 2. Resolve Municipality Code for fallback creation
                mun_code_raw = row.get(col_mun_code)
                if isinstance(mun_code_raw, (float, int)):
                    mun_code = str(int(mun_code_raw)).zfill(6)
                else:
                    mun_code = str(mun_code_raw).strip().zfill(6)

                min_p_val = row.get(col_min, 0)
                max_p_val = row.get(col_max, 0)
                avg_p_val = row.get(col_avg)

                min_p = float(str(min_p_val).replace(',', '.')) if not pd.isna(min_p_val) else 0.0
                max_p = float(str(max_p_val).replace(',', '.')) if not pd.isna(max_p_val) else 0.0
                
                if not pd.isna(avg_p_val):
                    avg_p = float(str(avg_p_val).replace(',', '.'))
                else:
                    avg_p = (min_p + max_p) / 2
                
                year_val = row.get(col_year, 0)
                sem_val = row.get(col_sem, 0)
                
                record = {
                    "omi_zone_code": zone_code,
                    "municipality_code": mun_code,
                    "year": int(year_val) if not pd.isna(year_val) else 2022,
                    "semester": int(sem_val) if not pd.isna(sem_val) else 1,
                    "property_type": self._map_property_type(row.get(col_type)),
                    "transaction_type": self._map_transaction_type(row.get(col_market)),
                    "min_price": min_p,
                    "max_price": max_p,
                    "avg_price": avg_p,
                    "property_state": str(row.get(col_state, "Normale"))
                }
                transformed.append(record)
            except Exception as e:
                logger.warning(f"Skipping row due to error: {e}")
            
        return transformed

    def load(self, transformed_data: List[Dict[str, Any]]) -> int:
        """
        Loads OMI records into the database with optimizations.
        """
        count = 0
        from app.models.geography import Municipality
        
        # 1. Pre-fetch existing OMI Zones
        existing_zones = {z.zone_code: z for z in self.db.query(OMIZone).all()}
        
        # 2. Pre-fetch Municipalities for zone creation
        municipalities = {m.code: m for m in self.db.query(Municipality).all()}
        
        # 3. Pre-fetch existing PropertyPrice keys (zone_id, year, semester, type, trans)
        existing_prices = {
            (p.omi_zone_id, p.year, p.semester, p.property_type, p.transaction_type)
            for p in self.db.query(
                PropertyPrice.omi_zone_id, 
                PropertyPrice.year, 
                PropertyPrice.semester, 
                PropertyPrice.property_type, 
                PropertyPrice.transaction_type
            ).all()
        }
        
        chunk_size = 500
        for chunk in self.chunk_list(transformed_data, chunk_size):
            for data in chunk:
                # 1. Resolve OMI Zone
                zone_code = data["omi_zone_code"]
                zone = existing_zones.get(zone_code)
                
                if not zone:
                    istat_code = data.get("municipality_code")
                    municipality = municipalities.get(istat_code)
                    if municipality:
                        zone = OMIZone(
                            zone_code=zone_code,
                            municipality_id=municipality.id,
                            zone_name=f"OMI Zone {zone_code.split('_')[-1]} - {municipality.name}",
                            zone_type="Residenziale"
                        )
                        self.db.add(zone)
                        self.db.flush() # Get zone.id
                        existing_zones[zone_code] = zone
                    else:
                        logger.warning(f"Skipping record: Municipality {istat_code} not found for zone {zone_code}")
                        continue
                
                # 2. Check if price record exists
                key = (zone.id, data["year"], data["semester"], data["property_type"], data["transaction_type"])
                if key not in existing_prices:
                    price_record = PropertyPrice(
                        omi_zone_id=zone.id,
                        year=data["year"],
                        semester=data["semester"],
                        reference_date=date(data["year"], 6 if data["semester"] == 1 else 12, 1),
                        property_type=data["property_type"],
                        transaction_type=data["transaction_type"],
                        property_state=data["property_state"],
                        min_price=data["min_price"],
                        max_price=data["max_price"],
                        avg_price=data["avg_price"]
                    )
                    self.db.add(price_record)
                    existing_prices.add(key)
                    count += 1
            
            self.db.commit()
            logger.info(f"Batched {chunk_size} OMI records...")
            
        logger.info(f"OMI Ingestion complete. Records added: {count}")
        return count

    def _map_property_type(self, val: str) -> PropertyType:
        # Placeholder mapping
        val = str(val).lower()
        if "abitazion" in val:
            return PropertyType.RESIDENTIAL
        if "negoz" in val or "commercial" in val:
            return PropertyType.COMMERCIAL
        return PropertyType.RESIDENTIAL

    def _map_transaction_type(self, val: str) -> TransactionType:
        # Placeholder mapping
        val = str(val).lower()
        if "affitto" in val or "locazione" in val:
            return TransactionType.RENT
        return TransactionType.SALE
