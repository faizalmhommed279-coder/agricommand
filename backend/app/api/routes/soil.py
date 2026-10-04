from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import SoilProfileModel, SoilObservationModel, FieldModel
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import SoilProfileCreate, SoilProfileOut
from backend.app.integrations.soil.soilgrids import SoilGridsProvider

router = APIRouter()
soilgrids = SoilGridsProvider()

@router.get("/profiles", response_model=StandardResponse[List[SoilProfileOut]])
def list_soil_profiles(field_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(SoilProfileModel)
    if field_id:
        query = query.filter(SoilProfileModel.field_id == field_id)
    profiles = query.all()
    if not profiles:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No soil profiles configured. Connect field core lab samples or query ISRIC SoilGrids regional priors."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=profiles,
        message=f"Retrieved {len(profiles)} soil profile record(s)."
    )

@router.post("/profiles", response_model=StandardResponse[SoilProfileOut])
def create_soil_profile(payload: SoilProfileCreate, db: Session = Depends(get_db)):
    profile = SoilProfileModel(
        field_id=payload.field_id,
        texture_class=payload.texture_class,
        sand_fraction=payload.sand_fraction,
        clay_fraction=payload.clay_fraction,
        silt_fraction=payload.silt_fraction,
        organic_matter_percent=payload.organic_matter_percent,
        ph=payload.ph,
        field_capacity_volumetric=payload.field_capacity_volumetric,
        wilting_point_volumetric=payload.wilting_point_volumetric,
        source=payload.source,
        provenance=f"Registered source: {payload.source}"
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=profile,
        message="Soil profile logged."
    )

@router.get("/soilgrids-priors")
def get_soilgrids_priors(latitude: float, longitude: float):
    return soilgrids.fetch_regional_priors(latitude, longitude)
