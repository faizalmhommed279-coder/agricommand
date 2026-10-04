from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import CropProfileModel, CropCycleModel
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import CropProfileCreate, CropProfileOut, CropCycleCreate, CropCycleOut

router = APIRouter()

@router.get("/profiles", response_model=StandardResponse[List[CropProfileOut]])
def list_crop_profiles(db: Session = Depends(get_db)):
    profiles = db.query(CropProfileModel).all()
    if not profiles:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No crop profiles registered yet. Configure crop profiles to calibrate FAO-56 Kc coefficients."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=profiles,
        message=f"Retrieved {len(profiles)} crop profile(s)."
    )

@router.post("/profiles", response_model=StandardResponse[CropProfileOut])
def create_crop_profile(payload: CropProfileCreate, db: Session = Depends(get_db)):
    profile = CropProfileModel(
        name=payload.name,
        variety=payload.variety,
        standard_duration_days=payload.standard_duration_days,
        kc_init=payload.kc_init,
        kc_mid=payload.kc_mid,
        kc_end=payload.kc_end,
        max_rooting_depth_m=payload.max_rooting_depth_m,
        critical_depletion_fraction=payload.critical_depletion_fraction,
        optimal_temp_min_c=payload.optimal_temp_min_c,
        optimal_temp_max_c=payload.optimal_temp_max_c
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=profile,
        message="Crop profile registered."
    )

@router.get("/cycles", response_model=StandardResponse[List[CropCycleOut]])
def list_crop_cycles(field_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CropCycleModel)
    if field_id:
        query = query.filter(CropCycleModel.field_id == field_id)
    cycles = query.order_by(CropCycleModel.created_at.desc()).all()
    if not cycles:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No active crop cycles configured for this field."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=cycles,
        message=f"Retrieved {len(cycles)} crop cycle(s)."
    )

@router.post("/cycles", response_model=StandardResponse[CropCycleOut])
def create_crop_cycle(payload: CropCycleCreate, db: Session = Depends(get_db)):
    cycle = CropCycleModel(
        field_id=payload.field_id,
        crop_profile_id=payload.crop_profile_id,
        planting_date=payload.planting_date,
        expected_harvest_date=payload.expected_harvest_date,
        current_growth_stage=payload.current_growth_stage,
        status=payload.status
    )
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=cycle,
        message="Field crop cycle initialized."
    )
