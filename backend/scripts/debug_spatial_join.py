import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_spatial():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        # Check SRIDs
        s_srid = conn.execute(text("SELECT ST_SRID(geometry) FROM service_nodes LIMIT 1")).scalar()
        m_srid = conn.execute(text("SELECT ST_SRID(geometry) FROM municipalities LIMIT 1")).scalar()
        logger.info(f"ServiceNode SRID: {s_srid}, Municipality SRID: {m_srid}")

        # Check raw coordinates sample
        s_pt = conn.execute(text("SELECT ST_AsText(geometry) FROM service_nodes LIMIT 1")).scalar()
        m_poly = conn.execute(text("SELECT ST_AsText(geometry) FROM municipalities WHERE name = 'Roma'")).scalar()
        logger.info(f"Sample Service Point: {s_pt}")
        logger.info(f"Sample Municipality (Roma) Start: {m_poly[:50]}...")

        # Test Intersection Count
        cnt = conn.execute(text("""
            SELECT COUNT(*) 
            FROM service_nodes s, municipalities m 
            WHERE m.name = 'Roma' 
            AND ST_Intersects(m.geometry, s.geometry)
        """)).scalar()
        logger.info(f"Intersections with Roma: {cnt}")
        
        # Test Bounding Box
        cnt_bbox = conn.execute(text("""
            SELECT COUNT(*) 
            FROM service_nodes s, municipalities m 
            WHERE m.name = 'Roma' 
            AND m.geometry && s.geometry
        """)).scalar()
        logger.info(f"Bounding Box matches with Roma: {cnt_bbox}")

if __name__ == "__main__":
    debug_spatial()
