import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generator
import pandas as pd
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class BaseIngestor(ABC):
    """
    Abstract base class for all data ingestors.
    Following the ETL (Extract, Transform, Load) pattern.
    """
    
    def __init__(self, db: Session):
        self.db = db

    @abstractmethod
    def fetch(self, source: Any) -> Any:
        """
        Extract data from the source (e.g., file path, URL, API).
        """
        pass

    @abstractmethod
    def transform(self, data: Any) -> List[Dict[str, Any]]:
        """
        Clean and transform the raw data into a list of dictionaries 
        compatible with SQLAlchemy models.
        """
        pass

    @abstractmethod
    def load(self, transformed_data: List[Dict[str, Any]]) -> int:
        """
        Load the transformed data into the database.
        Returns the number of records inserted/updated.
        """
        pass

    def chunk_list(self, data: List[Any], chunk_size: int) -> Generator[List[Any], None, None]:
        """
        Yield successive n-sized chunks from data.
        """
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    def run(self, source: Any) -> int:
        """
        Execute the full ETL pipeline with timing.
        """
        start_time = time.time()
        logger.info(f"Starting ingestion process for {self.__class__.__name__}")
        
        raw_data = self.fetch(source)
        transformed_data = self.transform(raw_data)
        count = self.load(transformed_data)
        
        duration = time.time() - start_time
        logger.info(f"Ingestion complete. Processed {count} records in {duration:.2f} seconds.")
        return count
