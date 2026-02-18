from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API Config
    PROJECT_NAME: str = "Italian Property Intelligence Platform"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost"]
    
    # Database
    DATABASE_URL: str
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    NOMINATIM_USER_AGENT: str = "italian-property-platform"
    NOMINATIM_BASE_URL: str = "https://nominatim.openstreetmap.org"
    
    # Data paths
    OMI_DATA_PATH: str = "./data/raw/omi"
    ISTAT_DATA_PATH: str = "./data/raw/istat"
    ISPRA_DATA_PATH: str = "./data/raw/ispra"
    INGV_DATA_PATH: str = "./data/raw/ingv"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
