"""Ingest cadastral parcel data from Agenzia delle Entrate bulk downloads.

Usage:
    python scripts/ingest_cadastral_maps.py <path_to_spatial_file>

    # Single file (GeoJSON, Shapefile, or GeoPackage):
    python scripts/ingest_cadastral_maps.py data/raw/cadastral/lazio_parcels.shp

    # Multiple files (process each archive sequentially):
    for f in data/raw/cadastral/*.shp; do
        python scripts/ingest_cadastral_maps.py "$f"
    done

Source:  https://www.agenziaentrate.gov.it/portale/download-massivo-cartografia-catastale
License: CC-BY 4.0 — must attribute "Agenzia delle Entrate" in the UI.
"""

import sys
import os
import logging
from app.core.database import SessionLocal
from app.data_pipeline.ingestion.cadastral import CadastralIngestor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run(source_path: str):
    if not os.path.exists(source_path):
        logger.error(f"Source file not found: {source_path}")
        sys.exit(1)

    db = SessionLocal()
    try:
        ingestor = CadastralIngestor(db)
        logger.info(f"Starting cadastral ingestion from {source_path}")
        count = ingestor.run(source_path)
        logger.info(f"Cadastral ingestion finished. New parcels inserted: {count}")
    except Exception as e:
        logger.error(f"Cadastral ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    run(sys.argv[1])
