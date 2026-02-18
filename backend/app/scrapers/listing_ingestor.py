"""
Listing data ingestor for database integration.

Handles:
- Upsert logic (create/update listings)
- Deduplication via source_id
- Lifecycle management (active → inactive)
- Days on market calculation
"""

from typing import List, Dict
from datetime import date
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import logging

from app.models.listing import RealEstateListing
from app.models.geography import Municipality
from app.core.database import SessionLocal


class ListingIngestor:
    """Handles database operations for scraped listings."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.logger = logging.getLogger(__name__)
    
    def ingest_listing(self, listing_data: Dict) -> RealEstateListing:
        """
        Ingest a single listing with upsert logic.
        
        Args:
            listing_data: Dict with listing fields
        
        Returns:
            RealEstateListing object (created or updated)
        """
        source_id = listing_data['source_id']
        
        # Check if listing already exists
        existing = self.db.query(RealEstateListing).filter_by(
            source_id=source_id
        ).first()
        
        if existing:
            return self._update_listing(existing, listing_data)
        else:
            return self._create_listing(listing_data)
    
    def _create_listing(self, data: Dict) -> RealEstateListing:
        """Create new listing record."""
        try:
            listing = RealEstateListing(**data)
            self.db.add(listing)
            self.db.commit()
            self.db.refresh(listing)
            
            self.logger.info(f"Created new listing: {listing.source_id}")
            return listing
            
        except IntegrityError as e:
            self.db.rollback()
            self.logger.error(f"Integrity error creating listing: {e}")
            raise
    
    def _update_listing(self, existing: RealEstateListing, data: Dict) -> RealEstateListing:
        """
        Update existing listing.
        
        Updates:
        - price (may have changed)
        - views (if available)
        - days_on_market (recalculated)
        - is_active (still listed)
        """
        # Update price if changed
        if data.get('price') and data['price'] != existing.price:
            self.logger.info(f"Price changed for {existing.source_id}: €{existing.price} → €{data['price']}")
            existing.price = data['price']
            
            # Recalculate price_per_sqm
            if existing.size_sqm and existing.size_sqm > 0:
                existing.price_per_sqm = data['price'] / existing.size_sqm
        
        # Update views
        if data.get('views'):
            existing.views = data['views']
        
        # Recalculate days on market
        if existing.date_posted:
            existing.days_on_market = (date.today() - existing.date_posted).days
        
        # Mark as active (still being scraped)
        if not existing.is_active:
            self.logger.info(f"Reactivating listing {existing.source_id}")
            existing.is_active = True
            existing.date_removed = None
        
        self.db.commit()
        self.db.refresh(existing)
        
        self.logger.info(f"Updated listing: {existing.source_id}")
        return existing
    
    def ingest_batch(self, listings_data: List[Dict]) -> Dict[str, int]:
        """
        Ingest multiple listings in batch.
        
        Args:
            listings_data: List of listing dicts
        
        Returns:
            Dict with stats (created, updated, errors)
        """
        stats = {'created': 0, 'updated': 0, 'errors': 0}
        
        for data in listings_data:
            try:
                listing = self.ingest_listing(data)
                
                if listing.created_at == listing.updated_at:
                    stats['created'] += 1
                else:
                    stats['updated'] += 1
                    
            except Exception as e:
                stats['errors'] += 1
                self.logger.error(f"Error ingesting listing {data.get('source_id')}: {e}")
                continue
        
        self.logger.info(f"Batch ingest complete: {stats}")
        return stats
    
    def mark_delisted(self, municipality_id: int, active_source_ids: List[str], platform: str = 'casa_it'):
        """
        Mark listings as inactive if they're no longer in active set.
        
        This is called after scraping to identify delisted properties.
        
        Args:
            municipality_id: Municipality ID
            active_source_ids: List of source_ids currently active
            platform: Source platform ('casa_it')
        """
        # Find listings not in active set
        delisted = self.db.query(RealEstateListing).filter(
            and_(
                RealEstateListing.municipality_id == municipality_id,
                RealEstateListing.source_platform == platform,
                RealEstateListing.is_active == True,
                RealEstateListing.source_id.notin_(active_source_ids) if active_source_ids else True
            )
        ).all()
        
        count = len(delisted)
        
        if count > 0:
            self.logger.info(f"Marking {count} listings as delisted for municipality {municipality_id}")
            
            for listing in delisted:
                listing.is_active = False
                listing.date_removed = date.today()
                
                # Calculate final days on market
                if listing.date_posted:
                    listing.days_on_market = (listing.date_removed - listing.date_posted).days
            
            self.db.commit()
        
        return count
    
    def get_active_count(self, municipality_id: int, platform: str = 'casa_it') -> int:
        """Get count of active listings for a municipality."""
        return self.db.query(RealEstateListing).filter(
            and_(
                RealEstateListing.municipality_id == municipality_id,
                RealEstateListing.source_platform == platform,
                RealEstateListing.is_active == True
            )
        ).count()
    
    def close(self):
        """Close database connection."""
        self.db.close()
