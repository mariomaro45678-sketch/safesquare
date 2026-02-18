
import json
import logging
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.geography import Municipality, OMIZone
from app.models.property import PropertyPrice, PropertyType
from app.models.demographics import Demographics, CrimeStatistics
from app.models.risk import SeismicRisk, FloodRisk, LandslideRisk, ClimateProjection, AirQuality

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_global_stats():
    db = SessionLocal()
    stats = {}
    
    try:
        logger.info("Calculating Global Stats for Z-Score Normalization...")
        
        # 1. Price Growth (YoY %)
        # Fetch recent prices joined with OMIZone to get municipality_id
        price_query = db.query(PropertyPrice.avg_price, OMIZone.municipality_id, PropertyPrice.year, PropertyPrice.semester)\
            .join(OMIZone)\
            .filter(PropertyPrice.property_type == PropertyType.RESIDENTIAL)\
            .filter(PropertyPrice.year >= 2021).all()
        
        growths = []
        mun_prices = {}
        for p in price_query:
            if p.municipality_id not in mun_prices: mun_prices[p.municipality_id] = []
            mun_prices[p.municipality_id].append(p)
            
        for m_id, p_list in mun_prices.items():
            sorted_p = sorted(p_list, key=lambda x: (x.year, x.semester), reverse=True)
            if len(sorted_p) >= 2:
                latest = sorted_p[0].avg_price
                oldest = sorted_p[-1].avg_price
                if oldest > 0:
                    growths.append((latest - oldest) / oldest * 100)
        
        stats['price_trend'] = {
            'mean': float(np.mean(growths)) if growths else 2.0,
            'std': float(np.std(growths)) if growths else 1.5
        }

        # 2. Income
        incomes = [d.avg_income_euro for d in db.query(Demographics.avg_income_euro).filter(Demographics.avg_income_euro != None).all()]
        stats['income'] = {
            'mean': float(np.mean(incomes)) if incomes else 21000,
            'std': float(np.std(incomes)) if incomes else 5000
        }

        # 3. Crime Index
        crimes = [c.crime_index for c in db.query(CrimeStatistics.crime_index).filter(CrimeStatistics.crime_index != None).all()]
        stats['crime'] = {
            'mean': float(np.mean(crimes)) if crimes else 50,
            'std': float(np.std(crimes)) if crimes else 15
        }

        # 4. Air Quality (PM2.5)
        aq = [a.pm25_avg for a in db.query(AirQuality.pm25_avg).filter(AirQuality.pm25_avg != None).all()]
        stats['air_quality'] = {
            'mean': float(np.mean(aq)) if aq else 15.0,
            'std': float(np.std(aq)) if aq else 5.0
        }

        # 5. Climate Heatwaves
        heatwaves = [c.heatwave_days_increase for c in db.query(ClimateProjection.heatwave_days_increase).filter(ClimateProjection.heatwave_days_increase != None).all()]
        stats['climate_heat'] = {
            'mean': float(np.mean(heatwaves)) if heatwaves else 10.0,
            'std': float(np.std(heatwaves)) if heatwaves else 5.0
        }

        # 6. Populations
        pops = [m.population for m in db.query(Municipality.population).filter(Municipality.population > 0).all()]
        stats['population'] = {
            'mean': float(np.mean(pops)) if pops else 7300,
            'std': float(np.std(pops)) if pops else 30000
        }

        # 7. Environmental Risks (Step 25+: Standardizing to Z-Score)
        # Seismic Risk (0-100)
        seismic = [r.risk_score for r in db.query(SeismicRisk.risk_score).filter(SeismicRisk.risk_score != None).all()]
        stats['seismic'] = {
            'mean': float(np.mean(seismic)) if seismic else 50.0,
            'std': float(np.std(seismic)) if seismic else 20.0
        }

        # Flood Risk (0-100)
        flood = [r.risk_score for r in db.query(FloodRisk.risk_score).filter(FloodRisk.risk_score != None).all()]
        stats['flood'] = {
            'mean': float(np.mean(flood)) if flood else 15.0,
            'std': float(np.std(flood)) if flood else 10.0
        }

        # Landslide Risk (0-100)
        landslide = [r.risk_score for r in db.query(LandslideRisk.risk_score).filter(LandslideRisk.risk_score != None).all()]
        stats['landslide'] = {
            'mean': float(np.mean(landslide)) if landslide else 15.0,
            'std': float(np.std(landslide)) if landslide else 10.0
        }

        # Save to file
        output_path = "app/services/global_stats.json"
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=4)
            
        logger.info(f"Global stats saved to {output_path}")
        
    finally:
        db.close()

if __name__ == "__main__":
    calculate_global_stats()
