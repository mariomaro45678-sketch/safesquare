from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import logging

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging_config import setup_logging

# Initialize Logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

# Set all CORS enabled origins with explicit methods (security hardening)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],  # Explicit methods only
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/health/detailed")
def detailed_health_check():
    """
    Comprehensive health check that validates actual database connectivity.
    """
    db_status = "unknown"
    db_latency_ms = None
    
    try:
        import time
        db = SessionLocal()
        start = time.time()
        db.execute(text("SELECT 1"))
        db_latency_ms = round((time.time() - start) * 1000, 2)
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f"disconnected"
    finally:
        try:
            db.close()
        except Exception:
            pass
    
    is_healthy = db_status == "connected"
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "system": "up",
        "database": db_status,
        "database_latency_ms": db_latency_ms,
        "version": "1.0.0"
    }
