from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# --- 1. Farm ---
class FarmCreate(BaseModel):
    name: str = Field(..., example="Green Valley Demonstration Farm")
    owner_id: Optional[str] = None
    description: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_area_hectares: Optional[float] = None
    geometry_geojson: Optional[Dict[str, Any]] = None

class FarmOut(FarmCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# --- 2. Field ---
class FieldCreate(BaseModel):
    farm_id: str
    name: str
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    slope_percent: Optional[float] = None
    elevation_meters: Optional[float] = None
    polygon_geojson: Optional[Dict[str, Any]] = None

class FieldOut(FieldCreate):
    id: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- 3. Crop Profile & Cycle ---
class CropProfileCreate(BaseModel):
    name: str
    variety: Optional[str] = None
    standard_duration_days: Optional[int] = None
    kc_init: Optional[float] = None
    kc_mid: Optional[float] = None
    kc_end: Optional[float] = None
    max_rooting_depth_m: Optional[float] = None
    critical_depletion_fraction: Optional[float] = None
    optimal_temp_min_c: Optional[float] = None
    optimal_temp_max_c: Optional[float] = None

class CropProfileOut(CropProfileCreate):
    id: str
    class Config:
        from_attributes = True

class CropCycleCreate(BaseModel):
    field_id: str
    crop_profile_id: Optional[str] = None
    planting_date: Optional[datetime] = None
    expected_harvest_date: Optional[datetime] = None
    current_growth_stage: Optional[str] = "Initial"
    status: str = "ACTIVE"

class CropCycleOut(CropCycleCreate):
    id: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- 4. Sensors & Ingestion ---
class SensorDeviceCreate(BaseModel):
    device_uid: str
    farm_id: str
    model_name: str = "ESP32 Gateway"
    firmware_version: Optional[str] = None

class SensorDeviceOut(SensorDeviceCreate):
    id: str
    is_connected: bool
    last_heartbeat: Optional[datetime] = None
    battery_level_volts: Optional[float] = None
    created_at: datetime
    class Config:
        from_attributes = True

class SensorCreate(BaseModel):
    sensor_uid: str
    device_id: str
    field_id: Optional[str] = None
    sensor_type: str
    unit: str
    min_operational_range: Optional[float] = None
    max_operational_range: Optional[float] = None
    calibration_offset: float = 0.0
    calibration_slope: float = 1.0

class SensorOut(SensorCreate):
    id: str
    is_active: bool
    last_calibrated_at: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True

# Ingestion Schema for ESP32 Gateways
class TelemetryIngestPayload(BaseModel):
    device_uid: str
    sensor_uid: str
    timestamp: datetime
    raw_value: float
    unit: str
    battery_voltage: Optional[float] = None
    calibration_hash: Optional[str] = None

class SensorObservationOut(BaseModel):
    id: str
    sensor_id: str
    field_id: Optional[str]
    raw_value: float
    calibrated_value: float
    unit: str
    observed_at: datetime
    data_category: str
    validation_status: str
    quality_flags: List[str]
    source: str
    provenance: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

# --- 5. Weather (NASA POWER / IMD) ---
class WeatherObservationOut(BaseModel):
    id: str
    farm_id: Optional[str]
    latitude: float
    longitude: float
    observed_at: datetime
    temp_min_c: Optional[float]
    temp_max_c: Optional[float]
    temp_mean_c: Optional[float]
    relative_humidity_percent: Optional[float]
    precipitation_mm: Optional[float]
    solar_radiation_mj_m2: Optional[float]
    wind_speed_2m_ms: Optional[float]
    data_category: str
    validation_status: str
    source: str
    provenance: Optional[str]
    class Config:
        from_attributes = True

# --- 6. Satellite (Sentinel-2) ---
class SatelliteObservationOut(BaseModel):
    id: str
    field_id: str
    observed_at: datetime
    granule_id: Optional[str]
    cloud_cover_percent: Optional[float]
    cloud_mask_applied: bool
    ndvi_mean: Optional[float]
    ndvi_min: Optional[float]
    ndvi_max: Optional[float]
    spectral_bands_json: Optional[Dict[str, Any]]
    data_category: str
    validation_status: str
    source: str
    provenance: Optional[str]
    class Config:
        from_attributes = True

# --- 7. Soil (ISRIC SoilGrids / Local) ---
class SoilProfileCreate(BaseModel):
    field_id: str
    texture_class: Optional[str] = None
    sand_fraction: Optional[float] = None
    clay_fraction: Optional[float] = None
    silt_fraction: Optional[float] = None
    organic_matter_percent: Optional[float] = None
    ph: Optional[float] = None
    field_capacity_volumetric: Optional[float] = None
    wilting_point_volumetric: Optional[float] = None
    source: str = "LOCAL_LAB"

class SoilProfileOut(SoilProfileCreate):
    id: str
    provenance: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

# --- 8. Water Resources & FAO-56 ---
class WaterResourceCreate(BaseModel):
    farm_id: str
    name: str
    type: str
    capacity_liters: Optional[float] = None
    current_level_liters: Optional[float] = None
    recharge_rate_lph: Optional[float] = None

class WaterResourceOut(WaterResourceCreate):
    id: str
    last_measured_at: Optional[datetime] = None
    provenance: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class FAO56CalculationRequest(BaseModel):
    field_id: str
    crop_cycle_id: str
    weather_observation_id: Optional[str] = None

class FAO56CalculationResult(BaseModel):
    field_id: str
    crop_name: str
    growth_stage: str
    kc: float
    et0_mm_day: float
    etc_mm_day: float
    net_irrigation_requirement_mm: float
    root_zone_depletion_mm: float
    stress_coefficient_ks: float
    calculation_timestamp: datetime
    input_provenance: Dict[str, Any]

# --- 9. Predictions ---
class PredictionRequest(BaseModel):
    field_id: str
    prediction_type: str # YIELD, WATER_DEMAND, CLIMATE_RISK

class PredictionOut(BaseModel):
    id: str
    model_id: Optional[str]
    field_id: str
    prediction_type: str
    predicted_value: float
    confidence_min: Optional[float]
    confidence_max: Optional[float]
    unit: Optional[str]
    target_horizon_date: Optional[datetime]
    data_category: str
    validation_status: str
    provenance: Optional[str]
    class Config:
        from_attributes = True

# --- 10. Optimization ---
class OptimizationRunRequest(BaseModel):
    farm_id: str
    domain: str = "WATER_ALLOCATION"
    available_water_liters: float
    field_priorities: Optional[Dict[str, int]] = None

class OptimizationRunOut(BaseModel):
    id: str
    farm_id: str
    domain: str
    solver: str
    objective_value: Optional[float]
    status: str
    parameters_json: Optional[Dict[str, Any]]
    schedule_result_json: Optional[Dict[str, Any]]
    data_category: str
    provenance: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

# --- 11. Recommendations (4 Explainable Questions) ---
class RecommendationCreate(BaseModel):
    farm_id: str
    field_id: Optional[str] = None
    title: str
    what_happened: str
    why_it_matters: str
    affected_field_summary: str
    suggested_action: str
    urgency: str = "MEDIUM"
    evidence_provenance: Optional[Dict[str, Any]] = None

class RecommendationOut(RecommendationCreate):
    id: str
    human_status: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- 12. Storage ---
class StorageFacilityCreate(BaseModel):
    farm_id: Optional[str] = None
    name: str
    facility_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_capacity_metric_tons: float
    target_temperature_c: Optional[float] = None
    target_relative_humidity: Optional[float] = None
    compatible_crops: List[str] = []

class StorageFacilityOut(StorageFacilityCreate):
    id: str
    current_occupancy_metric_tons: float
    created_at: datetime
    class Config:
        from_attributes = True

# --- 13. Audit & Data Quality ---
class AuditEventOut(BaseModel):
    id: str
    user_id: Optional[str]
    action: str
    entity_type: str
    entity_id: str
    previous_state: Optional[Dict[str, Any]]
    new_state: Optional[Dict[str, Any]]
    source: str
    model_version: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class DataQualitySummary(BaseModel):
    total_observations_received: int
    validated_count: int
    pending_count: int
    rejected_count: int
    stale_sensor_count: int
    calibration_issues_count: int
    data_sources_status: Dict[str, str]
