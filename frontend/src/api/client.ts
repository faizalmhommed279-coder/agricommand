export const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface StandardResponse<T> {
  status: 'AVAILABLE' | 'NOT_CONFIGURED' | 'NO_DATA' | 'PROCESSING' | 'STALE' | 'INVALID' | 'FAILED' | 'INSUFFICIENT_DATA';
  data: T | null;
  message: string;
  provenance?: Record<string, any>;
  timestamp: string;
}

export const api = {
  // Digital Twin
  getDigitalTwin: async (farmId?: string) => {
    const url = farmId ? `${API_BASE_URL}/digital-twin?farm_id=${farmId}` : `${API_BASE_URL}/digital-twin`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any>>;
  },

  // Farms
  getFarms: async () => {
    const res = await fetch(`${API_BASE_URL}/farms`);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  createFarm: async (farm: { name: string; location_name?: string; total_area_hectares?: number; latitude?: number; longitude?: number }) => {
    const res = await fetch(`${API_BASE_URL}/farms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(farm)
    });
    return res.json() as Promise<StandardResponse<any>>;
  },

  // Fields
  getFields: async (farmId?: string) => {
    const url = farmId ? `${API_BASE_URL}/fields?farm_id=${farmId}` : `${API_BASE_URL}/fields`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  createField: async (field: { farm_id: string; name: string; area_hectares?: number; soil_type?: string; polygon_geojson?: any }) => {
    const res = await fetch(`${API_BASE_URL}/fields`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(field)
    });
    return res.json() as Promise<StandardResponse<any>>;
  },

  // Sensors & ESP32 Telemetry
  getDevices: async (farmId?: string) => {
    const url = farmId ? `${API_BASE_URL}/sensors/devices?farm_id=${farmId}` : `${API_BASE_URL}/sensors/devices`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  getSensors: async (fieldId?: string) => {
    const url = fieldId ? `${API_BASE_URL}/sensors?field_id=${fieldId}` : `${API_BASE_URL}/sensors`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  getTelemetry: async (sensorId?: string, fieldId?: string) => {
    let url = `${API_BASE_URL}/telemetry?limit=50`;
    if (sensorId) url += `&sensor_id=${sensorId}`;
    if (fieldId) url += `&field_id=${fieldId}`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  ingestTelemetry: async (payload: { device_uid: string; sensor_uid: string; timestamp: string; raw_value: number; unit: string }) => {
    const res = await fetch(`${API_BASE_URL}/telemetry/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return res.json() as Promise<StandardResponse<any>>;
  },

  // Weather & Providers
  getWeather: async (farmId?: string) => {
    const url = farmId ? `${API_BASE_URL}/weather?farm_id=${farmId}` : `${API_BASE_URL}/weather`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  getWeatherProviderStatus: async () => {
    const res = await fetch(`${API_BASE_URL}/weather/provider-status`);
    return res.json();
  },

  // Satellite & Sentinel-2
  getSatellite: async (fieldId?: string) => {
    const url = fieldId ? `${API_BASE_URL}/satellite?field_id=${fieldId}` : `${API_BASE_URL}/satellite`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  getSatellitePipelineStatus: async () => {
    const res = await fetch(`${API_BASE_URL}/satellite/pipeline-status`);
    return res.json();
  },

  // Soil
  getSoilProfiles: async (fieldId?: string) => {
    const url = fieldId ? `${API_BASE_URL}/soil/profiles?field_id=${fieldId}` : `${API_BASE_URL}/soil/profiles`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },

  // Water & FAO-56
  getWaterResources: async (farmId?: string) => {
    const url = farmId ? `${API_BASE_URL}/water/resources?farm_id=${farmId}` : `${API_BASE_URL}/water/resources`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  calculateFAO56: async (payload: { field_id: string; crop_cycle_id: string }) => {
    const res = await fetch(`${API_BASE_URL}/water/fao56-calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return res.json();
  },

  // Predictions
  getPredictions: async (fieldId?: string) => {
    const url = fieldId ? `${API_BASE_URL}/predictions?field_id=${fieldId}` : `${API_BASE_URL}/predictions`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  getPredictionModels: async () => {
    const res = await fetch(`${API_BASE_URL}/predictions/models`);
    return res.json();
  },

  // Optimization
  getOptimizationRuns: async (farmId?: string) => {
    const url = farmId ? `${API_BASE_URL}/optimization/runs?farm_id=${farmId}` : `${API_BASE_URL}/optimization/runs`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  solveWaterAllocation: async (payload: { farm_id: string; available_water_liters: number }) => {
    const res = await fetch(`${API_BASE_URL}/optimization/solve-water-allocation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return res.json();
  },

  // Recommendations
  getRecommendations: async (farmId?: string, fieldId?: string) => {
    let url = `${API_BASE_URL}/recommendations`;
    if (farmId) url += `?farm_id=${farmId}`;
    if (fieldId) url += `${farmId ? '&' : '?'}field_id=${fieldId}`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  evaluateFieldAdvisories: async (fieldId: string) => {
    const res = await fetch(`${API_BASE_URL}/recommendations/evaluate-field/${fieldId}`, {
      method: 'POST'
    });
    return res.json();
  },

  // Harvest & Storage
  getHarvestEstimates: async (fieldId?: string) => {
    const url = fieldId ? `${API_BASE_URL}/harvest/estimates?field_id=${fieldId}` : `${API_BASE_URL}/harvest/estimates`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  getStorageFacilities: async (farmId?: string) => {
    const url = farmId ? `${API_BASE_URL}/storage?farm_id=${farmId}` : `${API_BASE_URL}/storage`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },

  // Outcomes
  getOutcomes: async (fieldId?: string) => {
    const url = fieldId ? `${API_BASE_URL}/outcomes?field_id=${fieldId}` : `${API_BASE_URL}/outcomes`;
    const res = await fetch(url);
    return res.json() as Promise<StandardResponse<any[]>>;
  },

  // Data Quality & Audit
  getDataQualitySummary: async () => {
    const res = await fetch(`${API_BASE_URL}/data-quality/summary`);
    return res.json() as Promise<StandardResponse<any>>;
  },
  getDataQualityEvents: async () => {
    const res = await fetch(`${API_BASE_URL}/data-quality/events`);
    return res.json() as Promise<StandardResponse<any[]>>;
  },
  getAuditTrail: async () => {
    const res = await fetch(`${API_BASE_URL}/audit`);
    return res.json() as Promise<StandardResponse<any[]>>;
  }
};
