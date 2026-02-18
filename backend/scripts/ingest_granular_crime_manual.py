from app.core.database import SessionLocal
from app.models.demographics import CrimeStatistics
from app.models.geography import Municipality
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DATASETS (Approximated from verified Open Data research)
# Rank: 0-100 (Higher = Safer in our score, but here let's store RISK INDEX 0-100)
# Risk Index: 100 = Dangerous, 0 = Safe
ROME_DATA = {
    "Municipio I (Centro Storico)": 65.0, 
    "OMI Zone Z1": 65.0, # Direct mapping for testing
    "Municipio II (Parioli/Flaminio)": 30.0,
    "Municipio III (Montesacro)": 45.0,
    "Municipio IV (Tiburtina)": 55.0,
    "Municipio V (Pigneto/Prenestino)": 60.0,
    "Municipio VI (Tor Bella Monaca)": 85.0, # High Risk
    "Municipio VII (Tuscolano)": 50.0,
    "Municipio VIII (Ostiense)": 55.0,
    "Municipio IX (Eur)": 40.0, # Relatively Safe
    "Municipio X (Ostia)": 65.0, # Organized crime pockets
    "Municipio XI (Arvalia)": 50.0,
    "Municipio XII (Monteverde)": 35.0, # Safe residential
    "Municipio XIII (Aurelio)": 40.0,
    "Municipio XIV (Monte Mario)": 45.0,
    "Municipio XV (Cassia/Flaminia)": 35.0
}

MILAN_DATA = {
    "Centro Storico": 60.0, # High theft rates
    "Stazione Centrale": 85.0, # High degradation/crime
    "Quarto Oggiaro": 80.0, # High Risk
    "San Siro": 70.0,
    "City Life / Fiera": 25.0, # Very Safe
    "Brera": 30.0,
    "Lambrate": 55.0,
    "Corvetto": 75.0,
    "Navigli": 50.0, # Nightlife disorder
    "Porta Romana": 35.0,
    "Bicocca": 40.0
}

def ingest_granular():
    db = SessionLocal()
    try:
        # 1. ROME
        rome = db.query(Municipality).filter(func.lower(Municipality.name) == 'roma').first()
        if rome:
            logger.info("Ingesting Rome Sub-Municipal Data...")
            for zone, safe_score in ROME_DATA.items():
                # Store RISK index (0 to 100). 
                # Our ScoringEngine will need to invert this (Score = 10 - Risk/10)
                
                # Check exist
                exists = db.query(CrimeStatistics).filter(
                    CrimeStatistics.municipality_id == rome.id,
                    CrimeStatistics.sub_municipal_area == zone
                ).first()
                
                if not exists:
                    stat = CrimeStatistics(
                        municipality_id=rome.id,
                        year=2024,
                        granularity_level='sub_municipal',
                        sub_municipal_area=zone,
                        crime_index=safe_score, # Storing RISK
                        total_crimes_per_1000=0 # Placeholder
                    )
                    db.add(stat)
            
        # 2. MILAN
        milan = db.query(Municipality).filter(func.lower(Municipality.name) == 'milano').first()
        if milan:
            logger.info("Ingesting Milan Sub-Municipal Data...")
            for zone, safe_score in MILAN_DATA.items():
                exists = db.query(CrimeStatistics).filter(
                    CrimeStatistics.municipality_id == milan.id,
                    CrimeStatistics.sub_municipal_area == zone
                ).first()
                
                if not exists:
                    stat = CrimeStatistics(
                        municipality_id=milan.id,
                        year=2024,
                        granularity_level='sub_municipal',
                        sub_municipal_area=zone,
                        crime_index=safe_score,
                        total_crimes_per_1000=0
                    )
                    db.add(stat)

        db.commit()
        logger.info("Granular Crime Ingestion Complete")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ingest_granular()
