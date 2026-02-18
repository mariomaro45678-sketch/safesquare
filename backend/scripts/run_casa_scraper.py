"""
CLI script to run the Casa.it scraper with checkpoint/resume support.

Usage:
    python scripts/run_casa_scraper.py --municipalities "Roma"
    python scripts/run_casa_scraper.py --municipalities "Roma,Milano,Napoli" --parallel --workers 10
    python scripts/run_casa_scraper.py --all-italy --workers 50 --max-listings-per-city 200
    python scripts/run_casa_scraper.py --resume  # Resume from last checkpoint
    python scripts/run_casa_scraper.py --checkpoint-file my_scrape.json --all-italy  # Custom checkpoint file
"""

import argparse
import logging
import sys
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import threading

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scrapers.casa_scraper import CasaScraper
from app.scrapers.listing_ingestor import ListingIngestor
from app.models.geography import Municipality
from app.core.database import SessionLocal
from sqlalchemy import func


# Checkpoint management
CHECKPOINT_DIR = Path(__file__).parent.parent / "logs" / "checkpoints"
DEFAULT_CHECKPOINT_FILE = CHECKPOINT_DIR / "scrape_checkpoint.json"


class CheckpointManager:
    """Manages scrape progress checkpoints for resume capability."""

    def __init__(self, checkpoint_file: Path = None):
        self.checkpoint_file = checkpoint_file or DEFAULT_CHECKPOINT_FILE
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.data = self._load()

    def _load(self) -> Dict:
        """Load existing checkpoint or create new."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._new_checkpoint()

    def _new_checkpoint(self) -> Dict:
        """Create new checkpoint structure."""
        return {
            'started_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'completed_municipalities': [],
            'failed_municipalities': [],
            'in_progress': None,
            'total_scraped': 0,
            'total_created': 0,
            'total_updated': 0,
            'total_delisted': 0,
            'total_errors': 0,
            'config': {}
        }

    def _save(self):
        """Save checkpoint to file."""
        self.data['updated_at'] = datetime.now().isoformat()
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def start_new_run(self, config: Dict):
        """Start a fresh scrape run."""
        self.data = self._new_checkpoint()
        self.data['config'] = config
        self._save()

    def get_completed(self) -> Set[str]:
        """Get set of completed municipality names."""
        return set(self.data.get('completed_municipalities', []))

    def get_failed(self) -> Set[str]:
        """Get set of failed municipality names."""
        return set(self.data.get('failed_municipalities', []))

    def mark_started(self, municipality_name: str):
        """Mark municipality as in progress."""
        with self.lock:
            self.data['in_progress'] = municipality_name
            self._save()

    def mark_completed(self, municipality_name: str, result: Dict):
        """Mark municipality as completed and update stats."""
        with self.lock:
            if municipality_name not in self.data['completed_municipalities']:
                self.data['completed_municipalities'].append(municipality_name)
            if municipality_name in self.data.get('failed_municipalities', []):
                self.data['failed_municipalities'].remove(municipality_name)
            self.data['in_progress'] = None

            # Update aggregate stats
            self.data['total_scraped'] += result.get('scraped', 0)
            self.data['total_created'] += result.get('created', 0)
            self.data['total_updated'] += result.get('updated', 0)
            self.data['total_delisted'] += result.get('delisted', 0)
            self.data['total_errors'] += result.get('errors', 0)

            self._save()

    def mark_failed(self, municipality_name: str, error: str):
        """Mark municipality as failed."""
        with self.lock:
            if municipality_name not in self.data.get('failed_municipalities', []):
                self.data['failed_municipalities'].append(municipality_name)
            self.data['in_progress'] = None
            self._save()

    def get_summary(self) -> Dict:
        """Get checkpoint summary."""
        return {
            'started_at': self.data.get('started_at'),
            'updated_at': self.data.get('updated_at'),
            'completed_count': len(self.data.get('completed_municipalities', [])),
            'failed_count': len(self.data.get('failed_municipalities', [])),
            'total_scraped': self.data.get('total_scraped', 0),
            'total_created': self.data.get('total_created', 0),
            'total_updated': self.data.get('total_updated', 0),
        }

    def clear(self):
        """Clear checkpoint file."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        self.data = self._new_checkpoint()


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/scraper_run.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_municipalities(municipality_names: List[str] = None, all_italy: bool = False) -> List[Municipality]:
    """
    Get municipalities to scrape.
    
    Args:
        municipality_names: List of municipality names
        all_italy: Scrape all Italian municipalities
    
    Returns:
        List of Municipality objects
    """
    db = SessionLocal()
    
    if all_italy:
        municipalities = db.query(Municipality).all()
        logging.info(f"Selected all {len(municipalities)} Italian municipalities")
    elif municipality_names:
        municipalities = db.query(Municipality).filter(
            func.lower(Municipality.name).in_([m.lower() for m in municipality_names])
        ).all()
        logging.info(f"Selected {len(municipalities)} municipalities: {[m.name for m in municipalities]}")
    else:
        # Default: top 50 cities
        municipalities = db.query(Municipality).order_by(
            Municipality.population.desc()
        ).limit(50).all()
        logging.info(f"Selected top 50 cities by population")
    
    db.close()
    return municipalities


def scrape_single_municipality(
    municipality: Municipality,
    max_listings: int,
    checkpoint_manager: Optional[CheckpointManager] = None,
    mode: str = 'browser',
    headless: bool = True,
    listing_type: str = 'sale'
) -> dict:
    """
    Scrape a single municipality (used in parallel execution).

    Args:
        municipality: Municipality object
        max_listings: Max listings to scrape
        checkpoint_manager: Optional checkpoint manager for progress tracking
        mode: 'browser' for Playwright, 'http' for curl_cffi
        headless: Run browser in headless mode (browser mode only)

    Returns:
        Stats dict
    """
    scraper = None
    ingestor = None

    # Mark as in progress
    if checkpoint_manager:
        checkpoint_manager.mark_started(municipality.name)

    try:
        scraper = CasaScraper(mode=mode, headless=headless, listing_type=listing_type)
        ingestor = ListingIngestor()

        # Scrape listings
        listings_data = scraper.scrape_municipality(municipality, max_listings)

        if not listings_data:
            result = {
                'municipality': municipality.name,
                'status': 'no_listings',
                'scraped': 0,
                'created': 0,
                'updated': 0,
                'delisted': 0,
                'errors': 0
            }
            if checkpoint_manager:
                checkpoint_manager.mark_completed(municipality.name, result)
            return result

        # Ingest to database
        ingest_stats = ingestor.ingest_batch(listings_data)

        # Mark delisted listings
        active_source_ids = [l['source_id'] for l in listings_data]
        delisted_count = ingestor.mark_delisted(municipality.id, active_source_ids)

        result = {
            'municipality': municipality.name,
            'status': 'success',
            'scraped': len(listings_data),
            'created': ingest_stats['created'],
            'updated': ingest_stats['updated'],
            'delisted': delisted_count,
            'errors': ingest_stats['errors']
        }

        if checkpoint_manager:
            checkpoint_manager.mark_completed(municipality.name, result)

        return result

    except Exception as e:
        logging.error(f"Error scraping {municipality.name}: {e}")
        result = {
            'municipality': municipality.name,
            'status': 'error',
            'error': str(e)
        }
        if checkpoint_manager:
            checkpoint_manager.mark_failed(municipality.name, str(e))
        return result

    finally:
        if scraper:
            scraper.close()
        if ingestor:
            ingestor.close()


def main():
    parser = argparse.ArgumentParser(description='Run Casa.it scraper with checkpoint/resume support')
    parser.add_argument('--municipalities', type=str, help='Comma-separated municipality names (e.g., "Roma,Milano")')
    parser.add_argument('--all-italy', action='store_true', help='Scrape all 7,895 Italian municipalities')
    parser.add_argument('--parallel', action='store_true', help='Run parallel scraping')
    parser.add_argument('--workers', type=int, default=10, help='Number of parallel workers (default: 10)')
    parser.add_argument('--max-listings-per-city', type=int, default=100, help='Max listings per city (default: 100)')
    parser.add_argument('--limit', type=int, help='Limit total number of municipalities to scrape')

    # Scraper mode arguments
    parser.add_argument('--mode', type=str, choices=['browser', 'http'], default='browser',
                        help='Scraping mode: browser (Playwright) or http (curl_cffi). Default: browser')
    parser.add_argument('--listing-type', type=str, choices=['sale', 'rent'], default='sale',
                        help='Listing type: sale or rent. Default: sale')
    parser.add_argument('--no-headless', action='store_true',
                        help='Run browser in visible mode (useful for debugging CAPTCHA)')

    # Checkpoint/resume arguments
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint')
    parser.add_argument('--checkpoint-file', type=str, help='Custom checkpoint file path')
    parser.add_argument('--clear-checkpoint', action='store_true', help='Clear existing checkpoint and start fresh')
    parser.add_argument('--retry-failed', action='store_true', help='Retry previously failed municipalities')
    parser.add_argument('--checkpoint-status', action='store_true', help='Show checkpoint status and exit')

    args = parser.parse_args()

    # Setup
    setup_logging()

    # Initialize checkpoint manager
    checkpoint_file = Path(args.checkpoint_file) if args.checkpoint_file else None
    checkpoint_mgr = CheckpointManager(checkpoint_file)

    # Handle checkpoint status query
    if args.checkpoint_status:
        summary = checkpoint_mgr.get_summary()
        logging.info("=== CHECKPOINT STATUS ===")
        logging.info(f"Started: {summary['started_at']}")
        logging.info(f"Last updated: {summary['updated_at']}")
        logging.info(f"Completed municipalities: {summary['completed_count']}")
        logging.info(f"Failed municipalities: {summary['failed_count']}")
        logging.info(f"Total scraped: {summary['total_scraped']}")
        logging.info(f"Total created: {summary['total_created']}")
        logging.info(f"Total updated: {summary['total_updated']}")
        if summary['failed_count'] > 0:
            logging.info(f"\nFailed municipalities: {checkpoint_mgr.get_failed()}")
        return

    # Handle clear checkpoint
    if args.clear_checkpoint:
        checkpoint_mgr.clear()
        logging.info("Checkpoint cleared")
        if not (args.municipalities or args.all_italy):
            return

    logging.info("Starting Casa.it scraper")

    # Get municipalities
    municipality_names = args.municipalities.split(',') if args.municipalities else None
    municipalities = get_municipalities(municipality_names, args.all_italy)

    if args.limit:
        municipalities = municipalities[:args.limit]
        logging.info(f"Limited to {args.limit} municipalities")

    if not municipalities:
        logging.error("No municipalities found")
        return

    # Handle resume/checkpoint filtering
    if args.resume or args.retry_failed:
        completed = checkpoint_mgr.get_completed()
        failed = checkpoint_mgr.get_failed()

        original_count = len(municipalities)

        if args.retry_failed:
            # Only retry failed ones
            municipalities = [m for m in municipalities if m.name in failed]
            logging.info(f"Retrying {len(municipalities)} previously failed municipalities")
        elif args.resume:
            # Skip completed ones
            municipalities = [m for m in municipalities if m.name not in completed]
            logging.info(f"Resuming: {original_count - len(municipalities)} already completed, {len(municipalities)} remaining")

        if not municipalities:
            logging.info("All municipalities already processed. Use --clear-checkpoint to start fresh.")
            return
    else:
        # New run - initialize checkpoint with config
        checkpoint_mgr.start_new_run({
            'municipalities': args.municipalities,
            'all_italy': args.all_italy,
            'parallel': args.parallel,
            'workers': args.workers,
            'max_listings_per_city': args.max_listings_per_city,
            'limit': args.limit
        })

    # Scraper mode settings
    headless = not args.no_headless
    logging.info(f"Using scraper mode: {args.mode} (headless={headless})")

    # Scrape
    if args.parallel:
        logging.info(f"Running parallel scraper with {args.workers} workers")

        # Note: Browser mode with parallel workers will create multiple browser instances
        # which may be resource-intensive. Consider using fewer workers with browser mode.
        if args.mode == 'browser' and args.workers > 3:
            logging.warning("Browser mode with many parallel workers is resource-intensive. Consider --workers 3 or less.")

        results = []
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(
                    scrape_single_municipality,
                    m,
                    args.max_listings_per_city,
                    checkpoint_mgr,
                    args.mode,
                    headless,
                    args.listing_type
                ): m
                for m in municipalities
            }

            # Progress bar
            with tqdm(total=len(municipalities), desc="Scraping municipalities") as pbar:
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    pbar.update(1)
                    pbar.set_postfix({'last': result['municipality'], 'status': result['status']})

    else:
        logging.info("Running sequential scraper")
        results = []

        for municipality in tqdm(municipalities, desc="Scraping municipalities"):
            result = scrape_single_municipality(
                municipality,
                args.max_listings_per_city,
                checkpoint_mgr,
                args.mode,
                headless,
                args.listing_type
            )
            results.append(result)

    # Summary
    logging.info("\n" + "="*50)
    logging.info("SCRAPE SUMMARY")
    logging.info("="*50)

    total_scraped = sum(r.get('scraped', 0) for r in results)
    total_created = sum(r.get('created', 0) for r in results)
    total_updated = sum(r.get('updated', 0) for r in results)
    total_delisted = sum(r.get('delisted', 0) for r in results)
    total_errors = sum(r.get('errors', 0) for r in results)
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'error')
    no_listings = sum(1 for r in results if r['status'] == 'no_listings')

    logging.info(f"Municipalities processed this run: {len(results)}")
    logging.info(f"  - Successful: {successful}")
    logging.info(f"  - No listings found: {no_listings}")
    logging.info(f"  - Failed: {failed}")
    logging.info(f"Listings scraped: {total_scraped}")
    logging.info(f"  - New listings created: {total_created}")
    logging.info(f"  - Existing listings updated: {total_updated}")
    logging.info(f"  - Listings marked delisted: {total_delisted}")
    logging.info(f"  - Errors: {total_errors}")
    logging.info("="*50)

    # Checkpoint cumulative summary
    checkpoint_summary = checkpoint_mgr.get_summary()
    logging.info("\n=== CUMULATIVE PROGRESS (from checkpoint) ===")
    logging.info(f"Total completed municipalities: {checkpoint_summary['completed_count']}")
    logging.info(f"Total failed municipalities: {checkpoint_summary['failed_count']}")
    logging.info(f"Total listings scraped: {checkpoint_summary['total_scraped']}")
    logging.info(f"Total new listings: {checkpoint_summary['total_created']}")
    logging.info(f"Total updated listings: {checkpoint_summary['total_updated']}")

    # Success rate
    if len(results) > 0:
        success_rate = ((successful + no_listings) / len(results)) * 100
        logging.info(f"\nThis run success rate: {success_rate:.1f}%")

    # Detailed errors
    if failed > 0:
        logging.info("\nFailed municipalities this run:")
        for r in results:
            if r['status'] == 'error':
                logging.info(f"  - {r['municipality']}: {r.get('error', 'Unknown error')}")
        logging.info("\nTip: Use --retry-failed to retry these municipalities")


if __name__ == "__main__":
    main()
