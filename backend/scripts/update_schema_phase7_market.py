from app.core.database import engine
from app.models.listing import RealEstateListing
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_schema():
    logger.info("Creating real_estate_listings table...")
    RealEstateListing.__table__.create(bind=engine, checkfirst=True)
    logger.info("Table created successfully.")

if __name__ == "__main__":
    update_schema()
