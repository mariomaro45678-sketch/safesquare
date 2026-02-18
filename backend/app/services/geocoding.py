import logging
import requests
import time
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from app.models.geography import Municipality, OMIZone
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeocodingService:
    """
    Geocoding service using Nominatim (OpenStreetMap) API
    Handles address to coordinates conversion and spatial resolution
    """
    
    def __init__(self):
        self.base_url = settings.NOMINATIM_BASE_URL
        self.user_agent = settings.NOMINATIM_USER_AGENT
        self.rate_limit_delay = 1.0  # Nominatim requires 1 request per second
        
    def geocode_address(
        self,
        address: str,
        country: str = "Italy"
    ) -> Optional[Dict[str, Any]]:
        """
        Convert address to coordinates
        """
        try:
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            params = {
                'q': f"{address}, {country}",
                'format': 'json',
                'addressdetails': 1,
                'limit': 1,
            }
            
            headers = {
                'User-Agent': self.user_agent
            }
            
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            results = response.json()
            
            if not results:
                logger.warning(f"No results found for address: {address}")
                return None
            
            result = results[0]
            
            return {
                'latitude': float(result['lat']),
                'longitude': float(result['lon']),
                'display_name': result['display_name'],
                'address_details': result.get('address', {}),
            }
            
        except Exception as e:
            logger.error(f"Geocoding failed for '{address}': {e}")
            return None
    
    def reverse_geocode(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """
        Convert coordinates to address
        """
        try:
            time.sleep(self.rate_limit_delay)
            
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'addressdetails': 1,
            }
            
            headers = {
                'User-Agent': self.user_agent
            }
            
            response = requests.get(
                f"{self.base_url}/reverse",
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'display_name': result.get('display_name'),
                'address_details': result.get('address', {}),
            }
            
        except Exception as e:
            logger.error(f"Reverse geocoding failed for ({latitude}, {longitude}): {e}")
            return None
    
    def find_municipality_by_coordinates(
        self,
        db: Session,
        latitude: float,
        longitude: float
    ) -> Optional[Municipality]:
        """
        Find municipality containing coordinates using PostGIS
        """
        try:
            # Create a point and use PostGIS spatial query
            point = f"SRID=4326;POINT({longitude} {latitude})"
            
            municipality = db.query(Municipality).filter(
                func.ST_Contains(Municipality.geometry, point)
            ).first()
            
            if municipality:
                logger.info(f"Found municipality: {municipality.name}")
            return municipality
            
        except Exception as e:
            logger.error(f"Spatial query failed for municipality: {e}")
            return None
    
    def find_omi_zone_by_coordinates(
        self,
        db: Session,
        latitude: float,
        longitude: float
    ) -> Optional[OMIZone]:
        """
        Find OMI zone containing coordinates using PostGIS
        """
        try:
            point = f"SRID=4326;POINT({longitude} {latitude})"
            
            omi_zone = db.query(OMIZone).filter(
                func.ST_Contains(OMIZone.geometry, point)
            ).first()
            
            if omi_zone:
                logger.debug(f"Found OMI zone: {omi_zone.zone_code}")
            return omi_zone
            
        except Exception as e:
            logger.error(f"Spatial query failed for OMI zone: {e}")
            return None

    def find_municipality_by_name(
        self,
        db: Session,
        name: str
    ) -> Optional[Municipality]:
        """
        Find municipality by name (exact or ilike)
        """
        # Try exact match first
        muni = db.query(Municipality).filter(Municipality.name.ilike(name)).first()
        if muni:
            return muni
        
        # Try cleaning the name (Italians often use 'Milano' for 'Comune di Milano')
        clean_name = name.replace("Comune di ", "").replace("Municipio di ", "").strip()
        muni = db.query(Municipality).filter(Municipality.name.ilike(f"%{clean_name}%")).first()
        return muni

    def resolve_search_query(
        self,
        db: Session,
        query: str
    ) -> Dict[str, Any]:
        """
        Main entry point for resolving a search query.
        Now includes robust fallbacks for missing geometries.
        """
        result = {
            'query': query,
            'found': False,
            'geocoded': None,
            'municipality': None,
            'omi_zone': None,
            'coordinates': None,
        }
        
        # 1. Try Geocoding via Nominatim
        geocoded = self.geocode_address(query)
        
        if geocoded:
            lat, lon = geocoded['latitude'], geocoded['longitude']
            result['geocoded'] = geocoded
            result['coordinates'] = {'latitude': lat, 'longitude': lon}
            
            # 2a. Spatial Resolution (Preferred)
            municipality = self.find_municipality_by_coordinates(db, lat, lon)
            
            if not municipality:
                # 2b. Geocoding Result Name Fallback
                # If spatial lookup fails (missing geometry), use the name from Nominatim
                nom_address = geocoded.get('address_details', {})
                city_name = nom_address.get('city') or nom_address.get('town') or nom_address.get('village')
                if city_name:
                    logger.info(f"Spatial lookup failed, trying Nominatim name fallback: {city_name}")
                    municipality = self.find_municipality_by_name(db, city_name)
            
            if municipality:
                result['found'] = True
                result['municipality'] = {
                    'id': municipality.id,
                    'name': municipality.name,
                    'code': municipality.code
                }
                
                # 3. Resolve OMI Zone
                omi_zone = self.find_omi_zone_by_coordinates(db, lat, lon)
                if not omi_zone:
                    # Fallback to first residential zone in municipality if no spatial match
                    from app.models.geography import OMIZone
                    omi_zone = db.query(OMIZone).filter(
                        OMIZone.municipality_id == municipality.id,
                        OMIZone.zone_type == "Residenziale"
                    ).first()
                
                if omi_zone:
                    result['omi_zone'] = {
                        'id': omi_zone.id,
                        'zone_code': omi_zone.zone_code,
                        'zone_name': omi_zone.zone_name
                    }
        
        # 4. Final Fallback: Direct Query Match (if geocoding failed or didn't find muni)
        if not result['municipality']:
            municipality = self.find_municipality_by_name(db, query)
            if municipality:
                result['found'] = True
                result['municipality'] = {
                    'id': municipality.id,
                    'name': municipality.name,
                    'code': municipality.code
                }
                # No coordinates or OMI zone in this fallback unless we geocode it specifically
        
        return result
