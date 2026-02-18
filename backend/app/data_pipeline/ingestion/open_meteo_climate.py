
import pandas as pd
import logging
import requests
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseIngestor
from app.models.geography import Municipality
from app.models.risk import ClimateProjection

logger = logging.getLogger(__name__)

class OpenMeteoClimateIngestor(BaseIngestor):
    """
    Ingestor for Climate Projections using Open-Meteo API.
    Provides downscaled CMIP6 projections (10km grid).
    """
    
    API_URL = "https://climate-api.open-meteo.com/v1/climate"
    
    def fetch(self, coordinates: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """
        Fetch climate data for a list of coordinates.
        Supports up to 50 locations per request.
        """
        results = []
        lats = [c['lat'] for c in coordinates]
        lons = [c['lon'] for c in coordinates]
        
        params = {
            "latitude": lats,
            "longitude": lons,
            "start_date": "2050-01-01",
            "end_date": "2050-12-31",
            "models": "CMCC_CM2_VHR4", # Italy-specific high-res model
            "daily": ["temperature_2m_mean", "temperature_2m_max", "precipitation_sum"],
            "timezone": "Europe/Rome"
        }
        
        try:
            response = requests.get(self.API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Handle list vs dict response (Open-Meteo returns a list for multi-coord)
            if not isinstance(data, list):
                data = [data]
                
            for i, entry in enumerate(data):
                results.append({
                    "meta": coordinates[i],
                    "daily": entry.get("daily", {})
                })
                
        except Exception as e:
            logger.error(f"Failed to fetch climate data from Open-Meteo: {e}")
            
        return results

    def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transforms Open-Meteo daily response into ClimateProjection records.
        """
        transformed = []
        for entry in raw_data:
            daily = entry.get("daily", {})
            if not daily: continue
            
            lat_lon_meta = entry["meta"]
            
            # Calculate metrics for 2050 projection
            avg_temp = sum(daily.get("temperature_2m_mean", [])) / len(daily.get("temperature_2m_mean", [1]))
            max_temp = max(daily.get("temperature_2m_max", [0]))
            extreme_heat_days = len([t for t in daily.get("temperature_2m_max", []) if t > 35])
            total_precip = sum(daily.get("precipitation_sum", []))
            
            # We assume baseline delta calculation is handled via comparison with historical means
            # For MVP, we'll store the projected absolute values and a placeholder for change
            # (In a full scale app, we'd fetch 2000-2020 too)
            
            record = {
                "municipality_id": lat_lon_meta["mun_id"],
                "scenario": "SSP5-8.5", # High emission scenario in CMIP6
                "target_year": 2050,
                "avg_temp_change": round(avg_temp - 14.5, 2), # Assuming 14.5 is Italian baseline mean
                "max_temp_change": round(max_temp - 32.0, 2),
                "heatwave_days_increase": extreme_heat_days,
                "avg_precipitation_change": round((total_precip / 800 - 1) * 100, 1), # 800mm baseline
                "extreme_rainfall_increase": round(total_precip / 10, 1),
                "drought_risk_increase": 5.5 if total_precip < 600 else 2.0,
                "sea_level_rise_cm": 0.0, # Handled elsewhere or via coastal risk
                "flood_risk_multiplier": 1.2 if total_precip > 1000 else 1.0,
                "projection_metadata": {
                    "model": "CMCC_CM2_VHR4",
                    "lat": lat_lon_meta["lat"],
                    "lon": lat_lon_meta["lon"],
                    "source": "Open-Meteo Climate API"
                }
            }
            transformed.append(record)
            
        return transformed

    def load(self, transformed_data: List[Dict[str, Any]]) -> int:
        count = 0
        for data in transformed_data:
            existing = self.db.query(ClimateProjection).filter(
                ClimateProjection.municipality_id == data["municipality_id"],
                ClimateProjection.scenario == data["scenario"],
                ClimateProjection.target_year == data["target_year"]
            ).first()
            
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
            else:
                projection = ClimateProjection(**data)
                self.db.add(projection)
                
            count += 1
            if count % 100 == 0:
                self.db.commit()
                
        self.db.commit()
        return count
