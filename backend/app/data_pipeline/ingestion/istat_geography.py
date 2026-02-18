import pandas as pd
import requests
import io
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .base import BaseIngestor
from app.models.geography import Region, Province, Municipality

logger = logging.getLogger(__name__)

class ISTATGeographyIngestor(BaseIngestor):
    """
    Ingestor for Italian administrative hierarchy (Regions, Provinces, Municipalities).
    Source: ISTAT (Istituto Nazionale di Statistica)
    URL: https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv
    """
    
    ISTAT_URL = "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv"
    
    def fetch(self, source: str = None) -> pd.DataFrame:
        """
        Downloads the latest ISTAT municipality list.
        """
        url = source or self.ISTAT_URL
        logger.info(f"Downloading ISTAT geography data from {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        
        # ISTAT uses semicolon separator and latin-1 encoding usually
        try:
            df = pd.read_csv(io.StringIO(response.content.decode('latin-1')), sep=';')
        except UnicodeDecodeError:
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8-sig')), sep=';')
            
        logger.info(f"DataFrame loaded. Columns: {df.columns.tolist()}")
        logger.info(f"First row: {df.iloc[0].to_dict()}")
        return df

    def transform(self, data: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """
        Transforms ISTAT CSV into hierarchical records.
        """
        def _get_col(keywords: List[str]):
            for col in data.columns:
                if all(k.lower() in col.lower() for k in keywords):
                    return col
            return None

        col_reg_name = _get_col(["Denominazione", "Regione"])
        col_reg_code = _get_col(["Codice", "Regione"])
        col_prov_name = _get_col(["Denominazione", "territoriale", "sovracomunale"])
        col_prov_code = _get_col(["Codice", "territoriale", "sovracomunale"])
        col_mun_name = _get_col(["Denominazione in italiano"]) or _get_col(["Denominazione (Italiana)"])
        col_mun_code = _get_col(["Codice", "Comune", "alfanumerico"])

        logger.info(f"Detected columns: Reg={col_reg_name}, Prov={col_prov_name}, Mun={col_mun_name}")

        transformed = {
            "regions": [],
            "provinces": [],
            "municipalities": []
        }
        
        regions_seen = set()
        provinces_seen = set()
        
        def safe_strip(val):
            if pd.isna(val) or not isinstance(val, str):
                return str(val) if not pd.isna(val) else None
            return val.strip()

        for _, row in data.iterrows():
            # 1. Region
            reg_name = safe_strip(row.get(col_reg_name))
            reg_code_val = row.get(col_reg_code)
            if pd.isna(reg_code_val): continue
            reg_code = str(int(reg_code_val)).zfill(2)
            
            if reg_name and reg_code not in regions_seen:
                transformed["regions"].append({"name": reg_name, "code": reg_code})
                regions_seen.add(reg_code)
            
            # 2. Province
            prov_name = safe_strip(row.get(col_prov_name))
            prov_code_val = row.get(col_prov_code)
            if pd.isna(prov_code_val): continue
            prov_code = str(int(prov_code_val)).zfill(3)
            
            if prov_name and prov_code not in provinces_seen:
                transformed["provinces"].append({
                    "name": prov_name, 
                    "code": prov_code,
                    "region_code": reg_code
                })
                provinces_seen.add(prov_code)
                
            # 3. Municipality
            mun_name = safe_strip(row.get(col_mun_name))
            mun_code_val = row.get(col_mun_code)
            if pd.isna(mun_code_val): continue
            mun_code = str(mun_code_val).zfill(6)
            
            if mun_name and mun_code:
                transformed["municipalities"].append({
                    "name": mun_name,
                    "code": mun_code,
                    "province_code": prov_code
                })
                
        return transformed

    def load(self, transformed_data: Dict[str, List[Dict[str, Any]]]) -> int:
        """
        Loads hierarchical geography data into the database with optimizations.
        """
        count = 0
        
        # 1. Pre-fetch existing Regions
        existing_regions = {r.code: r for r in self.db.query(Region).all()}
        
        # Load New Regions
        for r_data in transformed_data["regions"]:
            if r_data["code"] not in existing_regions:
                region = Region(name=r_data["name"], code=r_data["code"])
                self.db.add(region)
                existing_regions[r_data["code"]] = region
                count += 1
        self.db.flush() 
        
        # 2. Pre-fetch existing Provinces
        existing_provinces = {p.code: p for p in self.db.query(Province).all()}
        
        # Load New Provinces
        for p_data in transformed_data["provinces"]:
            if p_data["code"] not in existing_provinces:
                region = existing_regions.get(p_data["region_code"])
                if region:
                    province = Province(name=p_data["name"], code=p_data["code"], region_id=region.id)
                    self.db.add(province)
                    existing_provinces[p_data["code"]] = province
                    count += 1
        self.db.flush()
        
        # 3. Load Municipalities in Batches
        # Pre-fetch existing Mun codes to avoid duplicates
        existing_mun_codes = {m.code for m in self.db.query(Municipality.code).all()}
        
        chunk_size = 500
        for chunk in self.chunk_list(transformed_data["municipalities"], chunk_size):
            for m_data in chunk:
                if m_data["code"] not in existing_mun_codes:
                    province = existing_provinces.get(m_data["province_code"])
                    if province:
                        mun = Municipality(name=m_data["name"], code=m_data["code"], province_id=province.id)
                        self.db.add(mun)
                        existing_mun_codes.add(m_data["code"])
                        count += 1
            
            # Commit each batch to keep memory and transaction log small
            self.db.commit()
            logger.info(f"Batched {chunk_size} municipalities...")
        
        logger.info(f"Geography Ingestion complete. Total new records created: {count}")
        return count
