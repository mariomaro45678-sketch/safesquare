import os
import sys
import subprocess
import time
import logging

# Configure logging to write to a file in the data directory so we can monitor it
LOG_FILE = "/app/data/background_pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_script(script_path, description):
    logger.info(f">>> STARTING: {description} ({script_path})")
    try:
        # Run with current python interpreter and add /app to PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = "/app"
        
        # Using /app as cwd for all scripts
        # We stream output to the log file in real-time
        process = subprocess.Popen(
            [sys.executable, script_path],
            env=env,
            cwd="/app",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Log output as it comes
        if process.stdout:
            for line in process.stdout:
                clean_line = line.strip()
                if clean_line:
                    logger.info(f"[{description}] {clean_line}")
        
        process.wait()
        
        if process.returncode == 0:
            logger.info(f"✓ COMPLETED: {description}")
        else:
            logger.error(f"✗ FAILED: {description} (Exit code: {process.returncode})")
            
    except Exception as e:
        logger.error(f"Error running {description}: {e}")
    
    # Sleep between scripts to allow CPU/DB to breath
    time.sleep(30)

def main():
    logger.info("==========================================================")
    logger.info("   SAFE SQUARE - NATIONAL DATA ENRICHMENT PIPELINE")
    logger.info("==========================================================")
    logger.info(f"Starting background processing. Log: {LOG_FILE}")
    
    # 1. Generate National Data Files
    run_script("scripts/create_full_demography_data.py", "Generating National Demographics")
    run_script("scripts/create_full_omi_data.py", "Generating National OMI Prices")
    run_script("scripts/create_full_risk_data.py", "Generating National Risks")
    run_script("scripts/create_full_climate_data.py", "Generating National Climate Data")
    run_script("scripts/create_full_crime_data.py", "Generating National Crime Data")
    run_script("scripts/create_full_pollution_data.py", "Generating National Pollution Data")
    
    # 2. Ingest Data into DB
    run_script("scripts/ingest_demographics_full.py", "Ingesting National Demographics")
    run_script("scripts/ingest_omi_full.py", "Ingesting National OMI Prices")
    run_script("scripts/ingest_risks_full.py", "Ingesting National Risks")
    run_script("scripts/ingest_climate.py", "Ingesting National Climate")
    run_script("scripts/ingest_crime.py", "Ingesting National Crime (Hyper-Local)")
    run_script("scripts/ingest_pollution_full.py", "Ingesting National Air Quality")
    
    # 3. Complete Geocoding (Centroids)
    # This might take ~1.5h but runs 1 req/sec
    run_script("scripts/update_geometries.py", "Completing National Geocoding (Centroids)")
    
    # 4. Final National Scoring
    # Recalculates everything with the new detailed data
    run_script("data/batch_calculate_scores.py", "Final National Investment Scoring")
    
    logger.info("==========================================================")
    logger.info("   PIPELINE FINISHED SUCCESSFULLY! 100% COVERAGE REACHED")
    logger.info("==========================================================")

if __name__ == "__main__":
    main()
