from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from backend.app.core.database import get_db
from backend.app.models.entities import SatelliteObservationModel, FieldModel
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import SatelliteObservationOut
from backend.app.integrations.satellite.sentinel2 import Sentinel2Pipeline

router = APIRouter()
pipeline = Sentinel2Pipeline()

@router.get("", response_model=StandardResponse[List[SatelliteObservationOut]])
def get_satellite_observations(
    field_id: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(SatelliteObservationModel)
    if field_id:
        query = query.filter(SatelliteObservationModel.field_id == field_id)
    obs = query.order_by(SatelliteObservationModel.observed_at.desc()).limit(limit).all()
    
    if not obs:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No satellite observations available. Connect the Sentinel-2 data pipeline to begin crop-health analysis."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=obs,
        message=f"Retrieved {len(obs)} satellite observation(s)."
    )

@router.get("/pipeline-status")
def get_pipeline_status():
    return {
        "status": StateStatus.AVAILABLE,
        "pipeline": "Copernicus Sentinel-2 MSI",
        "configured": pipeline.is_configured(),
        "bands_supported": pipeline.SENTINEL_BANDS,
        "features": [
            "Level-2A BOA Reflectance",
            "SCL Scene Classification Cloud Masking",
            "Field Polygon Clipping",
            "B08/B04 Normalized Difference Vegetation Index"
        ],
        "connection_state": "CONNECTED" if pipeline.is_configured() else "NOT_CONFIGURED",
        "message": "Sentinel-2 pipeline configuration retrieved."
    }

@router.post("/compute-ndvi")
def compute_ndvi(b04_red: float, b08_nir: float, cloud_masked: bool = False):
    """
    Computes deterministic NDVI without fake data.
    """
    return pipeline.compute_field_ndvi(b04_red, b08_nir, cloud_flag=cloud_masked)
