import sys
import os
import requests
import logging
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import SessionLocal
from app.models.geography import Municipality
from app.models.demographics import Demographics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def restore_real_data():
    db = SessionLocal()
    try:
        # 1. Fetch real population data (2023)
        logger.info("Fetching real population data from GitHub...")
        pop_url = "https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"
        resp = requests.get(pop_url)
        resp.raise_for_status()
        comuni_data = resp.json()
        
        # 2. Regional age distribution (approximations based on ISTAT 2023)
        # Form: {reg_code: (0-14%, 15-64%, 65+%)}
        regional_age_dist = {
            "01": (0.12, 0.63, 0.25), # Piemonte
            "02": (0.11, 0.61, 0.28), # Valle d'Aosta
            "03": (0.13, 0.64, 0.23), # Lombardia
            "05": (0.12, 0.64, 0.24), # Veneto
            "08": (0.12, 0.63, 0.25), # Emilia-Romagna
            "09": (0.11, 0.61, 0.28), # Toscana
            "12": (0.13, 0.65, 0.22), # Lazio
            "15": (0.14, 0.67, 0.19), # Campania
            "16": (0.13, 0.66, 0.21), # Puglia
            "19": (0.13, 0.65, 0.22), # Sicilia
            "DEFAULT": (0.12, 0.64, 0.24)
        }
        
        # 3. Income and other maps (kept from previous successful run)
        city_income_map = {
             "058091": 28602, "015146": 32545, "063049": 21856, "001272": 25433,
             "037006": 27244, "048017": 26865, "010025": 24987, "082053": 21344,
             "027042": 23677, "023091": 25890, "016024": 28455, "017029": 26844,
        }
        
        regional_avg_income = {
            "01": 22500, "03": 25300, "05": 23600, "08": 24200, "09": 24800, "12": 24100, "15": 18400, "19": 17500,
        }
        
        # 4. Ingest/Update
        municipalities = {m.code: (m.id, m.area_sqkm) for m in db.query(Municipality.code, Municipality.id, Municipality.area_sqkm).all()}
        
        count = 0
        for entry in comuni_data:
            code = str(entry.get('codice')).zfill(6)
            pop = entry.get('popolazione')
            reg_entry = entry.get('regione', {})
            reg_code = str(reg_entry.get('codice')).zfill(2) if isinstance(reg_entry, dict) else "DEFAULT"
            
            info = municipalities.get(code)
            if not info: continue
            mun_id, area = info
            
            # Resolve age distribution
            dist = regional_age_dist.get(reg_code, regional_age_dist["DEFAULT"])
            age_0_14 = int(pop * dist[0])
            age_15_64 = int(pop * dist[1])
            age_65_plus = pop - age_0_14 - age_15_64
            
            # Resolve income
            income = city_income_map.get(code) or regional_avg_income.get(reg_code, 20000)
                
            demo = db.query(Demographics).filter(Demographics.municipality_id == mun_id, Demographics.year == 2023).first()
            if not demo:
                demo = Demographics(
                    municipality_id=mun_id, year=2023, reference_date=date(2023, 1, 1),
                    total_population=pop, avg_income_euro=income,
                    age_0_14=age_0_14, age_15_64=age_15_64, age_65_plus=age_65_plus,
                    median_age=46.5 # placeholder
                )
                db.add(demo)
            else:
                demo.total_population = pop
                demo.avg_income_euro = income
                demo.age_0_14 = age_0_14
                demo.age_15_64 = age_15_64
                demo.age_65_plus = age_65_plus
                
            count += 1
            if count % 1000 == 0:
                db.commit()
                logger.info(f"Updated {count} municipalities...")
                
        db.commit()
        logger.info(f"Restoration with Age Data complete. Updated {count} records.")
        
    except Exception as e:
        logger.error(f"Restoration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    restore_real_data()
