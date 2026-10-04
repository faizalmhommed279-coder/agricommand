from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class QualityFlag(str, Enum):
    IDENTITY_VALID = "IDENTITY_VALID"
    IDENTITY_UNKNOWN = "IDENTITY_UNKNOWN"
    TIMESTAMP_VALID = "TIMESTAMP_VALID"
    TIMESTAMP_FUTURE = "TIMESTAMP_FUTURE"
    TIMESTAMP_STALE = "TIMESTAMP_STALE"
    RANGE_VALID = "RANGE_VALID"
    RANGE_UNDERFLOW = "RANGE_UNDERFLOW"
    RANGE_OVERFLOW = "RANGE_OVERFLOW"
    SPIKE_OUTLIER = "SPIKE_OUTLIER"
    MOVING_AVG_CONSISTENT = "MOVING_AVG_CONSISTENT"
    CALIBRATION_APPLIED = "CALIBRATION_APPLIED"
    CALIBRATION_EXPIRED = "CALIBRATION_EXPIRED"
    SAFETY_INTERLOCK_HOLD = "SAFETY_INTERLOCK_HOLD"

@dataclass
class ValidationResult:
    is_valid: bool
    calibrated_value: float
    raw_value: float
    flags: List[QualityFlag]
    validation_status: str # VALIDATED, REJECTED, STALE, CALIBRATION_DRIFT
    safety_authorization_granted: bool
    rejection_reason: Optional[str] = None
    provenance_summary: str = ""

# Operational ranges by sensor type
STANDARD_SENSOR_RANGES = {
    "capacitive_soil_moisture": {"min": 0.0, "max": 100.0, "unit": "%"},
    "sht31_temperature": {"min": -20.0, "max": 65.0, "unit": "°C"},
    "sht31_humidity": {"min": 0.0, "max": 100.0, "unit": "%"},
    "ds18b20_soil_temp": {"min": -10.0, "max": 60.0, "unit": "°C"},
    "water_flow": {"min": 0.0, "max": 500.0, "unit": "L/min"},
    "hx711_load_cell": {"min": 0.0, "max": 50000.0, "unit": "kg"},
    "ndir_co2": {"min": 200.0, "max": 10000.0, "unit": "ppm"},
    "water_level": {"min": 0.0, "max": 20.0, "unit": "m"},
}

class TelemetryValidator:
    """
    Dedicated Sensor Validation Pipeline ensuring:
    Observation -> Identity validation -> Timestamp validation -> Range validation
    -> Outlier detection -> Quality filtering -> Calibration check -> Safety Interlock Check
    """
    
    @staticmethod
    def validate_reading(
        raw_value: float,
        timestamp: datetime,
        sensor_type: str,
        known_sensor: bool,
        min_range: Optional[float] = None,
        max_range: Optional[float] = None,
        cal_offset: float = 0.0,
        cal_slope: float = 1.0,
        last_calibrated_at: Optional[datetime] = None,
        recent_values_window: Optional[List[float]] = None
    ) -> ValidationResult:
        flags: List[QualityFlag] = []
        is_valid = True
        rejection_reasons = []
        now = datetime.now(timezone.utc)
        
        # Ensure timestamp is timezone-aware
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # 1. Identity Validation
        if not known_sensor:
            flags.append(QualityFlag.IDENTITY_UNKNOWN)
            is_valid = False
            rejection_reasons.append("Unknown or unprovisioned sensor hardware identity.")
        else:
            flags.append(QualityFlag.IDENTITY_VALID)

        # 2. Timestamp Validation (reject future timestamps and stale > 7 days)
        if timestamp > now + timedelta(minutes=5):
            flags.append(QualityFlag.TIMESTAMP_FUTURE)
            is_valid = False
            rejection_reasons.append("Telemetry timestamp is in the future.")
        elif timestamp < now - timedelta(days=7):
            flags.append(QualityFlag.TIMESTAMP_STALE)
            flags.append(QualityFlag.SAFETY_INTERLOCK_HOLD)
            is_valid = False
            rejection_reasons.append("Telemetry observation is stale (>7 days old).")
        else:
            flags.append(QualityFlag.TIMESTAMP_VALID)

        # 3. Calibration Application
        # Calibrated = (Raw * Slope) + Offset
        calibrated_value = (raw_value * cal_slope) + cal_offset
        if last_calibrated_at:
            if last_calibrated_at.tzinfo is None:
                last_calibrated_at = last_calibrated_at.replace(tzinfo=timezone.utc)
            if now - last_calibrated_at > timedelta(days=180):
                flags.append(QualityFlag.CALIBRATION_EXPIRED)
                flags.append(QualityFlag.SAFETY_INTERLOCK_HOLD)
            else:
                flags.append(QualityFlag.CALIBRATION_APPLIED)
        else:
            flags.append(QualityFlag.CALIBRATION_APPLIED)

        # 4. Range Validation
        spec = STANDARD_SENSOR_RANGES.get(sensor_type, {"min": -1000.0, "max": 100000.0})
        effective_min = min_range if min_range is not None else spec["min"]
        effective_max = max_range if max_range is not None else spec["max"]

        if calibrated_value < effective_min:
            flags.append(QualityFlag.RANGE_UNDERFLOW)
            is_valid = False
            rejection_reasons.append(f"Value {calibrated_value} is below physical minimum operational bound {effective_min}.")
        elif calibrated_value > effective_max:
            flags.append(QualityFlag.RANGE_OVERFLOW)
            is_valid = False
            rejection_reasons.append(f"Value {calibrated_value} exceeds physical maximum operational bound {effective_max}.")
        else:
            flags.append(QualityFlag.RANGE_VALID)

        # 5. Moving-Average Outlier / Sudden Spike Detection
        if recent_values_window and len(recent_values_window) >= 3:
            avg = sum(recent_values_window) / len(recent_values_window)
            # If standard deviation or delta is immense (e.g. > 400% deviation on positive values)
            if avg > 0 and abs(calibrated_value - avg) > (avg * 3.0 + 10.0):
                flags.append(QualityFlag.SPIKE_OUTLIER)
                flags.append(QualityFlag.SAFETY_INTERLOCK_HOLD)
            else:
                flags.append(QualityFlag.MOVING_AVG_CONSISTENT)

        # 6. Hardware Safety Rule Check:
        # "An unvalidated sensor reading must NEVER directly trigger a high-impact automated action."
        # If any safety interlock hold flag is set or is_valid is False, safety authorization is strictly FALSE.
        safety_authorization_granted = is_valid and (QualityFlag.SAFETY_INTERLOCK_HOLD not in flags)

        validation_status = "VALIDATED" if is_valid else "REJECTED"
        if QualityFlag.CALIBRATION_EXPIRED in flags:
            validation_status = "CALIBRATION_DRIFT"
        elif QualityFlag.TIMESTAMP_STALE in flags:
            validation_status = "STALE"

        provenance_str = (
            f"Validated via AgriCommand TelemetryValidator pipeline at {now.isoformat()}. "
            f"SensorType={sensor_type}, Raw={raw_value}, Calibrated={calibrated_value}, "
            f"PassedAllChecks={is_valid}, SafetyAuth={safety_authorization_granted}."
        )

        return ValidationResult(
            is_valid=is_valid,
            calibrated_value=calibrated_value,
            raw_value=raw_value,
            flags=flags,
            validation_status=validation_status,
            safety_authorization_granted=safety_authorization_granted,
            rejection_reason="; ".join(rejection_reasons) if rejection_reasons else None,
            provenance_summary=provenance_str
        )
