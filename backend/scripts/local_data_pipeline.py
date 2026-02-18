import os
import sys
import subprocess
import time
import logging

# Configure logging
LOG_FILE = "backend/logs/local_pipeline.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

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
        env = os.environ.copy()
        env["PYTHONPATH"] = "."
        
        process = subprocess.Popen(
            [sys.executable, script_path.replace("backend/", "")],
            env=env,
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
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
    
    time.sleep(5) # Short sleep for local execution

def main():
    logger.info("Starting local data enrichment pipeline...")
    
    # 1. Ingest Data into DB (Assume files already generated or use existing raw files)
    # Most of these 'ingest_*_full.py' scripts use pandas to read files from raw directory.
    # We need to make sure their paths are also fixed.
    
    scripts = [
        ("backend/scripts/ingest_demographics_full.py", "Ingesting National Demographics"),
        ("backend/scripts/ingest_omi_full.py", "Ingesting National OMI Prices"),
        ("backend/scripts/ingest_risks_full.py", "Ingesting National Risks"),
        ("backend/scripts/ingest_climate.py", "Ingesting National Climate"),
        ("backend/scripts/ingest_crime.py", "Ingesting National Crime"),
        ("backend/scripts/ingest_pollution_full.py", "Ingesting National Air Quality"),
        ("backend/scripts/ingest_services_overpass.py", "Ingesting Services (Hospitals/Schools)"),
        ("backend/scripts/ingest_transport_overpass.py", "Ingesting Transport (Stations/Exits)"),
        ("backend/scripts/ingest_broadband_agcom.py", "Ingesting Broadband Data")
    ]
    
    for path, desc in scripts:
        if os.path.exists(path):
            run_script(path, desc)
        else:
            logger.warning(f"Script not found: {path}")

    logger.info("Pipeline finished.")

if __name__ == "__main__":
    main()
