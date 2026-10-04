from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import FarmModel
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import FarmCreate, FarmOut
from backend.app.services.audit_service import log_audit_event

router = APIRouter()

@router.get("", response_model=StandardResponse[List[FarmOut]])
def list_farms(db: Session = Depends(get_db)):
    farms = db.query(FarmModel).order_by(FarmModel.created_at.desc()).all()
    if not farms:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No farm registered. Register a farm to begin agricultural intelligence mapping."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=farms,
        message=f"Retrieved {len(farms)} registered farm(s)."
    )

@router.post("", response_model=StandardResponse[FarmOut])
def create_farm(payload: FarmCreate, db: Session = Depends(get_db)):
    farm = FarmModel(
        name=payload.name,
        owner_id=payload.owner_id,
        description=payload.description,
        location_name=payload.location_name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        total_area_hectares=payload.total_area_hectares,
        geometry_geojson=payload.geometry_geojson
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)

    log_audit_event(
        db=db,
        action="CREATE_FARM",
        entity_type="FARM",
        entity_id=farm.id,
        source="SYSTEM_API",
        new_state={"name": farm.name, "location": farm.location_name}
    )

    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=farm,
        message="Farm registered successfully."
    )

@router.get("/{farm_id}", response_model=StandardResponse[Optional[FarmOut]])
def get_farm(farm_id: str, db: Session = Depends(get_db)):
    farm = db.query(FarmModel).filter(FarmModel.id == farm_id).first()
    if not farm:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=None,
            message=f"Farm with ID {farm_id} does not exist."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=farm,
        message="Farm details retrieved successfully."
    )
