# Testing Guide

## Setup

### 1. Start Test Database
```bash
cd backend
docker-compose -f docker-compose.test.yml up -d
```

Wait for the database to be ready:
```bash
docker-compose -f docker-compose.test.yml ps
```

### 2. Run Tests

Run all tests:
```bash
pytest
```

Run specific test files:
```bash
pytest tests/test_spatial.py
pytest tests/test_scoring_edge_cases.py
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### 3. Stop Test Database
```bash
docker-compose -f docker-compose.test.yml down
```

## Test Structure

- `tests/conftest.py` - Pytest configuration and fixtures
- `tests/test_spatial.py` - PostGIS spatial query tests
- `tests/test_scoring_edge_cases.py` - ScoringEngine edge cases
- `tests/test_api_locations.py` - Location API tests
- `tests/test_scoring_engine.py` - Core scoring tests

## Environment Variables

Set `TEST_DATABASE_URL` to override default:
```bash
export TEST_DATABASE_URL="postgresql://test_user:test_password@localhost:5433/test_property_db"
```
