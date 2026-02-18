"""
Unit tests for Market Pulse Service.

Tests market metrics calculations:
- Active listings count
- Median days on market (DOM)
- Absorption rate
- Inventory months
- Average price per sqm
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session


@pytest.fixture
def sample_listings(db_session, sample_municipality):
    """Create sample listings for testing market metrics."""
    from app.models.listing import RealEstateListing

    listings = []

    # Active listings with varying DOM
    for i in range(5):
        listing = RealEstateListing(
            municipality_id=sample_municipality.id,
            source_id=f"casa_it_active_{i}",
            source_platform='casa_it',
            url=f"https://casa.it/listing/{i}",
            title=f"Test Listing {i}",
            price=200000 + i * 50000,
            size_sqm=80 + i * 10,
            price_per_sqm=(200000 + i * 50000) / (80 + i * 10),
            date_posted=date.today() - timedelta(days=10 + i * 5),
            is_active=True,
            days_on_market=10 + i * 5  # 10, 15, 20, 25, 30
        )
        listings.append(listing)
        db_session.add(listing)

    # Inactive (sold) listings - removed in last 30 days
    for i in range(3):
        listing = RealEstateListing(
            municipality_id=sample_municipality.id,
            source_id=f"casa_it_sold_{i}",
            source_platform='casa_it',
            url=f"https://casa.it/sold/{i}",
            title=f"Sold Listing {i}",
            price=250000,
            size_sqm=90,
            price_per_sqm=250000 / 90,
            date_posted=date.today() - timedelta(days=60),
            date_removed=date.today() - timedelta(days=5 + i * 5),  # Within 30 days
            is_active=False,
            days_on_market=55 - i * 5
        )
        listings.append(listing)
        db_session.add(listing)

    # Old inactive listings - removed more than 30 days ago (shouldn't count)
    listing = RealEstateListing(
        municipality_id=sample_municipality.id,
        source_id="casa_it_old_sold",
        source_platform='casa_it',
        url="https://casa.it/old_sold",
        title="Old Sold Listing",
        price=300000,
        size_sqm=100,
        price_per_sqm=3000,
        date_posted=date.today() - timedelta(days=120),
        date_removed=date.today() - timedelta(days=45),
        is_active=False,
        days_on_market=75
    )
    listings.append(listing)
    db_session.add(listing)

    db_session.commit()

    return listings


class TestActiveListingsCount:
    """Test active listings count calculation."""

    def test_count_active_listings(self, db_session, sample_municipality, sample_listings):
        """Test counting active listings."""
        from app.services.market_pulse_service import MarketPulseService

        # Patch to use test session
        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            count = service.get_active_listings_count(sample_municipality.id)

            assert count == 5  # 5 active listings

    def test_count_zero_when_no_listings(self, db_session, sample_municipality):
        """Test returns 0 when no listings exist."""
        from app.services.market_pulse_service import MarketPulseService

        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            count = service.get_active_listings_count(sample_municipality.id)

            assert count == 0


class TestMedianDOM:
    """Test median days on market calculation."""

    def test_median_dom_calculation(self, db_session, sample_municipality, sample_listings):
        """Test median DOM is calculated correctly."""
        from app.services.market_pulse_service import MarketPulseService

        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            median = service.get_median_dom(sample_municipality.id)

            # DOM values: 10, 15, 20, 25, 30 -> median = 20
            assert median == 20.0

    def test_median_dom_none_when_no_data(self, db_session, sample_municipality):
        """Test returns None when no DOM data."""
        from app.services.market_pulse_service import MarketPulseService

        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            median = service.get_median_dom(sample_municipality.id)

            assert median is None


class TestAbsorptionRate:
    """Test absorption rate (sold listings) calculation."""

    def test_absorption_rate_30_days(self, db_session, sample_municipality, sample_listings):
        """Test absorption rate counts only recent removals."""
        from app.services.market_pulse_service import MarketPulseService

        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            rate = service.get_absorption_rate(sample_municipality.id, days=30)

            # 3 listings removed within last 30 days
            assert rate == 3

    def test_absorption_rate_excludes_old(self, db_session, sample_municipality, sample_listings):
        """Test that old removals are excluded."""
        from app.services.market_pulse_service import MarketPulseService

        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            # Use 7 day window - should exclude some
            rate = service.get_absorption_rate(sample_municipality.id, days=7)

            # Only 1 listing removed within 7 days (at day 5)
            assert rate == 1


class TestInventoryMonths:
    """Test inventory months calculation."""

    def test_inventory_months_calculation(self, db_session, sample_municipality, sample_listings):
        """Test inventory months = active / absorption."""
        from app.services.market_pulse_service import MarketPulseService

        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            inventory = service.get_inventory_months(sample_municipality.id)

            # 5 active / 3 sold per month = 1.67 months
            assert inventory == round(5 / 3, 2)

    def test_inventory_months_none_when_no_sales(self, db_session, sample_municipality):
        """Test returns None when no absorption data."""
        from app.services.market_pulse_service import MarketPulseService
        from app.models.listing import RealEstateListing

        # Add only active listing, no sales
        listing = RealEstateListing(
            municipality_id=sample_municipality.id,
            source_id="casa_it_only_active",
            source_platform='casa_it',
            url="https://casa.it/only_active",
            title="Only Active",
            price=200000,
            size_sqm=80,
            price_per_sqm=2500,
            date_posted=date.today() - timedelta(days=10),
            is_active=True,
            days_on_market=10
        )
        db_session.add(listing)
        db_session.commit()

        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            inventory = service.get_inventory_months(sample_municipality.id)

            assert inventory is None  # No sales = no inventory calculation


class TestAveragePriceSqm:
    """Test average price per sqm calculation."""

    def test_avg_price_sqm_calculation(self, db_session, sample_municipality, sample_listings):
        """Test average price/sqm is calculated correctly."""
        from app.services.market_pulse_service import MarketPulseService

        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            avg = service.get_avg_price_sqm(sample_municipality.id)

            # Calculate expected average from active listings
            # Prices: 200k, 250k, 300k, 350k, 400k
            # Sizes: 80, 90, 100, 110, 120
            expected_price_per_sqm = [
                200000 / 80,
                250000 / 90,
                300000 / 100,
                350000 / 110,
                400000 / 120
            ]
            expected_avg = sum(expected_price_per_sqm) / len(expected_price_per_sqm)

            assert avg == round(expected_avg, 2)

    def test_avg_price_sqm_none_when_no_data(self, db_session, sample_municipality):
        """Test returns None when no price data."""
        from app.services.market_pulse_service import MarketPulseService

        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            avg = service.get_avg_price_sqm(sample_municipality.id)

            assert avg is None


class TestMarketPulseComplete:
    """Test complete market pulse response."""

    def test_get_market_pulse_all_metrics(self, db_session, sample_municipality, sample_listings):
        """Test complete market pulse returns all metrics."""
        from app.services.market_pulse_service import MarketPulseService

        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            pulse = service.get_market_pulse(sample_municipality.id)

            assert 'municipality_id' in pulse
            assert 'active_listings' in pulse
            assert 'median_dom' in pulse
            assert 'absorption_rate_per_month' in pulse
            assert 'inventory_months' in pulse
            assert 'avg_price_sqm' in pulse
            assert 'last_updated' in pulse

            assert pulse['municipality_id'] == sample_municipality.id
            assert pulse['active_listings'] == 5
            assert pulse['median_dom'] == 20.0
            assert pulse['absorption_rate_per_month'] == 3

    def test_market_pulse_platform_filtering(self, db_session, sample_municipality, sample_listings):
        """Test that platform filtering works."""
        from app.services.market_pulse_service import MarketPulseService
        from app.models.listing import RealEstateListing

        # Add listing from different platform
        other_listing = RealEstateListing(
            municipality_id=sample_municipality.id,
            source_id="immobiliare_123",
            source_platform='immobiliare_it',  # Different platform
            url="https://immobiliare.it/123",
            title="Other Platform Listing",
            price=500000,
            size_sqm=150,
            price_per_sqm=3333.33,
            date_posted=date.today() - timedelta(days=5),
            is_active=True,
            days_on_market=5
        )
        db_session.add(other_listing)
        db_session.commit()

        with patch('app.services.market_pulse_service.SessionLocal', return_value=db_session):
            service = MarketPulseService()
            service.db = db_session

            # Should only count casa_it listings
            pulse = service.get_market_pulse(sample_municipality.id, platform='casa_it')
            assert pulse['active_listings'] == 5

            # Should count immobiliare_it listings
            pulse_other = service.get_market_pulse(sample_municipality.id, platform='immobiliare_it')
            assert pulse_other['active_listings'] == 1
