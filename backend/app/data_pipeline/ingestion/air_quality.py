
import pandas as pd
import logging
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseIngestor
from app.models.geography import Municipality
from app.models.risk import AirQuality

logger = logging.getLogger(__name__)

class AirQualityIngestor(BaseIngestor):
    """
    Ingestor for Air Quality Data using Station Mapping.
    Source: Station-level measurements (Real or Synthetic) projected via mapping_comuni_arpa.json
    """
    
    from sqlalchemy.orm import Session

    def __init__(self, db: Session, data_dir: str = "./data"):
        super().__init__(db)
        self.mapping_file = Path(data_dir) / "mapping_comuni_arpa.json"
        self.mapping = self._load_mapping()
        
    def _load_mapping(self):
        if not self.mapping_file.exists():
            logger.warning(f"Mapping file not found at {self.mapping_file}")
            return {}
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load mapping file: {e}")
            return {}
    
    def fetch(self, source: str) -> pd.DataFrame:
        """
        Expects a file containing STATION-LEVEL data, not municipality level.
        Columns: station_id, PM2.5, PM10, NO2, Year
        """
        if source.endswith('.csv'):
            return pd.read_csv(source)
        elif source.endswith(('.xls', '.xlsx')):
            return pd.read_excel(source)
        else:
            raise ValueError(f"Unsupported file format: {source}")

    def transform(self, station_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Transforms Station Data -> Municipality Data using IDW Mapping
        """
        if not self.mapping:
            logger.error("No mapping available. Cannot transform.")
            return []
            
        # Convert station data to dict for fast lookup: {station_id: {measures}}
        stations_dict = {}
        for _, row in station_data.iterrows():
            s_id = str(row.get('Station_ID', '')).strip()
            if not s_id: continue
            
            stations_dict[s_id] = {
                'pm25': float(row.get('PM2.5', 0)),
                'pm10': float(row.get('PM10', 0)),
                'no2':  float(row.get('NO2', 0)),
                'year': int(row.get('Year', 2023))
            }
            
        transformed_records = []
        
        # Iterate over all mapped municipalities
        for mun_code, map_data in self.mapping.items():
            try:
                assigned_stations = map_data.get('stations', [])
                if not assigned_stations: continue
                
                # Weighted Average Calculation
                w_pm25, w_pm10, w_no2 = 0.0, 0.0, 0.0
                total_weight = 0.0
                station_count = 0
                
                for s in assigned_stations:
                    s_id = s['station_id']
                    weight = s['weight']
                    
                    if s_id in stations_dict:
                        data = stations_dict[s_id]
                        w_pm25 += data['pm25'] * weight
                        w_pm10 += data['pm10'] * weight
                        w_no2  += data['no2']  * weight
                        total_weight += weight
                        station_count += 1
                
                if total_weight > 0:
                    final_pm25 = w_pm25 / total_weight
                    final_pm10 = w_pm10 / total_weight
                    final_no2  = w_no2  / total_weight
                    
                    # Calculate AQI (Simplified)
                    # EU Scale: Good (0-20), Fair (20-40), Moderate (40-50), Poor (>50) for PM2.5
                    # Normalized 0-100 score where 0 is best
                    aqi = min(100, (final_pm25 * 2) + (final_no2 * 0.5))
                    
                    risk_level = "Low"
                    if aqi > 75: risk_level = "High"
                    elif aqi > 50: risk_level = "Moderate"
                    
                    record = {
                        "municipality_code": mun_code,
                        "pm25_avg": round(final_pm25, 2),
                        "pm10_avg": round(final_pm10, 2),
                        "no2_avg": round(final_no2, 2),
                        "aqi_index": round(aqi, 2),
                        "health_risk_level": risk_level,
                        "station_count": station_count,
                        "year": 2023, # Default or derive from data
                        "data_source": f"Interpolated from {station_count} ARPA stations"
                    }
                    transformed_records.append(record)
                    
            except Exception as e:
                logger.warning(f"Error processing municipality {mun_code}: {e}")
                continue
                
        return transformed_records

    def load(self, transformed_data: List[Dict[str, Any]]) -> int:
        count = 0
        # Pre-fetch municipalities for ID lookup
        mun_map = {m.code: m.id for m in self.db.query(Municipality.code, Municipality.id).all()}
        
        for data in transformed_data:
            mun_code = data["municipality_code"]
            if mun_code not in mun_map:
                continue
            
            mun_id = mun_map[mun_code]
            
            existing = self.db.query(AirQuality).filter(
                AirQuality.municipality_id == mun_id,
                AirQuality.year == data["year"]
            ).first()
            
            if not existing:
                aq = AirQuality(
                    municipality_id=mun_id,
                    pm25_avg=data["pm25_avg"],
                    pm10_avg=data["pm10_avg"],
                    no2_avg=data["no2_avg"],
                    aqi_index=data["aqi_index"],
                    health_risk_level=data["health_risk_level"],
                    station_count=data.get("station_count", 0),
                    year=data["year"],
                    data_source=data["data_source"]
                )
                self.db.add(aq)
                count += 1
            else:
                existing.pm25_avg = data["pm25_avg"]
                existing.pm10_avg = data["pm10_avg"]
                existing.no2_avg = data["no2_avg"]
                existing.aqi_index = data["aqi_index"]
                existing.health_risk_level = data["health_risk_level"]
                existing.station_count = data.get("station_count", 0)
                existing.data_source = data["data_source"]
            
        self.db.commit()
        logger.info(f"Air Quality Ingestion (Mapped) complete. Records: {count}")
        return count
