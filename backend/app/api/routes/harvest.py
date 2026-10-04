from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import CropCycleModel, FieldModel
from backend.app.schemas.common import StandardResponse, StateStatus

router = APIRouter()

@router.get("/estimates")
def get_harvest_estimates(field_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Harvest Window Tracker:
    Evaluates crop growth cycles, expected maturity date, and yield uncertainty ranges.
    Returns explicit empty-state when no active cycles or calibrated yield models are linked.
    """
    query = db.query(CropCycleModel)
    if field_id:
        query = query.filter(CropCycleModel.field_id == field_id)
    cycles = query.filter(CropCycleModel.status == "ACTIVE").all()

    if not cycles:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="Harvest estimation unavailable. No active crop cycles or validated field growth stages configured."
        )

    estimates = []
    for c in cycles:
        field = c.field
        crop_prof = c.crop_profile
        estimates.append({
            "field_id": c.field_id,
            "field_name": field.name if field else "Unknown",
            "crop": crop_prof.name if crop_prof else "Unassigned",
            "planting_date": c.planting_date,
            "current_growth_stage": c.current_growth_stage or "Awaiting classification",
            "harvest_window": {
                "earliest_date": c.expected_harvest_date,
                "latest_date": c.expected_harvest_date,
                "confidence": "PENDING_SATELLITE_MATURITY_INDEX"
            },
            "yield_forecast": {
                "status": "PREDICTION_MODEL_NOT_CONFIGURED",
                "estimated_kg_ha": None,
                "uncertainty_range": None
            },
            "status": "MONITORING"
        })

    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=estimates,
        message=f"Harvest window tracking active for {len(estimates)} crop cycle(s)."
    )
