# AgriCommand

## Integrated Agricultural Intelligence & Decision-Support Platform

AgriCommand is an agricultural intelligence and decision-support platform designed to connect farm resources, field information, crop profiles, IoT telemetry, weather and climate data, satellite observations, soil information, resource optimization, storage operations, recommendations, and real-world outcomes through a unified Farm Digital Twin.

The core principle of AgriCommand is:
> **Data changes decisions.**

AgriCommand is not primarily a chatbot and does not depend on artificial dashboard values to demonstrate functionality. The system is designed around real data sources, validated observations, explainable decision workflows, and future integration of real agricultural models.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Core Concept](#core-concept)
- [Farm Digital Twin](#farm-digital-twin)
- [Nine-Step Decision Loop](#nine-step-decision-loop)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Major Components](#major-components)
- [Data Sources](#data-sources)
- [IoT and Hardware](#iot-and-hardware)
- [Data Validation](#data-validation)
- [Hardware Safety](#hardware-safety)
- [Prediction and Model Architecture](#prediction-and-model-architecture)
- [Optimization](#optimization)
- [Recommendation System](#recommendation-system)
- [Storage Network Evaluator](#storage-network-evaluator)
- [Outcome Observer](#outcome-observer)
- [Immutable Audit Trail](#immutable-audit-trail)
- [Security](#security)
- [Project Structure](#project-structure)
- [Current Implementation Status](#current-implementation-status)
- [Test and Verification](#test-and-verification)
- [Important Data Integrity Rules](#important-data-integrity-rules)
- [Application States](#application-states)
- [Local Development](#local-development)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Architecture Documentation](#architecture-documentation)
- [Future Integrations](#future-integrations)
- [Development Principles](#development-principles)
- [Project Status](#project-status)
- [License](#license)

---

## Project Overview

AgriCommand is designed as an integrated agricultural operations and intelligence platform.

Instead of treating farm management, sensor telemetry, weather, crop health, water management, yield prediction, and storage as isolated systems, AgriCommand connects them through a common agricultural data model.

The platform is designed to support the complete lifecycle:

\\text{Farm Registration} \\rightarrow \\text{Field Mapping} \\rightarrow \\text{Crop Profile} \\rightarrow \\text{Data Collection} \\rightarrow \\text{Data Validation} \\rightarrow \\text{Prediction} \\rightarrow \\text{Optimization} \\rightarrow \\text{Recommendation} \\rightarrow \\text{Action} \\rightarrow \\text{Outcome Observation} \\rightarrow \\text{Model Evaluation} \\rightarrow \\text{Digital Twin Update}

The system is designed so that future real-world data sources and agricultural models can be integrated without rebuilding the core application.

---

## Core Concept

The central idea behind AgriCommand is the **Farm Digital Twin**.

The Digital Twin represents the current known state of a farm using connected entities and observations. It connects:

- Farms
- Fields
- Field boundaries
- Crops
- Crop cycles
- Soil information
- Sensor devices
- Sensor observations
- Weather observations
- Satellite observations
- Water resources
- Resource constraints
- Predictions
- Optimization results
- Recommendations
- Actions
- Outcomes
- Storage facilities
- Audit records

The Digital Twin is not intended to manufacture missing information. If a real data source is unavailable, the system explicitly represents that state.

---

## Farm Digital Twin

The Farm Digital Twin follows this conceptual structure:

`
                            FARM
                             │
            ┌────────────────┴────────────────┐
            │                                 │
          FIELDS                          RESOURCES
            │                                 │
          CROPS                        WATER / ENERGY
      ┌─────┼─────────┐                       │
      │     │         │                       │
    SOIL SENSORS SATELLITE                    │
      │     │         │                       │
      └─────┼─────────┘                       │
            │                                 │
        VALIDATION                            │
            │                                 │
      ┌─────┴──────┐                          │
      │            │                          │
  PREDICTION  OPTIMIZATION ◄──────────────────┘
      │            │
      └─────┬──────┘
            │
      RECOMMENDATION
            │
          ACTION
            │
         OUTCOME
            │
     MODEL EVALUATION
            │
   DIGITAL TWIN UPDATE
`

The Digital Twin should always represent the actual state of available information.

---

## Nine-Step Decision Loop

AgriCommand follows a nine-step decision workflow:

1. **Farm Registration**: Create and manage the farm entity, ownership information, location, area, and spatial information.
2. **Field Mapping & Crop Profile**: Fields can be represented using spatial polygons. Each field can be associated with:
   - Crop
   - Variety
   - Planting date
   - Crop stage
   - Soil information
   - Field metadata
3. **Data Collection**: AgriCommand is designed to receive data from multiple sources, including:
   - ESP32 gateways
   - Soil sensors
   - Temperature and humidity sensors
   - Soil temperature sensors
   - Water flow or level sensors
   - Weather providers
   - Satellite observations
   - Soil datasets
4. **Data Validation**: Incoming observations must be validated before they are used by downstream decision systems. Validation includes:
   - Identity validation
   - Timestamp validation
   - Range validation
   - Calibration checks
   - Moving-average checks
   - Outlier detection
   - Duplicate detection
   - Stale-data detection
   - Quality flags
   *Invalid data must not silently become valid data.*
5. **Prediction**: The architecture provides integration points for future agricultural models:
   - Water demand
   - Climate-risk exposure
   - Crop-health trends
   - Yield estimation
   *Models must use real, traceable inputs.*
6. **Optimization**: AgriCommand provides an architecture for constrained resource optimization:
   - Water allocation
   - Energy allocation
   - Labor allocation
   - Multi-field planning
   - Transport planning
   - Storage selection
   *Supported technologies include OR-Tools, Pyomo, and PuLP.*
7. **Recommendation**: Recommendations are intended to be explainable. Every recommendation answers:
   - **What happened?**
   - **Why does it matter?**
   - **Which field is affected?**
   - **What action should be considered?**
   *Recommendations must be based on validated evidence.*
8. **Outcome Observation**: AgriCommand records real-world outcomes so that predictions and decisions can eventually be evaluated against what actually happened:
   - Actual yield
   - Soil response
   - Field outcome
   - Action outcome
   - Prediction variance
9. **Learning & Evaluation**: Outcome information is used to evaluate and improve agricultural models:
   \\text{Prediction} \\rightarrow \\text{Real-world outcome} \\rightarrow \\text{Variance calculation} \\rightarrow \\text{Model evaluation} \\rightarrow \\text{Model improvement}

---

## System Architecture

The high-level architecture is:

`
                            AgriCommand
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
              Frontend                        Backend
        React + TypeScript                    FastAPI
                 │                               │
                 │                ┌──────────┼──────────┐
                 │                │          │          │
                 │               APIs    Services   Validation
                 │                │          │          │
                 │                └──────────┼──────────┘
                 │                               │
                 │                           PostgreSQL
                 │                            PostGIS
                 │                               │
                 └──────────── API ──────────────┘
                                 │
                      External Data / Hardware
                                 │
                   ├── ESP32 / IoT
                   ├── Weather Providers
                   ├── Sentinel-2
                   └── Soil Data Providers
`

---

## Technology Stack

### Frontend
- React
- TypeScript
- Tailwind CSS
- Leaflet or MapLibre
- API client layer

### Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy

### Database
- PostgreSQL
- PostGIS

### Analytics and Optimization
The architecture is prepared for:
- scikit-learn
- XGBoost
- OR-Tools
- Pyomo
- PuLP

*These technologies should only be used when there is an actual implementation requirement.*

---

## Major Components

### Farm Management
Responsible for:
- Farm registration
- Farm metadata
- Farm location
- Farm geometry

### Field Management
Responsible for:
- Field creation
- Field boundaries
- GeoJSON geometry
- Crop association
- Crop cycles

### Sensor Management
Responsible for:
- Device registration
- Sensor provisioning
- Sensor identity
- Sensor status
- Telemetry ingestion

---

## Data Sources

### Telemetry Pipeline
The telemetry architecture follows:
\\text{Sensor} \\rightarrow \\text{Gateway} \\rightarrow \\text{Ingestion API} \\rightarrow \\text{Validation} \\rightarrow \\text{Quality Assessment} \\rightarrow \\text{Database} \\rightarrow \\text{Digital Twin}

### Weather Integration
The system is designed to integrate external weather and climate sources:
- NASA POWER
- IMD

*The application must verify actual provider connectivity before showing provider data as available.*

### Satellite Integration
The architecture supports Copernicus Sentinel-2 integration:
\\text{Sentinel-2} \\rightarrow \\text{Image Acquisition} \\rightarrow \\text{Cloud Filtering} \\rightarrow \\text{Field Clipping} \\rightarrow \\text{Spectral Processing} \\rightarrow \\text{NDVI} \\rightarrow \\text{Crop Health Analysis}

### Soil Integration
The architecture supports soil information from:
- Local soil observations
- Regional soil datasets (ISRIC SoilGrids)

*Regional estimates must remain distinguishable from actual local soil measurements.*

---

## IoT and Hardware

AgriCommand connects physical hardware via low-latency ingestion gateways:
- ESP32 microcontrollers
- Capacitive soil moisture probes
- SHT31 ambient temperature and relative humidity sensors
- DS18B20 digital soil temperature sensors
- Water flow and water level meters
- Storage environment sensors (NDIR CO2, HX711 load cells)

---

## Data Validation

Data quality is a core part of AgriCommand. A sensor observation should contain enough metadata to determine:
- Where it came from
- Which device produced it
- When it was produced
- What was measured
- Which unit was used
- Whether calibration was applied
- Whether the value passed validation
- Whether the observation is stale

Example validation flow:
\\text{Raw Observation} \\rightarrow \\text{Identity Check} \\rightarrow \\text{Timestamp Check} \\rightarrow \\text{Calibration Check} \\rightarrow \\text{Range Check} \\rightarrow \\text{Quality Assessment} \\rightarrow \\text{Validated Observation}

---

## Hardware Safety

Low-cost agricultural sensors can drift or produce erroneous measurements. Therefore:
> **An unvalidated sensor observation must never directly trigger a high-impact automated action.**

For example, an invalid soil-moisture reading must not independently activate irrigation equipment.

The intended architecture is:
\\text{Sensor} \\rightarrow \\text{Validation} \\rightarrow \\text{Quality Check} \\rightarrow \\text{Safety / Authorization} \\rightarrow \\text{Decision} \\rightarrow \\text{Action}

---

## Prediction and Model Architecture

AgriCommand intentionally separates the application from future agricultural models:
\\text{Prediction Service} \\rightarrow \\text{Prediction Provider} \\rightarrow \\text{Real Agricultural Model}

Potential future models include:
- Yield prediction
- Crop-health prediction
- Climate-risk prediction
- Water-demand prediction

A model interface existing does not mean a model is connected. Until a real model is configured, the application reports:
MODEL_NOT_CONFIGURED

The system must not generate fake prediction values.

---

## Optimization

The optimization architecture is designed for real agricultural constraints:
- Available water
- Field requirements
- Crop requirements
- Energy constraints
- Labor constraints
- Transport constraints
- Storage constraints

Potential optimization engines include OR-Tools, Pyomo, and PuLP. Optimization results must only be produced from validated inputs.

---

## Recommendation System

Recommendations follow a four-question explainable structure:
1. **What happened?**
2. **Why does it matter?**
3. **Which field is affected?**
4. **What action should be considered?**

If there is insufficient validated evidence, the system reports:
INSUFFICIENT_DATA
rather than inventing a recommendation.

---

## Storage Network Evaluator

The storage architecture is designed to evaluate facilities using:
- Capacity
- Temperature
- Humidity
- CO2 levels
- Crop compatibility
- Distance
- Expected loss
- Availability

Storage information must come from configured facilities or real storage observations.

---

## Outcome Observer

The Outcome Observer records real-world outcomes:
\\text{Prediction} \\rightarrow \\text{Agricultural Action} \\rightarrow \\text{Real-world Outcome} \\rightarrow \\text{Outcome Recording} \\rightarrow \\text{Prediction Variance} \\rightarrow \\text{Model Evaluation}

The outcome system is not intended to manufacture results.

---

## Immutable Audit Trail

AgriCommand maintains an audit architecture for important state transformations:
- Timestamp
- Actor
- Entity ID
- Entity type
- Event / Action
- Source provenance
- Previous state where applicable
- New state where applicable
- Model version where applicable

The audit trail is intended to provide traceability across the decision lifecycle.

---

## Security

AgriCommand supports role-based access control (RBAC). Planned roles include:
- Farmer
- Agriculture Officer
- Storage Operator
- Administrator

Security responsibilities include authentication, authorization, role-based access, secure configuration, API protection, audit logging, and data validation. Secrets must never be hardcoded into the repository.

---

## Project Structure

The repository is organized around separate application responsibilities:

`
AgriCommand/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── integrations/
│   │   │   ├── weather/
│   │   │   ├── satellite/
│   │   │   └── soil/
│   │   ├── analytics/
│   │   │   ├── fao56.py
│   │   │   ├── optimization.py
│   │   │   └── recommendations.py
│   │   └── validation/
│   │       └── sensor_validator.py
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   │   ├── FarmMap.tsx
│   │   │   ├── DecisionLoopTracker.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   └── ExplainableRecommendationCard.tsx
│   │   ├── App.tsx
│   │   └── index.css
│   └── index.html
│
├── ARCHITECTURE.md
├── README.md
└── .env.example
`

The actual repository structure should be treated as authoritative if it differs from this conceptual structure.

---

## Current Implementation Status

The current implementation includes architecture and workflows for:
- Farm registration
- Field mapping
- Hardware/device provisioning
- Telemetry ingestion
- Telemetry validation
- Hardware safety validation
- Explainable recommendations
- Farm Digital Twin synchronization
- Outcome observation
- Audit trail
- End-to-end verification

The current verification environment includes controlled test scenarios.

---

## Test and Verification

The repository contains end-to-end verification for the main agricultural workflow:
- Farm Registration
- Field Mapping
- Hardware Provisioning
- Telemetry Validation
- Invalid Sensor Reading Rejection
- Recommendation Workflow
- Farm Digital Twin Synchronization
- Audit Trail

The E2E test suite is intended to verify the software architecture and workflow behavior. Passing automated tests does not mean that physical hardware, external providers, or agricultural ML models are automatically connected.

---

## Important Data Integrity Rules

AgriCommand follows these rules:

1. **No fake production data**: The production application must not use fabricated sensor readings, weather values, rainfall, soil measurements, NDVI, crop-health scores, yield predictions, climate-risk scores, storage measurements, optimization results, or model confidence values.
2. **Test data is different from production data**: Controlled test fixtures may be used inside automated tests. Test data must not be presented as live agricultural observations.
3. **Provisioned does not mean connected**: $\\text{PROVISIONED} \\neq \\text{CONNECTED}$. A device becomes connected only after actual communication is verified.
4. **Model interface does not mean model connected**: $\\text{MODEL\\_INTERFACE\\_EXISTS} \\neq \\text{MODEL\\_CONNECTED}$. Until a real model is integrated, MODEL_NOT_CONFIGURED should be reported.
5. **API exists does not mean provider is connected**: $\\text{API\\_EXISTS} \\neq \\text{EXTERNAL\\_PROVIDER\\_CONNECTED}$. External data providers must be verified through actual communication.

---

## Application States

AgriCommand uses explicit system states where applicable:
- NOT_CONFIGURED
- NO_DATA
- PROVISIONED
- CONNECTED
- DISCONNECTED
- PROCESSING
- AVAILABLE
- STALE
- INVALID
- INSUFFICIENT_DATA
- FAILED

This prevents the frontend from pretending that unavailable data exists.

---

## Local Development

### Prerequisites
- Python 3.10+
- Node.js & npm
- PostgreSQL & PostGIS (or SQLite for development)

### Backend Setup
From the backend directory:
`ash
cd backend
python -m venv .venv
# Activate on Windows:
.venv\\Scripts\\Activate.ps1
# Activate on Unix/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python run_server.py
`

### Frontend Setup
From the frontend directory:
`ash
cd frontend
npm install
npm run dev
`

---

## Configuration

Create the local environment configuration from .env.example:
- DATABASE_URL
- SECRET_KEY
- JWT_CONFIGURATION
- MQTT_CONFIGURATION
- WEATHER_PROVIDER_CONFIGURATION
- SATELLITE_PROVIDER_CONFIGURATION
- SOIL_PROVIDER_CONFIGURATION
- MODEL_PROVIDER_CONFIGURATION

*Never commit real credentials. Never place API keys directly in source code.*

---

## API Documentation

When the FastAPI backend is running, interactive API documentation is available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Architecture Documentation

The detailed system architecture is documented separately in:
[ARCHITECTURE.md](ARCHITECTURE.md)

The README provides the project-level overview while ARCHITECTURE.md contains deeper implementation and architectural details.

---

## Future Integrations

AgriCommand is intentionally designed for future integration with real systems:
- **Hardware**: Physical ESP32 gateways, capacitive soil probes, SHT31, DS18B20, flow meters, water level sensors, load cells.
- **Weather**: NASA POWER, IMD gridded datasets.
- **Satellite**: Copernicus Sentinel-2 (13 bands, cloud filtering, NDVI).
- **Soil**: ISRIC SoilGrids, certified local laboratory core tests.
- **Models**: Yield prediction, crop-health analysis, climate-risk analysis, water-demand calculation, agricultural optimization.

These integrations should be added through the existing provider and service boundaries rather than bypassing the application architecture.

---

## Development Principles

1. **Real data over fabricated data**: The system must prefer an honest empty state over a fake number.
2. **Validation before decision**: Unvalidated observations must not directly drive high-impact decisions.
3. **Explainability**: Recommendations should be traceable to observations and evidence.
4. **Provenance**: Important data and model outputs should have identifiable sources.
5. **Separation of concerns**: Frontend, backend, database, ingestion, analytics, and external integrations should remain clearly separated.
6. **Extensibility**: Future data providers and models should be pluggable.
7. **Test isolation**: Test fixtures must not become production data.
8. **Auditability**: Important state transformations must be traceable.
9. **Honest system states**: The application must distinguish between Implemented, Configured, Connected, Available, Not Configured, No Data, and Failed.

---

## Project Status

AgriCommand is under active development. The current stage focuses on establishing the complete software architecture, data contracts, validation mechanisms, Digital Twin, operational workflows, and integration boundaries.

Real-world external data sources, physical IoT devices, and agricultural prediction models can be connected incrementally without changing the fundamental application architecture.

---

## License

[MIT License](LICENSE)
