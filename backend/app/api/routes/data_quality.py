from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import (
    DataQualityEventModel, SensorObservationModel, SensorDeviceModel, SensorModel
)
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import DataQualitySummary
from datetime import datetime, timezone, timedelta

router = APIRouter()

@router.get("/summary", response_model=StandardResponse[DataQualitySummary])
def get_data_quality_summary(db: Session = Depends(get_db)):
    total_obs = db.query(SensorObservationModel).count()
    if total_obs == 0:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=DataQualitySummary(
                total_observations_received=0,
                validated_count=0,
                pending_count=0,
                rejected_count=0,
                stale_sensor_count=0,
                calibration_issues_count=0,
                data_sources_status={
                    "ESP32_TELEMETRY": "NO_TELEMETRY",
                    "NASA_POWER": "NOT_CONNECTED",
                    "SENTINEL_2": "NOT_CONNECTED",
                    "ISRIC_SOILGRIDS": "STANDBY"
                }
            ),
            message="No sensor telemetry available in database. Data quality metrics will compute upon receipt of initial observations."
        )

    validated = db.query(SensorObservationModel).filter(SensorObservationModel.validation_status == "VALIDATED").count()
    pending = db.query(SensorObservationModel).filter(SensorObservationModel.validation_status == "PENDING").count()
    rejected = db.query(SensorObservationModel).filter(SensorObservationModel.validation_status == "REJECTED").count()
    
    # Check stale sensors (last heartbeat > 24 hours ago)
    stale_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    stale_count = db.query(SensorDeviceModel).filter(
        (SensorDeviceModel.last_heartbeat == None) | (SensorDeviceModel.last_heartbeat < stale_cutoff)
    ).count()

    calibration_issues = db.query(DataQualityEventModel).filter(
        DataQualityEventModel.issue_type == "CALIBRATION_DRIFT"
    ).count()

    summary = DataQualitySummary(
        total_observations_received=total_obs,
        validated_count=validated,
        pending_count=pending,
        rejected_count=rejected,
        stale_sensor_count=stale_count,
        calibration_issues_count=calibration_issues,
        data_sources_status={
            "ESP32_TELEMETRY": "ACTIVE" if total_obs > 0 else "OFFLINE",
            "NASA_POWER": "READY",
            "SENTINEL_2": "NOT_CONNECTED",
            "ISRIC_SOILGRIDS": "AVAILABLE"
        }
    )

    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=summary,
        message="Telemetry data quality health metrics compiled."
    )

@router.get("/events")
def list_quality_events(limit: int = 50, db: Session = Depends(get_db)):
    events = db.query(DataQualityEventModel).order_by(DataQualityEventModel.created_at.desc()).limit(limit).all()
    if not events:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No data quality anomalies recorded. All ingested telemetry passed validation checks or no observations exist."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=events,
        message=f"Retrieved {len(events)} data quality event(s)."
    )
