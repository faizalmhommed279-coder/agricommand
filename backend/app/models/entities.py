import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
import enum

def utc_now():
    return datetime.now(timezone.utc)

class DataCategory(str, enum.Enum):
    TRAINING_DATA = "TRAINING_DATA"
    LIVE_SENSOR_TELEMETRY = "LIVE_SENSOR_TELEMETRY"
    SIMULATION_DATA = "SIMULATION_DATA"
    REGIONAL_WEATHER_DATA = "REGIONAL_WEATHER_DATA"
    SATELLITE_OBSERVATION = "SATELLITE_OBSERVATION"
    SOIL_DATA = "SOIL_DATA"
    MODEL_OUTPUT = "MODEL_OUTPUT"
    OPTIMIZATION_OUTPUT = "OPTIMIZATION_OUTPUT"
    OBSERVED_OUTCOME = "OBSERVED_OUTCOME"

class ValidationStatus(str, enum.Enum):
    VALIDATED = "VALIDATED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    STALE = "STALE"
    CALIBRATION_DRIFT = "CALIBRATION_DRIFT"

class StateStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    NO_DATA = "NO_DATA"
    PROCESSING = "PROCESSING"
    STALE = "STALE"
    INVALID = "INVALID"
    FAILED = "FAILED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

# 1. User
class UserModel(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="farmer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# 2. Farm
class FarmModel(Base):
    __tablename__ = "farms"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    description = Column(Text, nullable=True)
    location_name = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    total_area_hectares = Column(Float, nullable=True)
    geometry_geojson = Column(JSON, nullable=True)  # GeoJSON polygon/multipolygon
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    fields = relationship("FieldModel", back_populates="farm", cascade="all, delete-orphan")
    devices = relationship("SensorDeviceModel", back_populates="farm")

# 3. Field
class FieldModel(Base):
    __tablename__ = "fields"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    area_hectares = Column(Float, nullable=True)
    soil_type = Column(String(100), nullable=True)
    slope_percent = Column(Float, nullable=True)
    elevation_meters = Column(Float, nullable=True)
    polygon_geojson = Column(JSON, nullable=True)  # GeoJSON Polygon of field boundary
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    farm = relationship("FarmModel", back_populates="fields")
    crop_cycles = relationship("CropCycleModel", back_populates="field", cascade="all, delete-orphan")
    sensors = relationship("SensorModel", back_populates="field")

# 4. Crop Profile & Crop Cycle
class CropProfileModel(Base):
    __tablename__ = "crop_profiles"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)  # e.g. Wheat, Maize, Cotton
    variety = Column(String(255), nullable=True)
    standard_duration_days = Column(Integer, nullable=True)
    kc_init = Column(Float, nullable=True)      # FAO-56 crop coefficient initial
    kc_mid = Column(Float, nullable=True)       # FAO-56 mid stage
    kc_end = Column(Float, nullable=True)       # FAO-56 end stage
    max_rooting_depth_m = Column(Float, nullable=True)
    critical_depletion_fraction = Column(Float, nullable=True) # p factor
    optimal_temp_min_c = Column(Float, nullable=True)
    optimal_temp_max_c = Column(Float, nullable=True)

class CropCycleModel(Base):
    __tablename__ = "crop_cycles"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=False, index=True)
    crop_profile_id = Column(String(36), ForeignKey("crop_profiles.id"), nullable=True)
    planting_date = Column(DateTime(timezone=True), nullable=True)
    expected_harvest_date = Column(DateTime(timezone=True), nullable=True)
    actual_harvest_date = Column(DateTime(timezone=True), nullable=True)
    current_growth_stage = Column(String(100), nullable=True) # e.g. Initial, Vegetative, Mid-season, Late
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    field = relationship("FieldModel", back_populates="crop_cycles")
    crop_profile = relationship("CropProfileModel")

# 5. Soil Profile & Observations
class SoilProfileModel(Base):
    __tablename__ = "soil_profiles"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=False, index=True)
    texture_class = Column(String(100), nullable=True) # Sandy Loam, Clay, etc.
    sand_fraction = Column(Float, nullable=True)
    clay_fraction = Column(Float, nullable=True)
    silt_fraction = Column(Float, nullable=True)
    organic_matter_percent = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    cation_exchange_capacity = Column(Float, nullable=True)
    field_capacity_volumetric = Column(Float, nullable=True)
    wilting_point_volumetric = Column(Float, nullable=True)
    source = Column(String(100), default="LOCAL_LAB") # LOCAL_LAB vs ISRIC_SOILGRIDS_PRIOR
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class SoilObservationModel(Base):
    __tablename__ = "soil_observations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=False, index=True)
    sampling_date = Column(DateTime(timezone=True), nullable=False)
    depth_cm = Column(Float, nullable=True)
    moisture_percentage = Column(Float, nullable=True)
    nitrogen_mg_kg = Column(Float, nullable=True)
    phosphorus_mg_kg = Column(Float, nullable=True)
    potassium_mg_kg = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    ec_ds_m = Column(Float, nullable=True)
    data_category = Column(String(50), default=DataCategory.SOIL_DATA.value)
    validation_status = Column(String(50), default=ValidationStatus.VALIDATED.value)
    source = Column(String(100), default="FIELD_TEST")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# 6. Sensor Device (e.g., ESP32 Gateway) & Sensors
class SensorDeviceModel(Base):
    __tablename__ = "sensor_devices"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_uid = Column(String(100), unique=True, nullable=False, index=True) # e.g. ESP32-GW-001
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    model_name = Column(String(100), default="ESP32 Gateway")
    firmware_version = Column(String(50), nullable=True)
    is_connected = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    battery_level_volts = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    farm = relationship("FarmModel", back_populates="devices")
    sensors = relationship("SensorModel", back_populates="device", cascade="all, delete-orphan")

class SensorModel(Base):
    __tablename__ = "sensors"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sensor_uid = Column(String(100), unique=True, nullable=False, index=True)
    device_id = Column(String(36), ForeignKey("sensor_devices.id"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=True)
    sensor_type = Column(String(100), nullable=False) # capacitive_soil_moisture, sht31_temp_humidity, ds18b20, water_flow, hx711_load_cell
    unit = Column(String(50), nullable=False)
    min_operational_range = Column(Float, nullable=True)
    max_operational_range = Column(Float, nullable=True)
    calibration_offset = Column(Float, default=0.0)
    calibration_slope = Column(Float, default=1.0)
    last_calibrated_at = Column(DateTime(timezone=True), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    device = relationship("SensorDeviceModel", back_populates="sensors")
    field = relationship("FieldModel", back_populates="sensors")
    observations = relationship("SensorObservationModel", back_populates="sensor", cascade="all, delete-orphan")

# 7. Sensor Observation (Live Telemetry with Traceable Provenance)
class SensorObservationModel(Base):
    __tablename__ = "sensor_observations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sensor_id = Column(String(36), ForeignKey("sensors.id"), nullable=False, index=True)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=True, index=True)
    raw_value = Column(Float, nullable=False)
    calibrated_value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    data_category = Column(String(50), default=DataCategory.LIVE_SENSOR_TELEMETRY.value)
    validation_status = Column(String(50), default=ValidationStatus.PENDING.value)
    quality_flags = Column(JSON, default=list) # e.g. ["RANGE_PASS", "TIMESTAMP_PASS"]
    source = Column(String(100), default="ESP32_MQTT")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    sensor = relationship("SensorModel", back_populates="observations")

# 8. Weather Observations (NASA POWER / IMD)
class WeatherObservationModel(Base):
    __tablename__ = "weather_observations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    temp_min_c = Column(Float, nullable=True)
    temp_max_c = Column(Float, nullable=True)
    temp_mean_c = Column(Float, nullable=True)
    relative_humidity_percent = Column(Float, nullable=True)
    precipitation_mm = Column(Float, nullable=True)
    solar_radiation_mj_m2 = Column(Float, nullable=True)
    wind_speed_2m_ms = Column(Float, nullable=True)
    data_category = Column(String(50), default=DataCategory.REGIONAL_WEATHER_DATA.value)
    validation_status = Column(String(50), default=ValidationStatus.VALIDATED.value)
    source = Column(String(100), nullable=False) # e.g. "NASA_POWER", "IMD_GRIDDED"
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# 9. Satellite Observations (Copernicus Sentinel-2 13 Bands & Spectral)
class SatelliteObservationModel(Base):
    __tablename__ = "satellite_observations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=False, index=True)
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    granule_id = Column(String(255), nullable=True)
    cloud_cover_percent = Column(Float, nullable=True)
    cloud_mask_applied = Column(Boolean, default=True)
    ndvi_mean = Column(Float, nullable=True)
    ndvi_min = Column(Float, nullable=True)
    ndvi_max = Column(Float, nullable=True)
    spectral_bands_json = Column(JSON, nullable=True) # B02, B03, B04 (Red), B08 (NIR), etc.
    data_category = Column(String(50), default=DataCategory.SATELLITE_OBSERVATION.value)
    validation_status = Column(String(50), default=ValidationStatus.VALIDATED.value)
    source = Column(String(100), default="COPERNICUS_SENTINEL_2")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# 10. Water Resources & Constraints (FAO-56 & Hydrology)
class WaterResourceModel(Base):
    __tablename__ = "water_resources"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False) # Borewell, Canal, Farm Pond
    type = Column(String(100), nullable=False)
    capacity_liters = Column(Float, nullable=True)
    current_level_liters = Column(Float, nullable=True)
    recharge_rate_lph = Column(Float, nullable=True)
    last_measured_at = Column(DateTime(timezone=True), nullable=True)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class ResourceConstraintModel(Base):
    __tablename__ = "resource_constraints"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    constraint_type = Column(String(100), nullable=False) # WATER_DAILY_MAX, PUMP_POWER_HOURS, LABOR_HOURS
    max_value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    valid_from = Column(DateTime(timezone=True), default=utc_now)
    valid_to = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# 11. Prediction Models & Prediction Runs
class PredictionModelEntity(Base):
    __tablename__ = "prediction_models"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False) # e.g. "Yield-XGB-Wheat-v1"
    model_type = Column(String(100), nullable=False) # YIELD, WATER_DEMAND, CLIMATE_RISK
    version = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class PredictionEntity(Base):
    __tablename__ = "predictions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String(36), ForeignKey("prediction_models.id"), nullable=True)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=False, index=True)
    prediction_type = Column(String(100), nullable=False) # YIELD, WATER_DEMAND, CLIMATE_RISK
    predicted_value = Column(Float, nullable=False)
    confidence_min = Column(Float, nullable=True)
    confidence_max = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    target_horizon_date = Column(DateTime(timezone=True), nullable=True)
    data_category = Column(String(50), default=DataCategory.MODEL_OUTPUT.value)
    validation_status = Column(String(50), default=ValidationStatus.VALIDATED.value)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# 12. Optimization Runs
class OptimizationRunModel(Base):
    __tablename__ = "optimization_runs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    domain = Column(String(100), nullable=False) # WATER_ALLOCATION, HARVEST_SCHEDULE, STORAGE_DISPATCH
    solver = Column(String(100), default="OR-Tools") # OR-Tools, Pyomo
    objective_value = Column(Float, nullable=True)
    status = Column(String(50), default="SUCCESS") # SUCCESS, INFEASIBLE, UNBOUNDED
    parameters_json = Column(JSON, nullable=True)
    schedule_result_json = Column(JSON, nullable=True)
    data_category = Column(String(50), default=DataCategory.OPTIMIZATION_OUTPUT.value)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# 13. Recommendations (Explainable 4-Part Structure)
class RecommendationModel(Base):
    __tablename__ = "recommendations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    
    # 4 Core Questions:
    # 1. What happened? (Observation)
    what_happened = Column(Text, nullable=False)
    # 2. Why does it matter? (Impact)
    why_it_matters = Column(Text, nullable=False)
    # 3. Which field is affected? (Field context)
    affected_field_summary = Column(Text, nullable=False)
    # 4. What action should be considered? (Suggested action)
    suggested_action = Column(Text, nullable=False)
    
    urgency = Column(String(50), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    evidence_provenance = Column(JSON, nullable=True) # References to exact validated sensor/weather records
    human_status = Column(String(50), default="PENDING_REVIEW") # PENDING_REVIEW, APPROVED, REJECTED, EXECUTED
    created_at = Column(DateTime(timezone=True), default=utc_now)

# 14. Actions & Outcomes
class ActionModel(Base):
    __tablename__ = "actions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recommendation_id = Column(String(36), ForeignKey("recommendations.id"), nullable=True)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=True)
    action_type = Column(String(100), nullable=False) # IRRIGATION_DISPATCH, SPRAY_FERTILIZER, HARVEST
    initiated_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    details = Column(JSON, nullable=True)
    executed_at = Column(DateTime(timezone=True), default=utc_now)

class OutcomeModel(Base):
    __tablename__ = "outcomes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action_id = Column(String(36), ForeignKey("actions.id"), nullable=True)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=False)
    metric_name = Column(String(100), nullable=False) # e.g. YIELD_KG_HA, WATER_SAVED_LITERS
    predicted_metric_value = Column(Float, nullable=True)
    actual_metric_value = Column(Float, nullable=False)
    variance_percentage = Column(Float, nullable=True)
    observed_at = Column(DateTime(timezone=True), default=utc_now)
    data_category = Column(String(50), default=DataCategory.OBSERVED_OUTCOME.value)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# 15. Storage Facilities & Storage Observations
class StorageFacilityModel(Base):
    __tablename__ = "storage_facilities"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False) # Cold Room A, Silo 1, Warehouse Hub
    facility_type = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    total_capacity_metric_tons = Column(Float, nullable=False)
    current_occupancy_metric_tons = Column(Float, default=0.0)
    target_temperature_c = Column(Float, nullable=True)
    target_relative_humidity = Column(Float, nullable=True)
    compatible_crops = Column(JSON, default=list) # e.g. ["Wheat", "Potato", "Onion"]
    created_at = Column(DateTime(timezone=True), default=utc_now)

class StorageObservationModel(Base):
    __tablename__ = "storage_observations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    storage_facility_id = Column(String(36), ForeignKey("storage_facilities.id"), nullable=False, index=True)
    observed_at = Column(DateTime(timezone=True), default=utc_now)
    temperature_c = Column(Float, nullable=True)
    relative_humidity_percent = Column(Float, nullable=True)
    co2_ppm = Column(Float, nullable=True)
    door_opened_events = Column(Integer, default=0)
    current_loss_rate_percent = Column(Float, nullable=True)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# 16. Data Quality Events & Audit Trail
class DataQualityEventModel(Base):
    __tablename__ = "data_quality_events"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_entity_id = Column(String(100), nullable=True)
    entity_type = Column(String(100), nullable=False) # SENSOR, WEATHER, SATELLITE
    issue_type = Column(String(100), nullable=False) # OUT_OF_RANGE, STALE, MISSING_VALUE, CALIBRATION_DRIFT, CLOUD_OCCLUDED
    severity = Column(String(50), default="WARNING") # INFO, WARNING, ERROR, CRITICAL
    description = Column(Text, nullable=False)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class AuditEventModel(Base):
    __tablename__ = "audit_events"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    action = Column(String(255), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=False)
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    source = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
