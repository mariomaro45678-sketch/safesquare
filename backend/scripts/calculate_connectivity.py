import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_connectivity():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        # 1. Update distance to nearest Train Station
        logger.info("Updating dist_train_station_km...")
        try:
            # We use <-> operator for Nearest Neighbor search (GIST index usage)
            # This query updates each municipality with the distance to the nearest station
            # Note: This might take a few seconds/minutes for 8000 rows.
            # Using a LATERAL JOIN approach for batch update is complex in UPDATE statement.
            # Simpler update with subquery is standard:
            sql = """
            UPDATE municipalities m
            SET dist_train_station_km = (
                SELECT ST_Distance(m.centroid::geography, t.geometry::geography) / 1000.0
                FROM transport_nodes t
                WHERE t.node_type = 'TRAIN_STATION'
                ORDER BY m.centroid <-> t.geometry
                LIMIT 1
            );
            """
            conn.execute(text(sql))
            logger.info("Done updating Train Stations.")
        except Exception as e:
            logger.error(f"Error updating stations: {e}")

        # 2. Update distance to nearest Highway Exit
        logger.info("Updating dist_highway_exit_km...")
        try:
            sql = """
            UPDATE municipalities m
            SET dist_highway_exit_km = (
                SELECT ST_Distance(m.centroid::geography, t.geometry::geography) / 1000.0
                FROM transport_nodes t
                WHERE t.node_type = 'HIGHWAY_EXIT'
                ORDER BY m.centroid <-> t.geometry
                LIMIT 1
            );
            """
            conn.execute(text(sql))
            logger.info("Done updating Highway Exits.")
        except Exception as e:
            logger.error(f"Error updating exits: {e}")
            
    logger.info("Connectivity calculation complete.")

if __name__ == "__main__":
    calculate_connectivity()
