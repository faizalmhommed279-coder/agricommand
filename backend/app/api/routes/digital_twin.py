from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from backend.app.core.database import get_db
from backend.app.models.entities import (
    FarmModel, FieldModel, CropCycleModel, CropProfileModel,
    SoilProfileModel, SensorDeviceModel, SensorModel, SensorObservationModel,
    WeatherObservationModel, SatelliteObservationModel, WaterResourceModel,
    OptimizationRunModel, RecommendationModel, OutcomeModel, AuditEventModel
)
from backend.app.schemas.common import StandardResponse, StateStatus

router = APIRouter()

@router.get("")
def get_digital_twin(farm_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Central Farm Digital Twin Aggregator:
    Unifies all interconnected agricultural entities into a single coherent state graph.
    Respects strict empty-state rules with explicit StateStatus flags for each subsystem.
    """
    # 1. Farm
    farm = None
    if farm_id:
        farm = db.query(FarmModel).filter(FarmModel.id == farm_id).first()
    else:
        farm = db.query(FarmModel).first()

    if not farm:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=None,
            message="No farm registered. Register a farm to initiate the Farm Digital Twin."
        )

    # 2. Fields
    fields = db.query(FieldModel).filter(FieldModel.farm_id == farm.id).all()
    field_ids = [f.id for f in fields]

    # 3. Crop Cycles
    crop_cycles = []
    if field_ids:
        crop_cycles = db.query(CropCycleModel).filter(CropCycleModel.field_id.in_(field_ids)).all()

    # 4. Sensor Devices & Probes
    devices = db.query(SensorDeviceModel).filter(SensorDeviceModel.farm_id == farm.id).all()
    device_ids = [d.id for d in devices]
    sensors = []
    latest_telemetry = []
    if device_ids:
        sensors = db.query(SensorModel).filter(SensorModel.device_id.in_(device_ids)).all()
        sensor_ids = [s.id for s in sensors]
        if sensor_ids:
            latest_telemetry = db.query(SensorObservationModel)\
                .filter(SensorObservationModel.sensor_id.in_(sensor_ids))\
                .order_by(SensorObservationModel.observed_at.desc()).limit(20).all()

    # 5. Weather Observations
    weather_obs = db.query(WeatherObservationModel)\
        .filter(WeatherObservationModel.farm_id == farm.id)\
        .order_by(WeatherObservationModel.observed_at.desc()).limit(10).all()

    # 6. Satellite Observations
    satellite_obs = []
    if field_ids:
        satellite_obs = db.query(SatelliteObservationModel)\
            .filter(SatelliteObservationModel.field_id.in_(field_ids))\
            .order_by(SatelliteObservationModel.observed_at.desc()).limit(10).all()

    # 7. Soil Profiles
    soil_profiles = []
    if field_ids:
        soil_profiles = db.query(SoilProfileModel).filter(SoilProfileModel.field_id.in_(field_ids)).all()

    # 8. Water Resources
    water_resources = db.query(WaterResourceModel).filter(WaterResourceModel.farm_id == farm.id).all()

    # 9. Recommendations
    recommendations = db.query(RecommendationModel)\
        .filter(RecommendationModel.farm_id == farm.id)\
        .order_by(RecommendationModel.created_at.desc()).limit(10).all()

    # 10. Optimization Runs
    optimizations = db.query(OptimizationRunModel)\
        .filter(OptimizationRunModel.farm_id == farm.id)\
        .order_by(OptimizationRunModel.created_at.desc()).limit(5).all()

    # 11. Outcomes
    outcomes = []
    if field_ids:
        outcomes = db.query(OutcomeModel)\
            .filter(OutcomeModel.field_id.in_(field_ids))\
            .order_by(OutcomeModel.observed_at.desc()).limit(10).all()

    # Build Nine-Stage Decision Loop Statuses
    decision_loop = {
        "step_1_registration": {
            "status": "COMPLETE",
            "details": f"Farm '{farm.name}' registered."
        },
        "step_2_field_mapping": {
            "status": "COMPLETE" if fields else "AWAITING_DATA",
            "details": f"{len(fields)} field(s) mapped." if fields else "No fields configured."
        },
        "step_3_data_collection": {
            "status": "PROCESSING" if latest_telemetry else "AWAITING_DATA",
            "details": f"{len(latest_telemetry)} observations received from {len(devices)} device(s)." if latest_telemetry else "No sensor telemetry available."
        },
        "step_4_validation": {
            "status": "COMPLETE" if any(t.validation_status == "VALIDATED" for t in latest_telemetry) else "NOT_STARTED",
            "details": "Telemetry validation pipeline active with hardware safety interlocks."
        },
        "step_5_prediction": {
            "status": "NOT_CONFIGURED",
            "details": "Prediction model not connected. Interface awaiting machine learning models."
        },
        "step_6_optimization": {
            "status": "COMPLETE" if optimizations else "AWAITING_DATA",
            "details": f"{len(optimizations)} run(s) logged." if optimizations else "Optimization data unavailable."
        },
        "step_7_recommendation": {
            "status": "COMPLETE" if recommendations else "NO_DATA",
            "details": f"{len(recommendations)} advisory record(s)." if recommendations else "Insufficient validated evidence to generate a recommendation."
        },
        "step_8_action": {
            "status": "AWAITING_HUMAN_CONFIRMATION" if recommendations else "NOT_STARTED",
            "details": "Hardware safety interlock requires human operator confirmation for actuation."
        },
        "step_9_outcome_learning": {
            "status": "COMPLETE" if outcomes else "NOT_STARTED",
            "details": f"{len(outcomes)} outcome record(s) evaluated." if outcomes else "No observed outcomes recorded."
        }
    }

    def to_dict(obj):
        if obj is None:
            return None
        d = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.name)
            if hasattr(val, 'isoformat'):
                d[col.name] = val.isoformat()
            else:
                d[col.name] = val
        return d

    twin_state = {
        "farm": to_dict(farm),
        "fields": [to_dict(f) for f in fields],
        "crop_cycles": [to_dict(c) for c in crop_cycles],
        "devices": [to_dict(d) for d in devices],
        "sensors": [to_dict(s) for s in sensors],
        "latest_telemetry": [to_dict(t) for t in latest_telemetry],
        "weather_observations": [to_dict(w) for w in weather_obs],
        "satellite_observations": [to_dict(s) for s in satellite_obs],
        "soil_profiles": [to_dict(s) for s in soil_profiles],
        "water_resources": [to_dict(w) for w in water_resources],
        "recommendations": [to_dict(r) for r in recommendations],
        "optimizations": [to_dict(o) for o in optimizations],
        "outcomes": [to_dict(o) for o in outcomes],
        "decision_loop": decision_loop,
        "subsystem_states": {
            "farm": StateStatus.AVAILABLE.value,
            "fields": StateStatus.AVAILABLE.value if fields else StateStatus.NO_DATA.value,
            "sensors": StateStatus.AVAILABLE.value if latest_telemetry else StateStatus.NO_DATA.value,
            "weather": StateStatus.AVAILABLE.value if weather_obs else StateStatus.NOT_CONFIGURED.value,
            "satellite": StateStatus.AVAILABLE.value if satellite_obs else StateStatus.NO_DATA.value,
            "prediction": StateStatus.NOT_CONFIGURED.value,
            "optimization": StateStatus.AVAILABLE.value if optimizations else StateStatus.INSUFFICIENT_DATA.value,
            "recommendation": StateStatus.AVAILABLE.value if recommendations else StateStatus.NO_DATA.value
        }
    }

    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=twin_state,
        message=f"Farm Digital Twin synchronized for '{farm.name}'."
    )
