from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from backend.app.core.database import get_db
from backend.app.models.entities import (
    WaterResourceModel, FieldModel, CropCycleModel,
    SoilProfileModel, WeatherObservationModel, SensorObservationModel
)
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import (
    WaterResourceCreate, WaterResourceOut, FAO56CalculationRequest
)
from backend.app.analytics.fao56 import (
    FAO56WaterDemandEngine, FAO56WeatherInput, FAO56CropInput, FAO56SoilInput
)

router = APIRouter()

@router.get("/resources", response_model=StandardResponse[List[WaterResourceOut]])
def list_water_resources(farm_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(WaterResourceModel)
    if farm_id:
        query = query.filter(WaterResourceModel.farm_id == farm_id)
    resources = query.all()
    if not resources:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No farm water resources configured. Register borewells, farm ponds, or canal supplies to track hydrological balances."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=resources,
        message=f"Retrieved {len(resources)} water resource(s)."
    )

@router.post("/resources", response_model=StandardResponse[WaterResourceOut])
def create_water_resource(payload: WaterResourceCreate, db: Session = Depends(get_db)):
    resource = WaterResourceModel(
        farm_id=payload.farm_id,
        name=payload.name,
        type=payload.type,
        capacity_liters=payload.capacity_liters,
        current_level_liters=payload.current_level_liters,
        recharge_rate_lph=payload.recharge_rate_lph,
        provenance="Registered via AgriCommand Resource Manager"
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=resource,
        message="Water resource registered."
    )

@router.post("/fao56-calculate")
def calculate_fao56(payload: FAO56CalculationRequest, db: Session = Depends(get_db)):
    """
    Executes FAO-56 Penman-Monteith water-demand calculation only if validated inputs exist.
    """
    field = db.query(FieldModel).filter(FieldModel.id == payload.field_id).first()
    cycle = db.query(CropCycleModel).filter(CropCycleModel.id == payload.crop_cycle_id).first()
    
    if not field or not cycle:
        return {
            "status": StateStatus.INSUFFICIENT_DATA.value,
            "message": "Field or Crop Cycle entity not found.",
            "data": None
        }

    # Fetch crop profile
    crop_prof = cycle.crop_profile
    crop_input = None
    if crop_prof:
        crop_input = FAO56CropInput(
            crop_name=crop_prof.name,
            growth_stage=cycle.current_growth_stage or "MID",
            kc_init=crop_prof.kc_init or 0.4,
            kc_mid=crop_prof.kc_mid or 1.15,
            kc_end=crop_prof.kc_end or 0.5,
            rooting_depth_m=crop_prof.max_rooting_depth_m or 1.0,
            depletion_fraction_p=crop_prof.critical_depletion_fraction or 0.5
        )

    # Fetch soil profile
    soil_prof = db.query(SoilProfileModel).filter(SoilProfileModel.field_id == field.id).first()
    soil_input = None
    if soil_prof and soil_prof.field_capacity_volumetric and soil_prof.wilting_point_volumetric:
        # Check if live validated soil moisture sensor exists
        latest_sensor = db.query(SensorObservationModel)\
            .filter(SensorObservationModel.field_id == field.id, SensorObservationModel.validation_status == "VALIDATED")\
            .order_by(SensorObservationModel.observed_at.desc()).first()
        
        sm_vol = (latest_sensor.calibrated_value / 100.0) if latest_sensor else None

        soil_input = FAO56SoilInput(
            field_capacity_volumetric=soil_prof.field_capacity_volumetric,
            wilting_point_volumetric=soil_prof.wilting_point_volumetric,
            current_soil_moisture_volumetric=sm_vol
        )

    # Fetch weather observation
    weather_obs = None
    if payload.weather_observation_id:
        weather_obs = db.query(WeatherObservationModel).filter(WeatherObservationModel.id == payload.weather_observation_id).first()
    else:
        weather_obs = db.query(WeatherObservationModel).filter(WeatherObservationModel.farm_id == field.farm_id).order_by(WeatherObservationModel.observed_at.desc()).first()

    weather_input = None
    if weather_obs and weather_obs.temp_mean_c is not None and weather_obs.solar_radiation_mj_m2 is not None:
        day_of_year = weather_obs.observed_at.timetuple().tm_yday
        weather_input = FAO56WeatherInput(
            temp_min_c=weather_obs.temp_min_c or (weather_obs.temp_mean_c - 5.0),
            temp_max_c=weather_obs.temp_max_c or (weather_obs.temp_mean_c + 5.0),
            temp_mean_c=weather_obs.temp_mean_c,
            relative_humidity_percent=weather_obs.relative_humidity_percent or 60.0,
            solar_radiation_mj_m2=weather_obs.solar_radiation_mj_m2,
            wind_speed_2m_ms=weather_obs.wind_speed_2m_ms or 2.0,
            elevation_m=field.elevation_meters or 100.0,
            latitude_deg=weather_obs.latitude,
            day_of_year=day_of_year
        )

    return FAO56WaterDemandEngine.compute_water_balance(
        weather=weather_input,
        crop=crop_input,
        soil=soil_input
    )
