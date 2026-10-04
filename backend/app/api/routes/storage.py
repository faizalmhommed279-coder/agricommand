from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import StorageFacilityModel, StorageObservationModel
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import StorageFacilityCreate, StorageFacilityOut

router = APIRouter()

@router.get("", response_model=StandardResponse[List[StorageFacilityOut]])
def list_storage_facilities(farm_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(StorageFacilityModel)
    if farm_id:
        query = query.filter(StorageFacilityModel.farm_id == farm_id)
    facilities = query.all()
    if not facilities:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No storage facilities configured. Register silos, cold stores, or warehouse hubs to evaluate storage conditions."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=facilities,
        message=f"Retrieved {len(facilities)} storage facility record(s)."
    )

@router.post("", response_model=StandardResponse[StorageFacilityOut])
def create_storage_facility(payload: StorageFacilityCreate, db: Session = Depends(get_db)):
    fac = StorageFacilityModel(
        farm_id=payload.farm_id,
        name=payload.name,
        facility_type=payload.facility_type,
        latitude=payload.latitude,
        longitude=payload.longitude,
        total_capacity_metric_tons=payload.total_capacity_metric_tons,
        target_temperature_c=payload.target_temperature_c,
        target_relative_humidity=payload.target_relative_humidity,
        compatible_crops=payload.compatible_crops
    )
    db.add(fac)
    db.commit()
    db.refresh(fac)
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=fac,
        message="Storage facility registered."
    )
