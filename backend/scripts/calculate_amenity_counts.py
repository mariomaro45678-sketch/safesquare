import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_amenities():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        # 1. Hospitals Count
        logger.info("Counting Hospitals per municipality...")
        try:
            # Strategy: Use Dynamic Radius from Centroid since Polygons are missing
            # Radius approx = sqrt(area_sqkm / pi) * 1000 meters. 
            # We add 20% buffer to capture edge cases.
            
            sql = """
            UPDATE municipalities m
            SET hospital_count = (
                SELECT COUNT(*)
                FROM service_nodes s
                WHERE s.service_type = 'HOSPITAL'
                AND ST_DWithin(
                    m.centroid::geography, 
                    s.geometry::geography, 
                    (SQRT(COALESCE(NULLIF(m.area_sqkm, 0), 50.0) / 3.14159) * 1000 * 1.2)
                )
            );
            """
            conn.execute(text(sql))
            logger.info("Done counting Hospitals.")
        except Exception as e:
            logger.error(f"Error counting hospitals: {e}")

        # 2. Schools Count
        logger.info("Counting Schools per municipality...")
        try:
            sql = """
            UPDATE municipalities m
            SET school_count = (
                SELECT COUNT(*)
                FROM service_nodes s
                WHERE s.service_type = 'SCHOOL'
                AND ST_DWithin(
                    m.centroid::geography, 
                    s.geometry::geography, 
                    (SQRT(COALESCE(NULLIF(m.area_sqkm, 0), 50.0) / 3.14159) * 1000 * 1.2)
                )
            );
            """
            conn.execute(text(sql))
            logger.info("Done counting Schools.")
        except Exception as e:
            logger.error(f"Error counting schools: {e}")

        # 3. Supermarkets Count
        logger.info("Counting Supermarkets per municipality...")
        try:
            sql = """
            UPDATE municipalities m
            SET supermarket_count = (
                SELECT COUNT(*)
                FROM service_nodes s
                WHERE s.service_type = 'SUPERMARKET'
                AND ST_DWithin(
                    m.centroid::geography, 
                    s.geometry::geography, 
                    (SQRT(COALESCE(NULLIF(m.area_sqkm, 0), 50.0) / 3.14159) * 1000 * 1.2)
                )
            );
            """
            conn.execute(text(sql))
            logger.info("Done counting Supermarkets.")
        except Exception as e:
            logger.error(f"Error counting supermarkets: {e}")
            
    logger.info("Amenity aggregation complete.")

if __name__ == "__main__":
    calculate_amenities()
