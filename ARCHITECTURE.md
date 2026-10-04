# AgriCommand — Production Architecture & Implementation Blueprint

## 1. System Overview

**AgriCommand** is an Integrated Agricultural Intelligence and Decision-Support Platform built around the central architectural principle: **«Data changes decisions.»**

AgriCommand rejects fabricated metrics, pseudo-models, and hardcoded dashboard figures. Unconnected subsystems and empty states explicitly report their true readiness statuses (`NOT_CONFIGURED`, `NO_DATA`, `INSUFFICIENT_DATA`), while all observations flow through strict validation pipelines with hardware safety interlocks.

```
                              ┌────────────────────────────────────────┐
                              │            Farm Digital Twin           │
                              │       (Central Aggregate Model)        │
                              └──────────────────┬─────────────────────┘
                                                 │
      ┌────────────────────┬─────────────────────┼─────────────────────┬───────────────────┐
      │                    │                     │                     │                   │
┌─────▼──────┐      ┌──────▼──────┐       ┌──────▼──────┐       ┌──────▼─────┐      ┌──────▼──────┐
│   Spatial  │      │  Telemetry  │       │  Atmosphere │       │ Analytical │      │ Operations  │
│  Entities  │      │  Pipeline   │       │  Providers  │       │  Engines   │      │  & Outcomes │
├────────────┤      ├─────────────┤       ├─────────────┤       ├────────────┤      ├─────────────┤
│ • Farms    │      │ • ESP32 GW  │       │ • NASA POWER│       │ • FAO-56   │      │ • Storage   │
│ • Fields   │      │ • Probes    │       │ • IMD Grid  │       │ • Simplex  │      │ • Actions   │
│ • Crops    │      │ • Validator │       │ • Sentinel-2│       │ • ML Model │      │ • Outcomes  │
│ • Soil     │      │ • Interlock │       │ • SoilGrids │       │ • Advisory │      │ • Audit     │
└────────────┘      └─────────────┘       └─────────────┘       └────────────┘      └─────────────┘
```

---

## 2. Nine-Stage Decision Loop

| Stage | Name | Architecture & State Transition | Zero-Fake-Data Status Policy |
| :--- | :--- | :--- | :--- |
| **Step 1** | **Farm Registration** | PostGIS/GeoJSON polygon geometries, area in hectares, location, owner identity. | If empty: `No farm registered`. |
| **Step 2** | **Field Mapping** | Polygon boundaries, crop profiles, duration, FAO-56 Kc coefficients ($K_{c,init}$, $K_{c,mid}$, $K_{c,end}$). | If unmapped: `No fields configured`. |
| **Step 3** | **Data Collection** | Dedicated ESP32 gateway ingestion boundary over HTTP/MQTT with hardware UID, battery health, and probe channels. | If disconnected: `No sensor telemetry available`. |
| **Step 4** | **Data Validation** | 6-stage validator: Identity -> Timestamp -> Calibration -> Operational Bounds -> Spike/Moving Average -> Safety Interlock. | Invalid values are flagged `REJECTED` and logged to Data Quality events. |
| **Step 5** | **Prediction** | Abstraction boundary for future scikit-learn, XGBoost, and Crop Growth Simulation models. | Returns explicit `MODEL_NOT_CONFIGURED`. |
| **Step 6** | **Optimization** | Solver interface compatible with Google OR-Tools and Pyomo for priority-weighted resource/water allocation. | Returns `INSUFFICIENT_DATA` if constraints or fields are missing. |
| **Step 7** | **Recommendation** | Explainable 4-question advisories: *1. What happened? 2. Why does it matter? 3. Which field is affected? 4. What action should be considered?* | Returns `INSUFFICIENT_DATA` if no validated thresholds are breached. |
| **Step 8** | **Action & Interlock** | Hardware Safety Rule: low-cost sensors can drift. Automated actuators are held behind mandatory human confirmation. | Status: `AWAITING_HUMAN_CONFIRMATION`. |
| **Step 9** | **Outcome & Learning** | Ground truth yield & soil response recording, calculating prediction variance for closed-loop model evaluation. | Status: `NOT_STARTED` until harvest outcome logged. |

---

## 3. Strict Data Separation & Provenance

Every observation record preserves traceable metadata:
- **`data_category`**: `LIVE_SENSOR_TELEMETRY`, `REGIONAL_WEATHER_DATA`, `SATELLITE_OBSERVATION`, `SOIL_DATA`, `MODEL_OUTPUT`, `OPTIMIZATION_OUTPUT`, `OBSERVED_OUTCOME`.
- **`validation_status`**: `VALIDATED`, `PENDING`, `REJECTED`, `STALE`, `CALIBRATION_DRIFT`.
- **`provenance`**: Audit string recording pipeline timestamp, raw inputs, calibration formulas, and physical bounds.

---

## 4. Hardware Safety Rule Implementation

```
Sensor Reading (Raw)
       │
       ▼
Identity Check (Known provisioned device & probe)
       │
       ▼
Timestamp Check (Reject future timestamps or stale > 7 days)
       │
       ▼
Calibration Application: Calibrated = (Raw * Slope) + Offset
       │
       ▼
Operational Range Bounds Check (Physical min/max verification)
       │
       ▼
Spike / Outlier Check (Moving average deviation analysis)
       │
       ▼
Safety Interlock Authorization Check
       │
       ├── Passed: VALIDATED observation -> Advisory generation
       └── Failed: REJECTED -> Logged to DataQualityEvents -> Actuation Locked
```

---

## 5. Technology Stack Summary

- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic v2, Python 3.13.
- **Database**: PostgreSQL / PostGIS compatible relational schema with SQLite fallback (`agricommand.db`).
- **Frontend**: React 18, TypeScript, Tailwind CSS design system, Leaflet GIS mapping, Lucide icons.
- **Analytics & Math**: FAO-56 Penman-Monteith physical ET0 calculation, Simplex linear water distribution, Copernicus Sentinel-2 13-band NDVI formulation.
