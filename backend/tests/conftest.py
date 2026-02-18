"""
Pytest configuration for backend tests.

This module configures the test environment including:
- Test database setup with PostgreSQL/PostGIS
- FastAPI TestClient with dependency overrides
- Sample data fixtures for testing
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.models.base import Base
from app.core.database import get_db
from app.main import app

# Import all models to ensure they are registered with Base.metadata
from app.models import geography, property, demographics, risk, score, listing

# Test database URL - PostgreSQL with PostGIS for spatial testing
# Use environment variable or default to local test container
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://test_user:test_password@localhost:5433/test_property_db"
)


@pytest.fixture(scope="session")
def engine():
    """Create test database engine and tables."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create database session for tests with automatic rollback."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_region(db_session):
    """Create sample region for testing."""
    from app.models.geography import Region
    
    region = Region(
        name="Test Region",
        code="TR01"
    )
    db_session.add(region)
    db_session.commit()
    db_session.refresh(region)
    return region


@pytest.fixture
def sample_province(db_session, sample_region):
    """Create sample province for testing."""
    from app.models.geography import Province
    
    province = Province(
        name="Test Province",
        code="TP01",
        region_id=sample_region.id
    )
    db_session.add(province)
    db_session.commit()
    db_session.refresh(province)
    return province


@pytest.fixture
def sample_municipality(db_session, sample_province):
    """Create sample municipality for testing."""
    from app.models.geography import Municipality
    
    municipality = Municipality(
        name="Test City",
        code="001001",
        province_id=sample_province.id,
        population=100000,
        area_sqkm=50.0
    )
    db_session.add(municipality)
    db_session.commit()
    db_session.refresh(municipality)
    return municipality


@pytest.fixture
def sample_municipality_with_score(db_session, sample_municipality):
    """Create municipality with investment score."""
    from app.models.score import InvestmentScore
    
    score = InvestmentScore(
        municipality_id=sample_municipality.id,
        overall_score=7.5,
        price_trend_score=8.0,
        crime_score=7.0,
        demographics_score=7.5,
        connectivity_score=8.0,
        score_metadata={"category": "Good", "recommendation": "Recommended"}
    )
    db_session.add(score)
    db_session.commit()
    
    # Refresh to get the municipality with score relationship loaded
    db_session.refresh(sample_municipality)
    return sample_municipality
