from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import SensorDeviceModel, SensorModel, FarmModel
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import (
    SensorDeviceCreate, SensorDeviceOut, SensorCreate, SensorOut
)

router = APIRouter()

@router.get("/devices", response_model=StandardResponse[List[SensorDeviceOut]])
def list_devices(farm_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(SensorDeviceModel)
    if farm_id:
        query = query.filter(SensorDeviceModel.farm_id == farm_id)
    devices = query.all()
    if not devices:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No sensor gateways registered. Connect an ESP32 hardware gateway to begin receiving field telemetry."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=devices,
        message=f"Retrieved {len(devices)} hardware gateway device(s)."
    )

@router.post("/devices", response_model=StandardResponse[SensorDeviceOut])
def register_device(payload: SensorDeviceCreate, db: Session = Depends(get_db)):
    farm = db.query(FarmModel).filter(FarmModel.id == payload.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found.")

    existing = db.query(SensorDeviceModel).filter(SensorDeviceModel.device_uid == payload.device_uid).first()
    if existing:
        return StandardResponse(
            status=StateStatus.AVAILABLE,
            data=existing,
            message=f"Hardware gateway '{existing.device_uid}' already provisioned."
        )

    device = SensorDeviceModel(
        device_uid=payload.device_uid,
        farm_id=payload.farm_id,
        model_name=payload.model_name,
        firmware_version=payload.firmware_version,
        is_connected=False
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=device,
        message=f"Hardware gateway '{device.device_uid}' registered. Awaiting initial MQTT/HTTP telemetry handshake."
    )

@router.get("", response_model=StandardResponse[List[SensorOut]])
def list_sensors(field_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(SensorModel)
    if field_id:
        query = query.filter(SensorModel.field_id == field_id)
    sensors = query.all()
    if not sensors:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No field sensors provisioned yet. Add capacitive, temperature, or flow sensors to this field."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=sensors,
        message=f"Retrieved {len(sensors)} sensor probe(s)."
    )

@router.post("", response_model=StandardResponse[SensorOut])
def register_sensor(payload: SensorCreate, db: Session = Depends(get_db)):
    device = db.query(SensorDeviceModel).filter(SensorDeviceModel.id == payload.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Parent hardware gateway device does not exist.")

    existing = db.query(SensorModel).filter(SensorModel.sensor_uid == payload.sensor_uid).first()
    if existing:
        return StandardResponse(
            status=StateStatus.AVAILABLE,
            data=existing,
            message=f"Sensor probe '{existing.sensor_uid}' already provisioned."
        )

    sensor = SensorModel(
        sensor_uid=payload.sensor_uid,
        device_id=payload.device_id,
        field_id=payload.field_id,
        sensor_type=payload.sensor_type,
        unit=payload.unit,
        min_operational_range=payload.min_operational_range,
        max_operational_range=payload.max_operational_range,
        calibration_offset=payload.calibration_offset,
        calibration_slope=payload.calibration_slope
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=sensor,
        message=f"Sensor probe '{sensor.sensor_uid}' provisioned and mapped to field."
    )
