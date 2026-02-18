import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from app.models.base import Base
from app.data_pipeline.ingestion.base import BaseIngestor
from app.data_pipeline.ingestion.omi import OMIIngestor
from app.data_pipeline.manager import DataPipelineManager
from app.models.geography import OMIZone
from app.models.property import PropertyPrice
import pandas as pd
import os

# Mock DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from unittest.mock import MagicMock

@pytest.fixture
def db():
    # Instead of real SQLite with GeoAlchemy issues, use a MagicMock for the session
    # or a very simple mock schema. Since we are testing logic, MagicMock is safer.
    session = MagicMock(spec=Session)
    return session

def test_base_ingestor_instantiation(db):
    """Verify BaseIngestor cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseIngestor(db)

def test_omi_ingestor_transform(db):
    """Verify OMIIngestor transformation logic."""
    ingestor = OMIIngestor(db)
    df = pd.DataFrame({
        "Codice_Zona": ["A1"],
        "Anno": [2023],
        "Semestre": [1],
        "Tipologia": ["Abitazioni"],
        "Stato_Mercato": ["Vendita"],
        "Valore_Minimo": [1000],
        "Valore_Massimo": [2000],
        "Stato_Conservazione": ["Ottimo"]
    })
    
    transformed = ingestor.transform(df)
    assert len(transformed) == 1
    assert transformed[0]["omi_zone_code"] == "A1"
    assert transformed[0]["year"] == 2023
    assert transformed[0]["min_price"] == 1000

def test_pipeline_manager_registration(db):
    """Verify ingestors are correctly registered in manager."""
    manager = DataPipelineManager(db)
    assert "omi" in manager._ingestors
    assert isinstance(manager._ingestors["omi"], OMIIngestor)
