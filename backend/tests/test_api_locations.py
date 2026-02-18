"""
Integration tests for Location API endpoints.

Tests the location search, municipality retrieval, and listing endpoints.
"""

import pytest
from app.models.geography import Municipality


def test_search_location_found(client, sample_municipality):
    """Test location search with valid query returns results."""
    response = client.post(
        "/api/v1/locations/search",
        json={"query": "Test City"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert data["municipality"]["name"] == "Test City"
    assert data["municipality"]["code"] == "001001"


def test_search_location_not_found(client):
    """Test location search with invalid query."""
    response = client.post(
        "/api/v1/locations/search",
        json={"query": "Nonexistent City"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is False


def test_get_municipality_by_id(client, sample_municipality):
    """Test get municipality endpoint."""
    response = client.get(f"/api/v1/locations/municipalities/{sample_municipality.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test City"
    assert data["population"] == 100000
    assert data["area_sqkm"] == 50.0


def test_get_municipality_not_found(client):
    """Test municipality not found."""
    response = client.get("/api/v1/locations/municipalities/99999")
    assert response.status_code == 404


def test_list_municipalities(client, sample_municipality):
    """Test list municipalities endpoint."""
    response = client.get("/api/v1/locations/municipalities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(m["name"] == "Test City" for m in data)


def test_list_municipalities_with_limit(client, sample_municipality):
    """Test list municipalities with limit parameter."""
    response = client.get("/api/v1/locations/municipalities?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5


def test_get_regions(client, sample_region):
    """Test get regions endpoint."""
    response = client.get("/api/v1/locations/regions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(r["name"] == "Test Region" for r in data)


def test_get_provinces(client, sample_province):
    """Test get provinces endpoint."""
    response = client.get("/api/v1/locations/provinces")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(p["name"] == "Test Province" for p in data)
