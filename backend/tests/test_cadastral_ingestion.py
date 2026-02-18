"""Tests for cadastral parcel ingestion and the /locations/parcel endpoint.

Unit tests
----------
- CadastralParcel model unique-constraint enforcement.
- Transform step column detection and normalisation.

Integration tests
-----------------
- Full ingestor pipeline with a synthetic GeoDataFrame (mocks fetch).
- GET /locations/parcel endpoint: hit, miss, and OMI-linked cases.
"""

import pytest
import geopandas as gpd
from shapely.geometry import Polygon, Point
from geoalchemy2.shape import from_shape
from unittest.mock import patch

from app.models.geography import CadastralParcel, Municipality, OMIZone
from app.data_pipeline.ingestion.cadastral import CadastralIngestor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# A small polygon centred around (12.50, 41.90) — inside the "Rome-like" test
# municipality geometry used by conftest's sample_municipality_with_geometry.
PARCEL_POLY = Polygon([
    (12.49, 41.895),
    (12.51, 41.895),
    (12.51, 41.905),
    (12.49, 41.905),
    (12.49, 41.895),
])

# A second, non-overlapping parcel in the same municipality.
PARCEL_POLY_2 = Polygon([
    (12.46, 41.86),
    (12.48, 41.86),
    (12.48, 41.88),
    (12.46, 41.88),
    (12.46, 41.86),
])


def _make_test_gdf(foglio="101", particella="42", comune_code="001001", polygon=PARCEL_POLY):
    """Helper: build a one-row GeoDataFrame that mirrors the bulk-download schema."""
    return gpd.GeoDataFrame(
        {
            "foglio": [foglio],
            "particella": [particella],
            "codice_comune": [comune_code],
        },
        geometry=[polygon],
        crs="EPSG:4326",
    )


@pytest.fixture
def municipality_with_geometry(db_session, sample_municipality):
    """Municipality with a polygon that contains both test parcels."""
    polygon = Polygon([
        (12.45, 41.85),
        (12.55, 41.85),
        (12.55, 41.95),
        (12.45, 41.95),
        (12.45, 41.85),
    ])
    sample_municipality.geometry = from_shape(polygon, srid=4326)
    sample_municipality.centroid = from_shape(Point(12.50, 41.90), srid=4326)
    db_session.commit()
    db_session.refresh(sample_municipality)
    return sample_municipality


@pytest.fixture
def omi_zone_inside_parcel(db_session, municipality_with_geometry):
    """OMI zone whose geometry fully contains PARCEL_POLY."""
    zone_polygon = Polygon([
        (12.48, 41.88),
        (12.52, 41.88),
        (12.52, 41.92),
        (12.48, 41.92),
        (12.48, 41.88),
    ])
    zone = OMIZone(
        municipality_id=municipality_with_geometry.id,
        zone_code="TEST_B1",
        zone_name="Centro Test",
        zone_type="Centro",
        geometry=from_shape(zone_polygon, srid=4326),
    )
    db_session.add(zone)
    db_session.commit()
    db_session.refresh(zone)
    return zone


@pytest.fixture
def ingested_parcel(db_session, municipality_with_geometry, omi_zone_inside_parcel):
    """A single CadastralParcel already in the DB (skips the ingestor)."""
    parcel = CadastralParcel(
        municipality_id=municipality_with_geometry.id,
        omi_zone_id=omi_zone_inside_parcel.id,
        foglio="101",
        particella="42",
        geometry=from_shape(PARCEL_POLY, srid=4326),
    )
    db_session.add(parcel)
    db_session.commit()
    db_session.refresh(parcel)
    return parcel


# ---------------------------------------------------------------------------
# Unit tests — model constraints
# ---------------------------------------------------------------------------

class TestCadastralParcelModel:
    """CadastralParcel model constraint checks."""

    def test_unique_constraint_rejects_duplicate(self, db_session, municipality_with_geometry):
        """Inserting two parcels with same (municipality, foglio, particella) fails."""
        from sqlalchemy.exc import IntegrityError

        p1 = CadastralParcel(
            municipality_id=municipality_with_geometry.id,
            foglio="200",
            particella="1",
            geometry=from_shape(PARCEL_POLY, srid=4326),
        )
        db_session.add(p1)
        db_session.commit()

        p2 = CadastralParcel(
            municipality_id=municipality_with_geometry.id,
            foglio="200",
            particella="1",
            geometry=from_shape(PARCEL_POLY_2, srid=4326),
        )
        db_session.add(p2)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_different_particella_same_foglio_allowed(self, db_session, municipality_with_geometry):
        """Same foglio but different particella is valid."""
        db_session.add(CadastralParcel(
            municipality_id=municipality_with_geometry.id,
            foglio="300",
            particella="A",
            geometry=from_shape(PARCEL_POLY, srid=4326),
        ))
        db_session.add(CadastralParcel(
            municipality_id=municipality_with_geometry.id,
            foglio="300",
            particella="B",
            geometry=from_shape(PARCEL_POLY_2, srid=4326),
        ))
        db_session.commit()  # should not raise


# ---------------------------------------------------------------------------
# Unit tests — transform logic
# ---------------------------------------------------------------------------

class TestCadastralTransform:
    """CadastralIngestor.transform column detection and normalisation."""

    def test_transform_extracts_fields(self, db_session):
        gdf = _make_test_gdf(foglio="55", particella="99", comune_code="058091")
        ingestor = CadastralIngestor(db_session)
        records = ingestor.transform(gdf)

        assert len(records) == 1
        assert records[0]["foglio"] == "55"
        assert records[0]["particella"] == "99"
        assert records[0]["comune_code"] == "058091"
        assert "geometry_wkt" in records[0]

    def test_transform_skips_empty_geometry(self, db_session):
        from shapely.geometry import GeometryCollection
        gdf = gpd.GeoDataFrame(
            {"foglio": ["1"], "particella": ["2"], "codice_comune": ["001001"]},
            geometry=[GeometryCollection()],  # empty
            crs="EPSG:4326",
        )
        ingestor = CadastralIngestor(db_session)
        assert ingestor.transform(gdf) == []

    def test_transform_raises_on_missing_columns(self, db_session):
        gdf = gpd.GeoDataFrame(
            {"unrelated_col": ["x"]},
            geometry=[PARCEL_POLY],
            crs="EPSG:4326",
        )
        ingestor = CadastralIngestor(db_session)
        with pytest.raises(ValueError, match="foglio"):
            ingestor.transform(gdf)


# ---------------------------------------------------------------------------
# Integration tests — full ingestor pipeline (mocked fetch)
# ---------------------------------------------------------------------------

class TestCadastralIngestion:
    """End-to-end ingestion with a synthetic GeoDataFrame."""

    def test_ingest_single_parcel(self, db_session, municipality_with_geometry, omi_zone_inside_parcel):
        gdf = _make_test_gdf(foglio="101", particella="42", comune_code=municipality_with_geometry.code)
        ingestor = CadastralIngestor(db_session)

        # Bypass fetch — call transform + load directly
        records = ingestor.transform(gdf)
        count = ingestor.load(records)

        assert count == 1
        parcel = db_session.query(CadastralParcel).filter_by(foglio="101", particella="42").one()
        assert parcel.municipality_id == municipality_with_geometry.id
        assert parcel.omi_zone_id == omi_zone_inside_parcel.id

    def test_ingest_skips_duplicate_on_rerun(self, db_session, municipality_with_geometry, omi_zone_inside_parcel):
        gdf = _make_test_gdf(foglio="101", particella="42", comune_code=municipality_with_geometry.code)
        ingestor = CadastralIngestor(db_session)
        records = ingestor.transform(gdf)

        first_count = ingestor.load(records)
        second_count = ingestor.load(records)  # exact same data

        assert first_count == 1
        assert second_count == 0

    def test_ingest_parcel_without_omi_zone(self, db_session, municipality_with_geometry):
        """Parcel outside any OMI zone → omi_zone_id is NULL."""
        gdf = _make_test_gdf(foglio="999", particella="1", comune_code=municipality_with_geometry.code, polygon=PARCEL_POLY_2)
        ingestor = CadastralIngestor(db_session)
        records = ingestor.transform(gdf)
        count = ingestor.load(records)

        assert count == 1
        parcel = db_session.query(CadastralParcel).filter_by(foglio="999", particella="1").one()
        assert parcel.omi_zone_id is None


# ---------------------------------------------------------------------------
# Integration tests — GET /locations/parcel API endpoint
# ---------------------------------------------------------------------------

class TestParcelEndpoint:
    """HTTP-level tests for GET /api/v1/locations/parcel."""

    def test_parcel_found(self, client, ingested_parcel):
        """Point inside the parcel polygon → 200 with correct identifiers."""
        # Centre of PARCEL_POLY
        resp = client.get("/api/v1/locations/parcel", params={"lat": 41.90, "lon": 12.50})
        assert resp.status_code == 200
        body = resp.json()
        assert body["foglio"] == "101"
        assert body["particella"] == "42"
        assert body["linked_omi_zone"] is not None
        assert body["linked_omi_zone"]["zone_code"] == "TEST_B1"

    def test_parcel_not_found(self, client, ingested_parcel):
        """Point far from any ingested parcel → 404."""
        resp = client.get("/api/v1/locations/parcel", params={"lat": 45.46, "lon": 9.19})
        assert resp.status_code == 404

    def test_parcel_invalid_coordinates(self, client):
        """Coordinates outside valid range → 422 validation error."""
        resp = client.get("/api/v1/locations/parcel", params={"lat": 99, "lon": 0})
        assert resp.status_code == 422
