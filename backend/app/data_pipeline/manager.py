from typing import Dict, Type
from sqlalchemy.orm import Session
from .ingestion.base import BaseIngestor
from .ingestion.omi import OMIIngestor

class DataPipelineManager:
    """
    Orchestrates the data ingestion process.
    Maps source types to their respective ingestors.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self._ingestors = {
            "omi": OMIIngestor(db),
            # Add more ingestors here (e.g., "census", "listings")
        }

    def run_ingestion(self, ingestor_type: str, source: str) -> int:
        """
        Runs a specific ingestion pipeline.
        """
        ingestor = self._ingestors.get(ingestor_type)
        if not ingestor:
            raise ValueError(f"No ingestor found for type: {ingestor_type}")
        
        return ingestor.run(source)
