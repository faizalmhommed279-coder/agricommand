from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import FieldModel, FarmModel
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import FieldCreate, FieldOut
from backend.app.services.audit_service import log_audit_event

router = APIRouter()

@router.get("", response_model=StandardResponse[List[FieldOut]])
def list_fields(farm_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(FieldModel)
    if farm_id:
        query = query.filter(FieldModel.farm_id == farm_id)
    fields = query.order_by(FieldModel.created_at.desc()).all()
    
    if not fields:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No fields mapped yet. Draw or configure field boundaries on the map to begin spatial monitoring."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=fields,
        message=f"Retrieved {len(fields)} configured field(s)."
    )

@router.post("", response_model=StandardResponse[FieldOut])
def create_field(payload: FieldCreate, db: Session = Depends(get_db)):
    farm = db.query(FarmModel).filter(FarmModel.id == payload.farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent farm {payload.farm_id} does not exist."
        )

    field = FieldModel(
        farm_id=payload.farm_id,
        name=payload.name,
        area_hectares=payload.area_hectares,
        soil_type=payload.soil_type,
        slope_percent=payload.slope_percent,
        elevation_meters=payload.elevation_meters,
        polygon_geojson=payload.polygon_geojson
    )
    db.add(field)
    db.commit()
    db.refresh(field)

    log_audit_event(
        db=db,
        action="CREATE_FIELD",
        entity_type="FIELD",
        entity_id=field.id,
        source="SYSTEM_API",
        new_state={"name": field.name, "area_ha": field.area_hectares}
    )

    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=field,
        message=f"Field boundary '{field.name}' mapped and registered successfully."
    )

@router.get("/{field_id}", response_model=StandardResponse[Optional[FieldOut]])
def get_field(field_id: str, db: Session = Depends(get_db)):
    field = db.query(FieldModel).filter(FieldModel.id == field_id).first()
    if not field:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=None,
            message=f"Field with ID {field_id} not found."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=field,
        message="Field boundary retrieved."
    )
