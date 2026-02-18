"""
Base scraper class with enterprise-grade anti-detection capabilities.

Provides shared functionality for all scrapers:
- Proxy pool management (Italian primary, US backup)
- TLS fingerprinting prevention
- ML-based human delays
- Request retry logic with exponential backoff
- Realistic header generation
"""

import os
import time
import random
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
import yaml
from curl_cffi import requests
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from bs4 import BeautifulSoup


class ProxyPool:
    """Manages proxy rotation with priority-based failover."""
    
    def __init__(self, italian_proxies: List[Dict], us_proxies: List[Dict], config: Dict):
        self.italian_proxies = italian_proxies
        self.us_proxies = us_proxies
        self.config = config
        
        self.italian_index = 0
        self.us_index = 0
        
        self.italian_failures = 0
        self.max_italian_failures = config.get('max_consecutive_italian_failures', 5)
        
        # Blacklist for dead proxies
        self.italian_blacklist = set()
        self.us_blacklist = set()
        
        self.using_italian = True  # Start with Italian proxies
        
        self.logger = logging.getLogger(__name__)
    
    def get_next_proxy(self) -> Tuple[Dict, str]:
        """
        Get next proxy with priority-based selection.
        
        Returns:
            tuple: (proxy_dict, proxy_type)
        """
        # Try Italian proxies first
        if self.using_italian and len(self.italian_blacklist) < len(self.italian_proxies):
            proxy = self._get_next_italian()
            if proxy:
                return proxy, "italian"
        
        # Failover to US proxies
        self.logger.warning("Failing over to US proxies")
        self.using_italian = False
        return self._get_next_us(), "us"
    
    def _get_next_italian(self) -> Optional[Dict]:
        """Round-robin through Italian proxies."""
        attempts = 0
        while attempts < len(self.italian_proxies):
            proxy = self.italian_proxies[self.italian_index]
            self.italian_index = (self.italian_index + 1) % len(self.italian_proxies)
            
            if self.italian_index not in self.italian_blacklist:
                return proxy
            attempts += 1
        
        return None  # All Italian proxies blacklisted
    
    def _get_next_us(self) -> Dict:
        """Round-robin through US proxies."""
        attempts = 0
        while attempts < len(self.us_proxies):
            proxy = self.us_proxies[self.us_index]
            self.us_index = (self.us_index + 1) % len(self.us_proxies)
            
            if self.us_index not in self.us_blacklist:
                return proxy
            attempts += 1
        
        # If all blacklisted, reset and try again
        self.logger.warning("All US proxies blacklisted, resetting...")
        self.us_blacklist.clear()
        return self.us_proxies[0]
    
    def mark_proxy_failed(self, proxy_type: str, reason: str):
        """Handle proxy failure."""
        if proxy_type == "italian":
            self.italian_failures += 1
            self.logger.warning(f"Italian proxy failed ({self.italian_failures}/{self.max_italian_failures}): {reason}")
            
            if self.italian_failures >= self.max_italian_failures:
                self.logger.error("Max Italian proxy failures reached, switching to US pool")
                self.using_italian = False
        else:
            # For US, blacklist current proxy
            if self.us_index > 0:
                failed_index = self.us_index - 1
            else:
                failed_index = len(self.us_proxies) - 1
            
            self.us_blacklist.add(failed_index)
            self.logger.warning(f"US proxy {failed_index} blacklisted: {reason}")
    
    def mark_proxy_success(self, proxy_type: str):
        """Reset failure counter on success."""
        if proxy_type == "italian":
            if self.italian_failures > 0:
                self.italian_failures = 0
                self.logger.info("Italian proxy success, resetting failure counter")


class BaseScraper:
    """
    Enterprise-grade base scraper with advanced anti-detection.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize scraper with configuration.
        
        Args:
            config_path: Path to YAML config file
        """
        if config_path is None:
            config_path = Path(__file__).parent / "scraper_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.logger = self._setup_logging()
        self.ua = UserAgent()
        
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
        
        # Anti-detection config
        self.user_agents = self.config['anti_detection']['user_agents']
        self.accept_languages = self.config['anti_detection']['accept_languages']
        self.referers = self.config['anti_detection']['referers']
        
        self.logger.info("BaseScraper initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Configure logging with proxy context."""
        log_config = self.config['logging']
        logger = logging.getLogger(__name__)
        logger.setLevel(log_config['log_level'])
        
        # File handler
        os.makedirs('logs', exist_ok=True)
        fh = logging.FileHandler(log_config['log_file'])
        fh.setLevel(log_config['log_level'])
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        return logger
    
    def _load_proxy_pools(self) -> ProxyPool:
        """Load Italian and US proxy pools from config files."""
        proxy_config = self.config['proxy_config']

        # Resolve proxy file paths (relative to config directory or current working directory)
        def resolve_proxy_path(filepath: str) -> str:
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
        italian_proxies = self._parse_proxy_file(italian_file, proxy_type="rotating", country="Italy")

        # Load US proxies
        us_file = resolve_proxy_path(proxy_config['us_proxy_file'])
        us_proxies = self._parse_proxy_file(us_file, proxy_type="sticky", country="US")

        self.logger.info(f"Loaded {len(italian_proxies)} Italian proxies, {len(us_proxies)} US proxies")

        return ProxyPool(italian_proxies, us_proxies, proxy_config)
    
    def _parse_proxy_file(self, filepath: str, proxy_type: str, country: str) -> List[Dict]:
        """
        Parse proxy file in format: username:password:hostname:port
        
        Args:
            filepath: Path to proxy file
            proxy_type: 'rotating' or 'sticky'
            country: Country code
        
        Returns:
            List of proxy dicts
        """
        proxies = []
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(':')
                if len(parts) == 4:
                    username, password, hostname, port = parts
                    
                    proxy_url = f"http://{username}:{password}@{hostname}:{port}"
                    
                    proxies.append({
                        'http': proxy_url,
                        'https': proxy_url,
                        'type': proxy_type,
                        'country': country,
                        'username': username
                    })
        
        return proxies
    
    def generate_headers(self, url: str) -> Dict[str, str]:
        """
        Generate realistic browser headers.
        """
        user_agent = random.choice(self.user_agents)
        referer = random.choice(self.referers)
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': referer,
        }
        
        # Determine browser from UA for sec-ch-ua
        # Only add for Chrome/Chromium to match curl_cffi impersonation
        if 'Chrome' in user_agent:
             # Basic high-entropy not needed, simple version is safer to avoid mismatch
             headers['sec-ch-ua'] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
             headers['sec-ch-ua-mobile'] = '?0'
             headers['sec-ch-ua-platform'] = '"Windows"' if 'Windows' in user_agent else '"macOS"'
        
        return headers
    
    def human_delay(self):
        """
        Apply ML-based human-like delay using normal distribution.
        
        Uses mean and std dev from config to simulate realistic browsing patterns.
        """
        delay = np.random.normal(self.delay_mean, self.delay_std)
        delay = max(self.delay_min, min(self.delay_max, delay))
        
        self.logger.debug(f"Sleeping for {delay:.2f}s")
        time.sleep(delay)
    
    def respect_rate_limit(self):
        """Ensure minimum time between requests."""
        elapsed = time.time() - self.last_request_time
        min_wait = 1.0 / self.rate_limit
        
        if elapsed < min_wait:
            time.sleep(min_wait - elapsed)
        
        self.last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(12),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception))
    )
    def make_request(self, url: str, method: str = 'GET', **kwargs):
        """
        Make HTTP request with proxy rotation and anti-detection.
        
        Args:
            url: Target URL
            method: HTTP method
            **kwargs: Additional requests parameters
        
        Returns:
            Response object
        
        Raises:
            requests.RequestException: On repeated failures
        """
        self.respect_rate_limit()
        
        # Get proxy
        proxy, proxy_type = self.proxy_pool.get_next_proxy()
        
        # Generate headers
        headers = self.generate_headers(url)
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        
        # Use curl_cffi for TLS fingerprinting
        try:
            session = requests.Session()
            
            response = session.request(
                method=method,
                url=url,
                headers=headers,
                proxies=proxy,
                timeout=self.config['proxy_config']['proxy_timeout'],
                impersonate="chrome110",  # TLS fingerprint mimicry
                **kwargs
            )
            
            # Check for bot detection
            if response.status_code == 403:
                self.logger.warning(f"403 Forbidden - proxy {proxy_type} blocked")
                self.proxy_pool.mark_proxy_failed(proxy_type, "403 Forbidden")
                raise Exception("Proxy blocked (403)")
            
            if response.status_code == 429:
                self.logger.warning(f"429 Too Many Requests - proxy {proxy_type} rate limited")
                self.proxy_pool.mark_proxy_failed(proxy_type, "429 Rate Limited")
                raise Exception("Rate limited (429)")
            
            if 'captcha' in response.text.lower():
                self.logger.error(f"CAPTCHA detected on {url}")
                self.proxy_pool.mark_proxy_failed(proxy_type, "CAPTCHA detected")
                raise Exception("CAPTCHA triggered")
            
            response.raise_for_status()
            
            # Success!
            self.proxy_pool.mark_proxy_success(proxy_type)
            self.logger.info(f"[{proxy_type}] {method} {url} - {response.status_code}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            raise
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content with BeautifulSoup.
        
        Args:
            html: HTML string
        
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')
    
    def simulate_human_behavior(self):
        """
        Randomly perform human-like actions (visit about page, etc).
        
        Returns:
            True if non-target action was performed
        """
        if random.random() < self.config['anti_detection']['visit_about_page_probability']:
            self.logger.info("Simulating human behavior - visiting about page")
            # In real implementation, would actually visit a random page
            self.human_delay()
            return True
        
        return False
