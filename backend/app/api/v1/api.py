from fastapi import APIRouter
from app.api.v1.endpoints import locations, properties, scores, risks, demographics
from app.api.v1 import listings

api_router = APIRouter()
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(scores.router, prefix="/scores", tags=["scores"])
api_router.include_router(risks.router, prefix="/risks", tags=["risks"])
api_router.include_router(demographics.router, prefix="/demographics", tags=["demographics"])
api_router.include_router(listings.router, tags=["listings"])  # No prefix needed - already in listings.py
