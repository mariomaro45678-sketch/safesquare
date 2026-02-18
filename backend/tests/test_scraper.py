"""
Unit tests for scraper components.

Tests:
- ProxyPool rotation and failover
- HTML parsing (date, price, size)
- CasaScraper listing extraction
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock
import re


class TestProxyPool:
    """Test proxy rotation logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.italian_proxies = [
            {'http': 'http://user1:pass1@proxy1.it:8080', 'https': 'http://user1:pass1@proxy1.it:8080', 'type': 'rotating', 'country': 'Italy'},
            {'http': 'http://user2:pass2@proxy2.it:8080', 'https': 'http://user2:pass2@proxy2.it:8080', 'type': 'rotating', 'country': 'Italy'},
            {'http': 'http://user3:pass3@proxy3.it:8080', 'https': 'http://user3:pass3@proxy3.it:8080', 'type': 'rotating', 'country': 'Italy'},
        ]
        self.us_proxies = [
            {'http': 'http://ususer1:uspass1@proxy1.us:8080', 'https': 'http://ususer1:uspass1@proxy1.us:8080', 'type': 'sticky', 'country': 'US'},
            {'http': 'http://ususer2:uspass2@proxy2.us:8080', 'https': 'http://ususer2:uspass2@proxy2.us:8080', 'type': 'sticky', 'country': 'US'},
        ]
        self.config = {
            'max_consecutive_italian_failures': 3,
        }

    def test_proxy_pool_initialization(self):
        """Test ProxyPool initializes correctly."""
        from app.scrapers.base_scraper import ProxyPool

        pool = ProxyPool(self.italian_proxies, self.us_proxies, self.config)

        assert len(pool.italian_proxies) == 3
        assert len(pool.us_proxies) == 2
        assert pool.using_italian is True
        assert pool.italian_failures == 0

    def test_round_robin_italian_proxies(self):
        """Test round-robin selection of Italian proxies."""
        from app.scrapers.base_scraper import ProxyPool

        pool = ProxyPool(self.italian_proxies, self.us_proxies, self.config)

        # Get proxies in order
        proxy1, type1 = pool.get_next_proxy()
        proxy2, type2 = pool.get_next_proxy()
        proxy3, type3 = pool.get_next_proxy()
        proxy4, type4 = pool.get_next_proxy()  # Should wrap around

        assert type1 == "italian"
        assert type2 == "italian"
        assert type3 == "italian"
        assert type4 == "italian"

        # Verify round-robin
        assert proxy1['http'] == 'http://user1:pass1@proxy1.it:8080'
        assert proxy2['http'] == 'http://user2:pass2@proxy2.it:8080'
        assert proxy3['http'] == 'http://user3:pass3@proxy3.it:8080'
        assert proxy4['http'] == 'http://user1:pass1@proxy1.it:8080'

    def test_failover_to_us_after_max_failures(self):
        """Test automatic failover to US proxies after Italian failures."""
        from app.scrapers.base_scraper import ProxyPool

        pool = ProxyPool(self.italian_proxies, self.us_proxies, self.config)

        # Simulate failures up to threshold
        for _ in range(3):
            pool.mark_proxy_failed("italian", "403 Forbidden")

        # Next proxy should be US
        proxy, proxy_type = pool.get_next_proxy()

        assert proxy_type == "us"
        assert pool.using_italian is False

    def test_success_resets_failure_counter(self):
        """Test that success resets the Italian failure counter."""
        from app.scrapers.base_scraper import ProxyPool

        pool = ProxyPool(self.italian_proxies, self.us_proxies, self.config)

        # Add some failures
        pool.mark_proxy_failed("italian", "Timeout")
        pool.mark_proxy_failed("italian", "Timeout")
        assert pool.italian_failures == 2

        # Success should reset
        pool.mark_proxy_success("italian")
        assert pool.italian_failures == 0

    def test_us_proxy_blacklisting(self):
        """Test that failed US proxies get blacklisted."""
        from app.scrapers.base_scraper import ProxyPool

        pool = ProxyPool(self.italian_proxies, self.us_proxies, self.config)
        pool.using_italian = False  # Force US mode

        # Get first US proxy
        proxy1, _ = pool.get_next_proxy()

        # Mark it as failed
        pool.mark_proxy_failed("us", "Connection refused")

        # Blacklist should have one entry
        assert len(pool.us_blacklist) == 1

    def test_us_blacklist_reset_when_all_blacklisted(self):
        """Test that US blacklist resets when all proxies are blacklisted."""
        from app.scrapers.base_scraper import ProxyPool

        pool = ProxyPool(self.italian_proxies, self.us_proxies, self.config)
        pool.using_italian = False

        # Blacklist all US proxies
        for i in range(len(self.us_proxies)):
            pool.us_blacklist.add(i)

        # Getting next proxy should reset blacklist
        proxy, proxy_type = pool.get_next_proxy()

        assert len(pool.us_blacklist) == 0
        assert proxy_type == "us"


class TestDateParsing:
    """Test Italian date parsing."""

    def get_scraper_class(self):
        """Get CasaScraper for testing."""
        # We'll test the _parse_date method directly
        from app.scrapers.casa_scraper import CasaScraper
        return CasaScraper

    def test_parse_date_oggi(self):
        """Test parsing 'oggi' (today)."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()
            result = scraper._parse_date("Pubblicato oggi")
            assert result == date.today()

    def test_parse_date_ieri(self):
        """Test parsing 'ieri' (yesterday)."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()
            result = scraper._parse_date("inserito ieri")
            assert result == date.today() - timedelta(days=1)

    def test_parse_date_giorni_fa(self):
        """Test parsing 'X giorni fa' (X days ago)."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()

            result = scraper._parse_date("pubblicato 5 giorni fa")
            assert result == date.today() - timedelta(days=5)

            result = scraper._parse_date("3 giorno fa")
            assert result == date.today() - timedelta(days=3)

    def test_parse_date_settimane_fa(self):
        """Test parsing weeks ago."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()

            result = scraper._parse_date("una settimana fa")
            assert result == date.today() - timedelta(weeks=1)

            result = scraper._parse_date("2 settimane fa")
            assert result == date.today() - timedelta(weeks=2)

    def test_parse_date_mesi_fa(self):
        """Test parsing months ago."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()

            result = scraper._parse_date("un mese fa")
            assert result == date.today() - timedelta(days=30)

            result = scraper._parse_date("3 mesi fa")
            assert result == date.today() - timedelta(days=90)

    def test_parse_date_numeric_format(self):
        """Test parsing DD/MM/YYYY format."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()

            result = scraper._parse_date("pubblicato il 15/01/2025")
            assert result == date(2025, 1, 15)

            result = scraper._parse_date("data: 28-12-2024")
            assert result == date(2024, 12, 28)

    def test_parse_date_italian_month_name(self):
        """Test parsing Italian month names."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()

            result = scraper._parse_date("15 gennaio 2025")
            assert result == date(2025, 1, 15)

            result = scraper._parse_date("28 dicembre 2024")
            assert result == date(2024, 12, 28)

    def test_parse_date_fallback(self):
        """Test fallback to today for unparseable dates."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()

            result = scraper._parse_date("random text")
            assert result == date.today()

            result = scraper._parse_date("")
            assert result == date.today()


class TestPriceParsing:
    """Test price extraction from text."""

    def test_parse_price_euro_format(self):
        """Test parsing Euro formatted prices."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()

            # European format: dots for thousands
            assert scraper._parse_price("€ 250.000") == 250000.0
            assert scraper._parse_price("250.000 €") == 250000.0
            assert scraper._parse_price("EUR 1.500.000") == 1500000.0

    def test_parse_price_invalid(self):
        """Test that invalid prices return None."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()

            # Too low (below 10k)
            assert scraper._parse_price("€ 5.000") is None

            # Too high (above 10M)
            assert scraper._parse_price("€ 15.000.000") is None

            # No numbers
            assert scraper._parse_price("trattativa riservata") is None


class TestSizeParsing:
    """Test size extraction from text."""

    def test_parse_size_sqm(self):
        """Test parsing square meters."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()

            assert scraper._parse_size("85 mq") == 85
            assert scraper._parse_size("120 m²") == 120
            assert scraper._parse_size("75m2") == 75

    def test_parse_size_invalid(self):
        """Test that invalid sizes return None."""
        from app.scrapers.casa_scraper import CasaScraper

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()

            # Too small (below 20)
            assert scraper._parse_size("15 mq") is None

            # Too large (above 500)
            assert scraper._parse_size("600 mq") is None

            # No numbers
            assert scraper._parse_size("no size") is None


class TestListingExtraction:
    """Test listing card extraction."""

    def create_mock_card(self, url=None, title=None, price=None, size=None):
        """Create a mock BeautifulSoup card element."""
        from bs4 import BeautifulSoup

        html = f'''
        <article class="listing-card">
            <a href="{url or '/vendita/residenziale/roma/appartamento-123456'}">
                <h2>{title or 'Appartamento in vendita'}</h2>
            </a>
            <span class="price">{price or '€ 250.000'}</span>
            <span class="size">{size or '85 mq'}</span>
        </article>
        '''
        soup = BeautifulSoup(html, 'lxml')
        return soup.find('article')

    def test_extract_listing_preview_complete(self):
        """Test extracting complete listing data."""
        from app.scrapers.casa_scraper import CasaScraper
        from app.models.geography import Municipality

        # Create mock municipality
        mock_municipality = Mock(spec=Municipality)
        mock_municipality.id = 1

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()
            scraper.config = {'anti_detection': {'skip_listing_probability': 0}}

            card = self.create_mock_card()
            result = scraper._extract_listing_preview(card, mock_municipality)

            assert result is not None
            assert result['municipality_id'] == 1
            assert result['source_platform'] == 'casa_it'
            assert 'casa_it_' in result['source_id']
            assert result['title'] == 'Appartamento in vendita'
            assert result['price'] == 250000.0
            assert result['size_sqm'] == 85
            assert result['price_per_sqm'] == round(250000 / 85, 2)
            assert result['is_active'] is True

    def test_extract_listing_preview_missing_price(self):
        """Test extraction with missing price."""
        from app.scrapers.casa_scraper import CasaScraper
        from app.models.geography import Municipality

        mock_municipality = Mock(spec=Municipality)
        mock_municipality.id = 1

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()
            scraper.config = {'anti_detection': {'skip_listing_probability': 0}}

            card = self.create_mock_card(price='Trattativa riservata')
            result = scraper._extract_listing_preview(card, mock_municipality)

            assert result is not None
            assert result['price'] is None
            assert result['price_per_sqm'] is None

    def test_source_id_from_url(self):
        """Test source ID generation from URL."""
        from app.scrapers.casa_scraper import CasaScraper
        from app.models.geography import Municipality

        mock_municipality = Mock(spec=Municipality)
        mock_municipality.id = 1

        with patch.object(CasaScraper, '__init__', lambda x, y=None: None):
            scraper = CasaScraper()
            scraper.config = {'anti_detection': {'skip_listing_probability': 0}}

            # URL with numeric ID
            card = self.create_mock_card(url='/vendita/residenziale/roma/appartamento-id-789012')
            result = scraper._extract_listing_preview(card, mock_municipality)

            assert result is not None
            assert result['source_id'] == 'casa_it_789012'
