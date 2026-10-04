from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from backend.app.core.database import get_db
from backend.app.models.entities import (
    SensorDeviceModel, SensorModel, SensorObservationModel,
    DataQualityEventModel, DataCategory
)
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import TelemetryIngestPayload, SensorObservationOut
from backend.app.validation.sensor_validator import TelemetryValidator, QualityFlag
from backend.app.services.audit_service import log_audit_event

router = APIRouter()

@router.get("", response_model=StandardResponse[List[SensorObservationOut]])
def get_telemetry(
    sensor_id: Optional[str] = None,
    field_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(SensorObservationModel)
    if sensor_id:
        query = query.filter(SensorObservationModel.sensor_id == sensor_id)
    if field_id:
        query = query.filter(SensorObservationModel.field_id == field_id)
        
    observations = query.order_by(SensorObservationModel.observed_at.desc()).limit(limit).all()
    if not observations:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No sensor telemetry available. Connect an ESP32 gateway to begin receiving field measurements."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=observations,
        message=f"Retrieved {len(observations)} validated telemetry records."
    )

@router.post("/ingest", response_model=StandardResponse[SensorObservationOut])
def ingest_esp32_telemetry(payload: TelemetryIngestPayload, db: Session = Depends(get_db)):
    """
    Dedicated ESP32 Ingestion Boundary:
    Applies the full TelemetryValidator pipeline:
    1. Identity Check
    2. Timestamp Check
    3. Calibration Check
    4. Operational Range Bounds
    5. Moving-Average Outlier / Spike Detection
    6. Hardware Safety Rule Check
    """
    # 1. Lookup Device & Sensor
    device = db.query(SensorDeviceModel).filter(SensorDeviceModel.device_uid == payload.device_uid).first()
    sensor = db.query(SensorModel).filter(SensorModel.sensor_uid == payload.sensor_uid).first()
    
    known_sensor = (sensor is not None and device is not None)
    
    # Retrieve recent window for spike detection
    recent_values = []
    if sensor:
        recent_obs = db.query(SensorObservationModel.calibrated_value)\
            .filter(SensorObservationModel.sensor_id == sensor.id)\
            .order_by(SensorObservationModel.observed_at.desc()).limit(5).all()
        recent_values = [r[0] for r in recent_obs]

    validation = TelemetryValidator.validate_reading(
        raw_value=payload.raw_value,
        timestamp=payload.timestamp,
        sensor_type=sensor.sensor_type if sensor else "unknown",
        known_sensor=known_sensor,
        min_range=sensor.min_operational_range if sensor else None,
        max_range=sensor.max_operational_range if sensor else None,
        cal_offset=sensor.calibration_offset if sensor else 0.0,
        cal_slope=sensor.calibration_slope if sensor else 1.0,
        last_calibrated_at=sensor.last_calibrated_at if sensor else None,
        recent_values_window=recent_values
    )

    # If identity unknown, record quality event and abort ingestion
    if not known_sensor:
        event = DataQualityEventModel(
            source_entity_id=payload.sensor_uid,
            entity_type="SENSOR",
            issue_type="UNKNOWN_HARDWARE_IDENTITY",
            severity="CRITICAL",
            description=f"Received telemetry from unprovisioned sensor UID: {payload.sensor_uid} on gateway: {payload.device_uid}",
            raw_payload=payload.model_dump(mode="json")
        )
        db.add(event)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Telemetry rejected: Sensor UID {payload.sensor_uid} is not provisioned on gateway {payload.device_uid}."
        )

    # Update device heartbeat and connectivity state
    device.is_connected = True
    device.last_heartbeat = datetime.now(timezone.utc)
    if payload.battery_voltage is not None:
        device.battery_level_volts = payload.battery_voltage

    # Record observation
    observation = SensorObservationModel(
        sensor_id=sensor.id,
        field_id=sensor.field_id,
        raw_value=payload.raw_value,
        calibrated_value=validation.calibrated_value,
        unit=payload.unit,
        observed_at=payload.timestamp,
        data_category=DataCategory.LIVE_SENSOR_TELEMETRY.value,
        validation_status=validation.validation_status,
        quality_flags=[f.value for f in validation.flags],
        source="ESP32_TELEMETRY_PIPELINE",
        provenance=validation.provenance_summary
    )
    db.add(observation)

    # If validation failed, also log a DataQualityEvent
    if not validation.is_valid:
        quality_event = DataQualityEventModel(
            source_entity_id=sensor.sensor_uid,
            entity_type="SENSOR",
            issue_type=validation.validation_status,
            severity="WARNING",
            description=f"Sensor observation rejected: {validation.rejection_reason}",
            raw_payload=payload.model_dump(mode="json")
        )
        db.add(quality_event)

    db.commit()
    db.refresh(observation)

    resp_status = StateStatus.AVAILABLE if validation.is_valid else StateStatus.INVALID
    msg = "Telemetry validated and committed." if validation.is_valid else f"Telemetry ingested with validation flags: {validation.rejection_reason}"

    return StandardResponse(
        status=resp_status,
        data=observation,
        message=msg
    )
