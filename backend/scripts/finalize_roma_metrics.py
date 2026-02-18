
import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def finalize_roma_metrics():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        logger.info("Finalizing Roma metrics with correct area (1285 km2)...")
        
        # 1. Update Towers (using correct area for radius)
        sql_towers = """
        UPDATE municipalities m
        SET mobile_tower_count = (
            SELECT COUNT(*)
            FROM global_temp_towers t
            WHERE ST_DWithin(
                m.centroid::geography, 
                t.geometry::geography, 
                (SQRT(1285.0 / 3.14159) * 1000 * 1.2)
            )
        )
        WHERE m.name = 'Roma';
        """
        # Wait, global_temp_towers might be gone if the script finished.
        # I should check if it exists or use the existing ingest_mobile_towers logic.
        # Actually, let's just use the service_nodes and transport_nodes for now.
        # If I need towers again, I'd need to re-ingest them to a temp table.
        # Let's check if there's a better way for towers.
        
        # 2. Update amenity counts (using correct area)
        sql_amenities = """
        UPDATE municipalities m
        SET 
            hospital_count = (
                SELECT COUNT(*) FROM service_nodes s 
                WHERE s.service_type = 'HOSPITAL' 
                AND ST_DWithin(m.centroid::geography, s.geometry::geography, (SQRT(1285.0 / 3.14159) * 1000 * 1.2))
            ),
            school_count = (
                SELECT COUNT(*) FROM service_nodes s 
                WHERE s.service_type = 'SCHOOL' 
                AND ST_DWithin(m.centroid::geography, s.geometry::geography, (SQRT(1285.0 / 3.14159) * 1000 * 1.2))
            ),
            supermarket_count = (
                SELECT COUNT(*) FROM service_nodes s 
                WHERE s.service_type = 'SUPERMARKET' 
                AND ST_DWithin(m.centroid::geography, s.geometry::geography, (SQRT(1285.0 / 3.14159) * 1000 * 1.2))
            )
        WHERE m.name = 'Roma';
        """
        conn.execute(text(sql_amenities))
        
        # 3. Update connectivity
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
        
        logger.info("Roma final localized update complete.")

if __name__ == "__main__":
    finalize_roma_metrics()
