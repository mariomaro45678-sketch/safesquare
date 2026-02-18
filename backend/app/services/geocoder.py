from typing import Tuple, Optional
import time
import requests
from app.core.config import settings

class GeocoderService:
    """
    Service to handle geocoding (address to coordinates) 
    and reverse geocoding.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        # We can use Nominatim (free) or Google Maps / Mapbox (paid)
        self.api_key = api_key or settings.GEOCODING_API_KEY
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.user_agent = "ItalianPropertyIntelligencePlatform/1.0"

    def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocodes an address. Returns (latitude, longitude) or None.
        """
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": self.user_agent
        }
        
        try:
            response = requests.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            results = response.json()
            
            if results:
                lat = float(results[0]["lat"])
                lon = float(results[0]["lon"])
                return lat, lon
            
            return None
        except Exception as e:
            print(f"Geocoding error for {address}: {e}")
            return None
        finally:
            # Respect Nominatim's usage policy (max 1 request per second)
            time.sleep(1)

    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Reverse geocodes coordinates to an address.
        """
        # Implementation for reverse geocoding
        pass
