import pandas as pd
import logging
from typing import Any

logger = logging.getLogger(__name__)

class DataNormalizer:
    """
    Utility for standardizing data formats (ISTAT codes, prices, percentages)
    """
    
    @staticmethod
    def normalize_municipality_code(code: Any) -> str:
        """
        Standardize ISTAT codes to 6-digit strings
        """
        try:
            if pd.isna(code):
                return ""
            return str(int(float(code))).zfill(6)
        except (ValueError, TypeError):
            return str(code).strip().zfill(6)
    
    @staticmethod
    def normalize_price(value: Any) -> float:
        """
        Parse Italian currency formats (e.g., 1.234,56 -> 1234.56)
        """
        try:
            if pd.isna(value) or value == "":
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            
            s = str(value).strip().replace('€', '').replace(' ', '')
            if ',' in s:
                s = s.replace('.', '').replace(',', '.')
            return float(s)
        except Exception as e:
            logger.debug(f"Price normalization fallback for {value}: {e}")
            return 0.0

    @staticmethod
    def normalize_percentage(value: Any) -> float:
        """
        Standardize percentage strings to floats (0-100)
        """
        try:
            if pd.isna(value):
                return 0.0
            return float(str(value).replace('%', '').replace(',', '.'))
        except Exception:
            return 0.0
