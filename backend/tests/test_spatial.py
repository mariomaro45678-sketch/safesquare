"""
Integration tests for spatial queries using PostGIS.
Tests geocoding service and spatial resolution functionality.
"""

import pytest
from app.services.geocoding import GeocodingService
from app.models.geography import Municipality, OMIZone
from geoalchemy2.shape import from_shape
from shapely.geometry import Point, Polygon


@pytest.fixture
def geocoding_service():
    """Create geocoding service instance."""
    return GeocodingService()


@pytest.fixture
def sample_municipality_with_geometry(db_session, sample_municipality):
    """Create municipality with actual geometry for spatial testing."""
    # Create a polygon around Rome's coordinates (41.9028° N, 12.4964° E)
    # Small box around central Rome
    polygon = Polygon([
        (12.45, 41.85),  # SW corner
        (12.55, 41.85),  # SE corner
        (12.55, 41.95),  # NE corner
        (12.45, 41.95),  # NW corner
        (12.45, 41.85)   # Close polygon
    ])
    
    sample_municipality.geometry = from_shape(polygon, srid=4326)
    sample_municipality.centroid = from_shape(Point(12.4964, 41.9028), srid=4326)
    db_session.commit()
    db_session.refresh(sample_municipality)
    return sample_municipality


@pytest.fixture
def sample_omi_zone_with_geometry(db_session, sample_municipality_with_geometry):
    """Create OMI zone with geometry."""
    # Create a smaller polygon within the municipality
    zone_polygon = Polygon([
        (12.48, 41.88),
        (12.52, 41.88),
        (12.52, 41.92),
        (12.48, 41.92),
        (12.48, 41.88)
    ])
    
    zone = OMIZone(
        municipality_id=sample_municipality_with_geometry.id,
        zone_code="B1",
        zone_name="Central Zone",
        zone_type="Residenziale",
        geometry=from_shape(zone_polygon, srid=4326)
    )
    db_session.add(zone)
    db_session.commit()
    db_session.refresh(zone)
    return zone


class TestSpatialQueries:
    """Test spatial query functionality."""
    
    def test_find_municipality_by_coordinates(
        self, 
        db_session, 
        sample_municipality_with_geometry,
        geocoding_service
    ):
        """Test finding municipality containing specific coordinates."""
        # Point within the municipality polygon
        lat, lon = 41.9028, 12.4964
        
        result = geocoding_service.find_municipality_by_coordinates(
            db_session, lat, lon
        )
        
        assert result is not None
        assert result.id == sample_municipality_with_geometry.id
        assert result.name == "Test City"
    
    def test_find_municipality_outside_bounds(
        self,
        db_session,
        sample_municipality_with_geometry,
        geocoding_service
    ):
        """Test that coordinates outside municipality return None."""
        # Point far outside the municipality
        lat, lon = 45.4642, 9.1900  # Milan coordinates
        
        result = geocoding_service.find_municipality_by_coordinates(
            db_session, lat, lon
        )
        
        assert result is None
    
    def test_find_omi_zone_by_coordinates(
        self,
        db_session,
        sample_omi_zone_with_geometry,
        geocoding_service
    ):
        """Test finding OMI zone containing specific coordinates."""
        # Point within the OMI zone
        lat, lon = 41.90, 12.50
        
        result = geocoding_service.find_omi_zone_by_coordinates(
            db_session, lat, lon
        )
        
        assert result is not None
        assert result.zone_code == "B1"
        assert result.municipality_id == sample_omi_zone_with_geometry.municipality_id
    
    def test_find_omi_zone_outside_zone(
        self,
        db_session,
        sample_municipality_with_geometry,
        sample_omi_zone_with_geometry,
        geocoding_service
    ):
        """Test coordinates in municipality but outside specific OMI zone."""
        # Point in municipality but outside the OMI zone polygon
        lat, lon = 41.87, 12.47
        
        result = geocoding_service.find_omi_zone_by_coordinates(
            db_session, lat, lon
        )
        
        # Should return None as coordinates are outside the OMI zone
        assert result is None
    
    def test_find_municipality_by_name(
        self,
        db_session,
        sample_municipality,
        geocoding_service
    ):
        """Test finding municipality by name (case-insensitive)."""
        result = geocoding_service.find_municipality_by_name(
            db_session, "test city"
        )
        
        assert result is not None
        assert result.id == sample_municipality.id
    
    def test_find_municipality_by_partial_name(
        self,
        db_session,
        sample_municipality,
        geocoding_service
    ):
        """Test finding municipality with partial name match."""
        # Municipality is "Test City"
        result = geocoding_service.find_municipality_by_name(
            db_session, "Test"
        )
        
        assert result is not None
        assert result.name == "Test City"


class TestGeometryData:
    """Test geometry field storage and retrieval."""
    
    def test_municipality_centroid_storage(
        self,
        db_session,
        sample_municipality_with_geometry
    ):
        """Test that centroid is properly stored and retrieved."""
        muni = sample_municipality_with_geometry
        
        assert muni.centroid is not None
        
        # Convert to shapely to verify
        from geoalchemy2.shape import to_shape
        point = to_shape(muni.centroid)
        
        assert abs(point.x - 12.4964) < 0.001
        assert abs(point.y - 41.9028) < 0.001
    
    def test_municipality_geometry_storage(
        self,
        db_session,
        sample_municipality_with_geometry
    ):
        """Test that full geometry polygon is stored."""
        muni = sample_municipality_with_geometry
        
        assert muni.geometry is not None
        
        from geoalchemy2.shape import to_shape
        polygon = to_shape(muni.geometry)
        
        # Verify it's a polygon
        assert polygon.geom_type == "Polygon"
        
        # Verify bounds are approximately correct
        bounds = polygon.bounds  # (minx, miny, maxx, maxy)
        assert 12.4 < bounds[0] < 12.5  # min longitude
        assert 41.8 < bounds[1] < 41.9  # min latitude
