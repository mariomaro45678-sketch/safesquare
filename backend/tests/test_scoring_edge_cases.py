"""
Extended tests for ScoringEngine edge cases and data availability scenarios.
"""

import pytest
from datetime import date
from app.services.scoring_engine import ScoringEngine
from app.models.geography import Municipality
from app.models.property import PropertyPrice
from app.models.demographics import Demographics
from app.models.risk import SeismicRisk, FloodRisk


class TestScoringEngineEdgeCases:
    """Test ScoringEngine with various edge cases."""
    
    def test_score_with_empty_database(self, db_session):
        """Test scoring when municipality has no data at all."""
        # Create municipality with minimal data
        muni = Municipality(
            name="Empty City",
            code="999999",
            province_id=1,  # Assuming province exists from fixture
            population=10000
        )
        db_session.add(muni)
        db_session.commit()
        
        engine = ScoringEngine()
        result = engine.calculate_score(db_session, municipality_id=muni.id)
        
        # Should still return a score with fallback values
        assert 'overall_score' in result
        assert 1.0 <= result['overall_score'] <= 10.0
        
        # Confidence should be low due to missing data
        assert result['confidence_score'] < 0.3
    
    def test_score_with_partial_data(self, db_session, sample_municipality):
        """Test scoring with only some data available."""
        # Add only demographics data
        demo = Demographics(
            municipality_id=sample_municipality.id,
            total_population=100000,
            population_density=2000,
            median_age=42.0,
            population_growth_1y=1.5
        )
        db_session.add(demo)
        db_session.commit()
        
        engine = ScoringEngine()
        result = engine.calculate_score(
            db_session, 
            municipality_id=sample_municipality.id
        )
        
        # Should calculate score with partial data
        assert 'overall_score' in result
        assert 'component_scores' in result
        assert result['component_scores']['demographics'] > 0
        
        # Confidence should reflect partial availability
        assert 0.1 < result['confidence_score'] < 0.5
    
    def test_score_with_complete_data(
        self, 
        db_session, 
        sample_municipality
    ):
        """Test scoring with comprehensive data across all categories."""
        muni_id = sample_municipality.id
        
        # Add demographics
        demo = Demographics(
            municipality_id=muni_id,
            total_population=100000,
            population_density=2000,
            median_age=38.0,
            population_growth_1y=2.0,
            population_growth_3y=6.5
        )
        db_session.add(demo)
        
        # Add seismic risk
        seismic = SeismicRisk(
            municipality_id=muni_id,
            seismic_zone=4,  # Low risk
            peak_ground_acceleration=0.05,
            hazard_level="Low",
            risk_score=20.0
        )
        db_session.add(seismic)
        
        # Add flood risk
        flood = FloodRisk(
            municipality_id=muni_id,
            high_hazard_area_pct=2.0,
            risk_level="Low",
            risk_score=15.0
        )
        db_session.add(flood)
        
        db_session.commit()
        
        engine = ScoringEngine()
        result = engine.calculate_score(db_session, municipality_id=muni_id)
        
        # Should have higher confidence with complete data
        assert result['confidence_score'] > 0.3
        assert 'component_scores' in result
        
        # Verify all expected components are present
        components = result['component_scores']
        expected_keys = [
            'price_trend', 'affordability', 'rental_yield',
            'demographics', 'crime', 'seismic', 'flood',
            'landslide', 'climate', 'connectivity',
            'digital_connectivity', 'services', 'air_quality'
        ]
        for key in expected_keys:
            assert key in components
    
    def test_custom_weights_normalization(self, db_session, sample_municipality):
        """Test that custom weights are properly normalized."""
        engine = ScoringEngine()
        
        # Provide weights that don't sum to 1.0
        custom_weights = {
            'price_trend': 0.5,
            'demographics': 0.3,
            'seismic': 0.1
        }
        
        result = engine.calculate_score(
            db_session,
            municipality_id=sample_municipality.id,
            custom_weights=custom_weights
        )
        
        # Weights should be normalized
        weights = result['weights']
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.001  # Should sum to 1.0
    
    def test_invalid_municipality_id(self, db_session):
        """Test error handling for non-existent municipality."""
        engine = ScoringEngine()
        
        with pytest.raises(ValueError, match="not found"):
            engine.calculate_score(db_session, municipality_id=999999)
    
    def test_invalid_custom_weight_key(self, db_session, sample_municipality):
        """Test warning for unknown weight keys."""
        engine = ScoringEngine()
        
        custom_weights = {
            'invalid_key': 0.5,
            'price_trend': 0.5
        }
        
        # Should not raise error, but log warning
        result = engine.calculate_score(
            db_session,
            municipality_id=sample_municipality.id,
            custom_weights=custom_weights
        )
        
        assert 'overall_score' in result
    
    def test_negative_custom_weight(self, db_session, sample_municipality):
        """Test validation of negative weight values."""
        engine = ScoringEngine()
        
        custom_weights = {
            'price_trend': -0.5
        }
        
        with pytest.raises(ValueError, match="Invalid weight value"):
            engine.calculate_score(
                db_session,
                municipality_id=sample_municipality.id,
                custom_weights=custom_weights
            )
    
    def test_thread_safety_isolation(self, db_session, sample_municipality):
        """Test that custom weights don't affect default weights."""
        engine = ScoringEngine()
        
        # Store original default weights
        original_weights = engine.weights.copy()
        
        # Calculate with custom weights
        custom_weights = {'price_trend': 0.9, 'demographics': 0.1}
        result = engine.calculate_score(
            db_session,
            municipality_id=sample_municipality.id,
            custom_weights=custom_weights
        )
        
        # Verify engine's default weights weren't mutated
        assert engine.weights == original_weights
        
        # Verify result used custom weights
        assert result['weights']['price_trend'] > 0.5
    
    def test_score_consistency_multiple_calls(
        self, 
        db_session, 
        sample_municipality
    ):
        """Test that scoring is deterministic."""
        engine = ScoringEngine()
        
        result1 = engine.calculate_score(
            db_session,
            municipality_id=sample_municipality.id
        )
        result2 = engine.calculate_score(
            db_session,
            municipality_id=sample_municipality.id
        )
        
        # Scores should be identical
        assert result1['overall_score'] == result2['overall_score']
        assert result1['confidence_score'] == result2['confidence_score']
    
    def test_calculation_date_recorded(self, db_session, sample_municipality):
        """Test that calculation date is properly recorded."""
        engine = ScoringEngine()
        
        result = engine.calculate_score(
            db_session,
            municipality_id=sample_municipality.id
        )
        
        assert 'calculation_date' in result
        # Should be today's date
        assert result['calculation_date'] == date.today().isoformat()
