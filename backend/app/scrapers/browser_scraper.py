"""
Browser-based scraper using Playwright for CAPTCHA-protected sites.

This module provides headless Chrome automation to bypass Cloudflare
and other JavaScript-based bot detection systems. It integrates with
the existing proxy pool and anti-detection infrastructure.
"""

import asyncio
import random
import logging
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path

import yaml
import numpy as np

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    from playwright_stealth import stealth_async
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from .base_scraper import ProxyPool


class BrowserScraper:
    """
    Headless Chrome scraper with advanced anti-detection.

    Features:
    - Playwright stealth mode (evades headless detection)
    - Proxy rotation (Italian primary, US backup)
    - Session persistence (cookies)
    - CAPTCHA detection and handling
    - Human-like behavior simulation
    """

    def __init__(self, config_path: str = None):
        """
        Initialize browser scraper with configuration.

        Args:
            config_path: Path to YAML config file
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. Run: pip install playwright playwright-stealth && playwright install chromium"
            )

        if config_path is None:
            config_path = Path(__file__).parent / "scraper_config.yaml"

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.logger = self._setup_logging()

        # Load proxy pools
        self.proxy_pool = self._load_proxy_pools()

        # Rate limiting
        self.last_request_time = 0
        self.rate_limit = self.config['rate_limits']['casa_it_per_proxy']

        # Delays config
        self.delay_mean = self.config['rate_limits']['delay_mean_seconds']
        self.delay_std = self.config['rate_limits']['delay_std_dev_seconds']
        self.delay_min = self.config['rate_limits']['delay_min_seconds']
        self.delay_max = self.config['rate_limits']['delay_max_seconds']

        # Browser state
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Current proxy tracking
        self.current_proxy = None
        self.current_proxy_type = None

        # CAPTCHA handling
        self.captcha_wait_timeout = 120  # seconds to wait for manual CAPTCHA solve

        self.logger.info("BrowserScraper initialized")

    def _setup_logging(self) -> logging.Logger:
        """Configure logging."""
        import os
        log_config = self.config['logging']
        logger = logging.getLogger(f"{__name__}.browser")
        logger.setLevel(log_config['log_level'])

        # File handler — same log file as the base scraper so all activity is in one place
        os.makedirs('logs', exist_ok=True)
        fh = logging.FileHandler(log_config['log_file'])
        fh.setLevel(log_config['log_level'])

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(fh)
            logger.addHandler(ch)

        return logger

    def _load_proxy_pools(self) -> ProxyPool:
        """Load Italian and US proxy pools from config files."""
        proxy_config = self.config['proxy_config']

        # Resolve proxy file paths (relative to config directory or current working directory)
        def resolve_proxy_path(filepath: str) -> str:
            import os
            # If absolute path, use as-is
            if os.path.isabs(filepath):
                return filepath
            # Try relative to config file directory first
            config_dir = Path(__file__).parent
            config_relative = config_dir / filepath
            if config_relative.exists():
                return str(config_relative)
            # Try relative to current working directory
            cwd_relative = Path(filepath)
            if cwd_relative.exists():
                return str(cwd_relative)
            # Return original path (will fail with helpful error)
            return filepath

        # Load Italian proxies
        italian_file = resolve_proxy_path(proxy_config['italian_proxy_file'])
        italian_proxies = self._parse_proxy_file(italian_file)

        # Load US proxies
        us_file = resolve_proxy_path(proxy_config['us_proxy_file'])
        us_proxies = self._parse_proxy_file(us_file)

        self.logger.info(f"Loaded {len(italian_proxies)} Italian proxies, {len(us_proxies)} US proxies")

        return ProxyPool(italian_proxies, us_proxies, proxy_config)

    def _parse_proxy_file(self, filepath: str) -> List[Dict]:
        """Parse proxy file in format: username:password:hostname:port"""
        proxies = []

        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split(':')
                    if len(parts) == 4:
                        username, password, hostname, port = parts

                        proxies.append({
                            'server': f"http://{hostname}:{port}",
                            'username': username,
                            'password': password,
                            'hostname': hostname,
                            'port': port,
                        })
        except FileNotFoundError:
            self.logger.warning(f"Proxy file not found: {filepath}")

        return proxies

    def _get_proxy_config(self, proxy: Dict) -> Dict:
        """Convert proxy dict to Playwright format."""
        return {
            'server': proxy['server'],
            'username': proxy['username'],
            'password': proxy['password'],
        }

    async def init_browser(self, headless: bool = True):
        """
        Initialize Playwright browser with stealth settings.

        Args:
            headless: Run in headless mode (set False for debugging/manual CAPTCHA)
        """
        self.playwright = await async_playwright().start()

        # Get proxy
        proxy_dict, proxy_type = self.proxy_pool.get_next_proxy()
        self.current_proxy = proxy_dict
        self.current_proxy_type = proxy_type

        # Browser launch options
        launch_options = {
            'headless': headless,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--window-size=1920,1080',
                '--start-maximized',
            ]
        }

        # Add proxy if available
        if proxy_dict and 'server' in proxy_dict:
            launch_options['proxy'] = self._get_proxy_config(proxy_dict)
            self.logger.info(f"Using {proxy_type} proxy: {proxy_dict.get('hostname', 'unknown')}")

        self.browser = await self.playwright.chromium.launch(**launch_options)

        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self._get_user_agent(),
            locale='it-IT',
            timezone_id='Europe/Rome',
            geolocation={'latitude': 41.9028, 'longitude': 12.4964},  # Rome
            permissions=['geolocation'],
            java_script_enabled=True,
        )

        # Create page
        self.page = await self.context.new_page()

        # Apply stealth
        await stealth_async(self.page)

        # Set extra headers
        await self.page.set_extra_http_headers({
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        })

        self.logger.info(f"Browser initialized (headless={headless})")

    def _get_user_agent(self) -> str:
        """Get a realistic Chrome user agent."""
        user_agents = self.config['anti_detection']['user_agents']
        return random.choice(user_agents)

    async def rotate_proxy(self):
        """Rotate to next proxy (requires browser restart)."""
        self.logger.info("Rotating proxy...")

        await self.close()
        await self.init_browser()

    async def make_request(self, url: str, wait_until: str = 'domcontentloaded') -> str:
        """
        Navigate to URL and return page HTML.

        Args:
            url: Target URL
            wait_until: Playwright wait condition ('load', 'domcontentloaded', 'networkidle')

        Returns:
            HTML content of the page

        Raises:
            Exception: On navigation failure or CAPTCHA block
        """
        if not self.page:
            await self.init_browser()

        self.respect_rate_limit()

        try:
            self.logger.info(f"Navigating to: {url}")

            # Navigate with timeout
            response = await self.page.goto(
                url,
                wait_until=wait_until,
                timeout=30000  # 30 seconds
            )

            if response:
                status = response.status
                self.logger.info(f"Response status: {status}")

                if status == 403:
                    self.logger.warning("403 Forbidden - likely blocked")
                    self.proxy_pool.mark_proxy_failed(self.current_proxy_type, "403 Forbidden")
                    raise Exception("Blocked by site (403)")

                if status == 429:
                    self.logger.warning("429 Rate Limited")
                    self.proxy_pool.mark_proxy_failed(self.current_proxy_type, "429 Rate Limited")
                    raise Exception("Rate limited (429)")

            # Wait a moment for any lazy-loaded content
            await asyncio.sleep(0.5)

            # Check for CAPTCHA
            if await self._detect_captcha():
                self.logger.warning("CAPTCHA detected!")
                handled = await self._handle_captcha()
                if not handled:
                    self.proxy_pool.mark_proxy_failed(self.current_proxy_type, "CAPTCHA not solved")
                    raise Exception("CAPTCHA could not be solved")

            # Get page content
            html = await self.page.content()

            # Success
            self.proxy_pool.mark_proxy_success(self.current_proxy_type)

            return html

        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            raise

    async def _detect_captcha(self) -> bool:
        """
        Detect if page contains a CAPTCHA challenge.

        Returns:
            True if CAPTCHA is detected
        """
        content = await self.page.content()
        content_lower = content.lower()

        # Common CAPTCHA indicators
        captcha_indicators = [
            'cf-turnstile',          # Cloudflare Turnstile
            'h-captcha',             # hCaptcha
            'g-recaptcha',           # Google reCAPTCHA
            'captcha-container',
            'challenge-running',
            'challenge-form',
            'verify you are human',
            'verifica che sei un umano',  # Italian
            'controllo di sicurezza',     # Italian security check
            'accesso negato',             # Italian access denied
            'just a moment',              # Cloudflare waiting page
            'checking your browser',
            'please wait',
            'ddos protection',
        ]

        for indicator in captcha_indicators:
            if indicator in content_lower:
                self.logger.warning(f"CAPTCHA indicator found: {indicator}")
                return True

        # Check for Cloudflare challenge page by title
        title = await self.page.title()
        if title and any(x in title.lower() for x in ['just a moment', 'attention required', 'cloudflare']):
            self.logger.warning(f"CAPTCHA page detected via title: {title}")
            return True

        return False

    async def _handle_captcha(self) -> bool:
        """
        Handle CAPTCHA challenge.

        Currently implements:
        1. Wait for automatic challenge completion (Cloudflare JS)
        2. Manual intervention mode (if browser is visible)

        Returns:
            True if CAPTCHA was solved
        """
        self.logger.info("Attempting to handle CAPTCHA...")

        # First, wait for Cloudflare's automatic JS challenge
        # These usually complete in 2-5 seconds
        self.logger.info("Waiting for automatic challenge resolution...")

        for attempt in range(10):  # Wait up to 10 seconds
            await asyncio.sleep(1)

            if not await self._detect_captcha():
                self.logger.info("CAPTCHA resolved automatically!")
                return True

        # If still blocked, check if we need manual intervention
        self.logger.warning("Automatic resolution failed. Manual intervention may be required.")
        self.logger.warning(f"Waiting up to {self.captcha_wait_timeout} seconds for manual solve...")

        # Wait for manual solve (useful when running non-headless)
        start_time = time.time()
        while time.time() - start_time < self.captcha_wait_timeout:
            await asyncio.sleep(2)

            if not await self._detect_captcha():
                self.logger.info("CAPTCHA solved (manual intervention)!")
                return True

        self.logger.error("CAPTCHA timeout - could not be solved")
        return False

    def respect_rate_limit(self):
        """Ensure minimum time between requests."""
        elapsed = time.time() - self.last_request_time
        min_wait = 1.0 / self.rate_limit

        if elapsed < min_wait:
            time.sleep(min_wait - elapsed)

        self.last_request_time = time.time()

    async def human_delay(self):
        """Apply human-like delay using normal distribution."""
        delay = np.random.normal(self.delay_mean, self.delay_std)
        delay = max(self.delay_min, min(self.delay_max, delay))

        self.logger.debug(f"Sleeping for {delay:.2f}s")
        await asyncio.sleep(delay)

    async def simulate_human_behavior(self):
        """
        Perform random human-like actions on the page.

        Actions:
        - Random scrolling
        - Mouse movements
        - Random pauses
        """
        if not self.page:
            return

        actions = [
            self._random_scroll,
            self._random_mouse_move,
            self._random_pause,
        ]

        # Perform 1-3 random actions
        num_actions = random.randint(1, 3)
        for _ in range(num_actions):
            action = random.choice(actions)
            await action()

    async def _random_scroll(self):
        """Scroll to a random position on the page."""
        scroll_amount = random.randint(100, 500)
        direction = random.choice([1, -1])

        await self.page.evaluate(f"window.scrollBy(0, {scroll_amount * direction})")
        await asyncio.sleep(random.uniform(0.5, 1.5))

    async def _random_mouse_move(self):
        """Move mouse to a random position."""
        x = random.randint(100, 1800)
        y = random.randint(100, 900)

        await self.page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.1, 0.5))

    async def _random_pause(self):
        """Random short pause."""
        await asyncio.sleep(random.uniform(0.5, 2.0))

    async def save_cookies(self, filepath: str):
        """Save browser cookies to file for session persistence."""
        if self.context:
            cookies = await self.context.cookies()
            import json
            with open(filepath, 'w') as f:
                json.dump(cookies, f)
            self.logger.info(f"Saved {len(cookies)} cookies to {filepath}")

    async def load_cookies(self, filepath: str):
        """Load cookies from file."""
        if self.context:
            try:
                import json
                with open(filepath, 'r') as f:
                    cookies = json.load(f)
                await self.context.add_cookies(cookies)
                self.logger.info(f"Loaded {len(cookies)} cookies from {filepath}")
            except FileNotFoundError:
                self.logger.warning(f"Cookie file not found: {filepath}")

    async def take_screenshot(self, filepath: str):
        """Take screenshot for debugging."""
        if self.page:
            await self.page.screenshot(path=filepath)
            self.logger.info(f"Screenshot saved to {filepath}")

    async def close(self):
        """Close browser and cleanup resources."""
        if self.page:
            await self.page.close()
            self.page = None

        if self.context:
            await self.context.close()
            self.context = None

        if self.browser:
            await self.browser.close()
            self.browser = None

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

        self.logger.info("Browser closed")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Synchronous wrapper for compatibility with existing code
class SyncBrowserScraper:
    """
    Synchronous wrapper around BrowserScraper for use in non-async code.

    This allows the browser scraper to be used as a drop-in replacement
    for the curl_cffi-based BaseScraper.
    """

    def __init__(self, config_path: str = None):
        self._async_scraper = BrowserScraper(config_path)
        self._loop = None

    def _get_loop(self):
        """Get or create event loop."""
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop

    def init_browser(self, headless: bool = True):
        """Initialize browser synchronously."""
        loop = self._get_loop()
        loop.run_until_complete(self._async_scraper.init_browser(headless))

    def make_request(self, url: str) -> str:
        """Make request synchronously."""
        loop = self._get_loop()
        return loop.run_until_complete(self._async_scraper.make_request(url))

    def human_delay(self):
        """Human delay synchronously."""
        loop = self._get_loop()
        loop.run_until_complete(self._async_scraper.human_delay())

    def close(self):
        """Close browser synchronously."""
        loop = self._get_loop()
        loop.run_until_complete(self._async_scraper.close())

    @property
    def logger(self):
        return self._async_scraper.logger

    @property
    def config(self):
        return self._async_scraper.config
