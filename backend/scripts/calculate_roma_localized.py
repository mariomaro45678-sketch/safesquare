
import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_roma_metrics():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Updating Roma metrics localized...")
        
        # Update amenity counts for Roma
        sql_amenities = """
        UPDATE municipalities m
        SET 
            hospital_count = (
                SELECT COUNT(*) FROM service_nodes s 
                WHERE s.service_type = 'HOSPITAL' 
                AND ST_DWithin(m.centroid::geography, s.geometry::geography, (SQRT(COALESCE(NULLIF(m.area_sqkm, 0), 50.0) / 3.14159) * 1000 * 1.2))
            ),
            school_count = (
                SELECT COUNT(*) FROM service_nodes s 
                WHERE s.service_type = 'SCHOOL' 
                AND ST_DWithin(m.centroid::geography, s.geometry::geography, (SQRT(COALESCE(NULLIF(m.area_sqkm, 0), 50.0) / 3.14159) * 1000 * 1.2))
            ),
            supermarket_count = (
                SELECT COUNT(*) FROM service_nodes s 
                WHERE s.service_type = 'SUPERMARKET' 
                AND ST_DWithin(m.centroid::geography, s.geometry::geography, (SQRT(COALESCE(NULLIF(m.area_sqkm, 0), 50.0) / 3.14159) * 1000 * 1.2))
            )
        WHERE m.name = 'Roma';
        """
        conn.execute(text(sql_amenities))
        
        # Update connectivity for Roma
        sql_connectivity = """
        UPDATE municipalities m
        SET 
            dist_train_station_km = (
                SELECT MIN(ST_Distance(m.centroid::geography, t.geometry::geography) / 1000.0)
                FROM transport_nodes t WHERE t.node_type = 'TRAIN_STATION'
            ),
            dist_highway_exit_km = (
                SELECT MIN(ST_Distance(m.centroid::geography, t.geometry::geography) / 1000.0)
                FROM transport_nodes t WHERE t.node_type = 'HIGHWAY_EXIT'
            )
        WHERE m.name = 'Roma';
        """
        conn.execute(text(sql_connectivity))
        
        logger.info("Roma localized update complete.")

if __name__ == "__main__":
    update_roma_metrics()
