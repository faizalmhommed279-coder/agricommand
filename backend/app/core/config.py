import os
from typing import List

class Settings:
    PROJECT_NAME: str = "AgriCommand"
    PROJECT_DESCRIPTION: str = "Integrated Agricultural Intelligence & Decision-Support Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Database
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./agricommand.db")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]
    
    # Security & RBAC
    SECRET_KEY: str = os.getenv("SECRET_KEY", "agricommand-production-grade-secret-key-32-chars-min")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    # External Integration Endpoints (Configurations)
    NASA_POWER_API_BASE: str = os.getenv("NASA_POWER_API_BASE", "https://power.larc.nasa.gov/api/temporal/daily/point")
    IMD_GRIDDED_API_BASE: str = os.getenv("IMD_GRIDDED_API_BASE", "")
    SENTINEL_HUB_BASE: str = os.getenv("SENTINEL_HUB_BASE", "")
    ISRIC_SOILGRIDS_API_BASE: str = os.getenv("ISRIC_SOILGRIDS_API_BASE", "https://rest.isric.org/soilgrids/v2.0/properties/query")

settings = Settings()
