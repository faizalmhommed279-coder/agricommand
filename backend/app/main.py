from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
import backend.app.models.entities # Ensure all models are registered

# Create database tables automatically
Base.metadata.create_all(bind=engine)

# Include route routers
from backend.app.api.routes import (
    farms, fields, crops, sensors, telemetry, weather, satellite,
    soil, water, predictions, optimization, recommendations,
    harvest, storage, outcomes, digital_twin, data_quality, audit
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all domain routers
api_prefix = settings.API_V1_STR
app.include_router(farms.router, prefix=f"{api_prefix}/farms", tags=["Farm Management"])
app.include_router(fields.router, prefix=f"{api_prefix}/fields", tags=["Field Mapping"])
app.include_router(crops.router, prefix=f"{api_prefix}/crops", tags=["Crop Profiles & Cycles"])
app.include_router(sensors.router, prefix=f"{api_prefix}/sensors", tags=["Hardware & Sensor Registry"])
app.include_router(telemetry.router, prefix=f"{api_prefix}/telemetry", tags=["ESP32 Telemetry & Ingestion"])
app.include_router(weather.router, prefix=f"{api_prefix}/weather", tags=["Weather & Climate"])
app.include_router(satellite.router, prefix=f"{api_prefix}/satellite", tags=["Satellite & NDVI"])
app.include_router(soil.router, prefix=f"{api_prefix}/soil", tags=["Soil Information & ISRIC"])
app.include_router(water.router, prefix=f"{api_prefix}/water", tags=["Water Management & FAO-56"])
app.include_router(predictions.router, prefix=f"{api_prefix}/predictions", tags=["Prediction Models"])
app.include_router(optimization.router, prefix=f"{api_prefix}/optimization", tags=["Resource Optimization"])
app.include_router(recommendations.router, prefix=f"{api_prefix}/recommendations", tags=["Explainable Recommendations"])
app.include_router(harvest.router, prefix=f"{api_prefix}/harvest", tags=["Harvest Window Tracker"])
app.include_router(storage.router, prefix=f"{api_prefix}/storage", tags=["Storage Network Evaluator"])
app.include_router(outcomes.router, prefix=f"{api_prefix}/outcomes", tags=["Observed Outcomes"])
app.include_router(digital_twin.router, prefix=f"{api_prefix}/digital-twin", tags=["Farm Digital Twin"])
app.include_router(data_quality.router, prefix=f"{api_prefix}/data-quality", tags=["Data Quality Center"])
app.include_router(audit.router, prefix=f"{api_prefix}/audit", tags=["Audit Trail"])

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "philosophy": "Data changes decisions.",
        "data_policy": "NEVER_USE_FAKE_DATA"
    }

import os
from fastapi.staticfiles import StaticFiles

frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "platform": settings.PROJECT_NAME,
            "api_docs": "/docs",
            "digital_twin_endpoint": f"{settings.API_V1_STR}/digital-twin",
            "status": "OPERATIONAL"
        }

