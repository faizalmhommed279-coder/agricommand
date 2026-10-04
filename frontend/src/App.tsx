import React, { useState, useEffect } from 'react';
import { 
  Building2, Map, Sprout, Cpu, CloudSun, Satellite, 
  Layers, Droplets, Sparkles, Sliders, MessageSquareQuote, 
  Calendar, Warehouse, Award, ShieldCheck, FileText,
  Plus, RefreshCw, AlertCircle, Activity, Terminal
} from 'lucide-react';
import { api } from './api/client';
import { StatusBadge } from './components/StatusBadge';
import { EmptyState } from './components/EmptyState';
import { FarmMap } from './components/FarmMap';
import { DecisionLoopTracker } from './components/DecisionLoopTracker';
import { ExplainableRecommendationCard } from './components/ExplainableRecommendationCard';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [error, setError] = useState<string | null>(null);

  // Core Data States
  const [digitalTwin, setDigitalTwin] = useState<any>(null);
  const [selectedFarm, setSelectedFarm] = useState<any>(null);
  const [fields, setFields] = useState<any[]>([]);
  const [selectedFieldId, setSelectedFieldId] = useState<string | undefined>(undefined);
  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [weatherProviderStatus, setWeatherProviderStatus] = useState<any>(null);
  const [satellitePipelineStatus, setSatellitePipelineStatus] = useState<any>(null);
  const [dataQualitySummary, setDataQualitySummary] = useState<any>(null);
  const [auditTrail, setAuditTrail] = useState<any[]>([]);
  const [storageFacilities, setStorageFacilities] = useState<any[]>([]);

  // Modals
  const [showFarmModal, setShowFarmModal] = useState<boolean>(false);
  const [showFieldModal, setShowFieldModal] = useState<boolean>(false);
  const [showIngestModal, setShowIngestModal] = useState<boolean>(false);

  // Form States
  const [newFarmName, setNewFarmName] = useState('');
  const [newFarmLocation, setNewFarmLocation] = useState('');
  const [newFarmArea, setNewFarmArea] = useState('25.5');
  const [newFarmLat, setNewFarmLat] = useState('18.5204');
  const [newFarmLon, setNewFarmLon] = useState('73.8567');

  const [newFieldName, setNewFieldName] = useState('');
  const [newFieldArea, setNewFieldArea] = useState('8.0');
  const [newFieldSoil, setNewFieldSoil] = useState('Sandy Clay Loam');

  const [testRawVal, setTestRawVal] = useState('18.5');
  const [testSensorType, setTestSensorType] = useState('capacitive_soil_moisture');

  const loadAllData = async () => {
    try {
      setError(null);

      // Load Digital Twin & Farms
      const dtRes = await api.getDigitalTwin();
      if (dtRes && dtRes.data) {
        setDigitalTwin(dtRes.data);
        if (dtRes.data.farm) setSelectedFarm(dtRes.data.farm);
        if (dtRes.data.fields) setFields(dtRes.data.fields);
        if (dtRes.data.latest_telemetry) setTelemetry(dtRes.data.latest_telemetry);
        if (dtRes.data.recommendations) setRecommendations(dtRes.data.recommendations);
      } else {
        setDigitalTwin(null);
      }

      // Load Provider Statuses
      const wp = await api.getWeatherProviderStatus();
      setWeatherProviderStatus(wp);

      const sp = await api.getSatellitePipelineStatus();
      setSatellitePipelineStatus(sp);

      const dq = await api.getDataQualitySummary();
      if (dq && dq.data) setDataQualitySummary(dq.data);

      const at = await api.getAuditTrail();
      if (at && at.data) setAuditTrail(at.data);

      const st = await api.getStorageFacilities();
      if (st && st.data) setStorageFacilities(st.data);

    } catch (err: any) {
      console.error('Data load error:', err);
      setError('Unable to communicate with AgriCommand backend. Verify FastAPI service is running on port 8000.');
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  // Handlers for creating Farm & Field
  const handleCreateFarm = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFarmName.trim()) return;
    try {
      await api.createFarm({
        name: newFarmName,
        location_name: newFarmLocation || 'Precision Agro Corridor',
        total_area_hectares: parseFloat(newFarmArea) || 20.0,
        latitude: parseFloat(newFarmLat) || 18.52,
        longitude: parseFloat(newFarmLon) || 73.85
      });
      setShowFarmModal(false);
      setNewFarmName('');
      loadAllData();
    } catch (err) {
      alert('Error creating farm');
    }
  };

  const handleCreateField = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFieldName.trim() || !selectedFarm) return;
    try {
      const lat = selectedFarm.latitude || 18.52;
      const lon = selectedFarm.longitude || 73.85;
      const d = 0.003;
      // Real GeoJSON Polygon
      const polygon_geojson = {
        type: 'Polygon',
        coordinates: [[
          [lon - d, lat - d],
          [lon + d, lat - d],
          [lon + d, lat + d],
          [lon - d, lat + d],
          [lon - d, lat - d]
        ]]
      };

      await api.createField({
        farm_id: selectedFarm.id,
        name: newFieldName,
        area_hectares: parseFloat(newFieldArea) || 5.0,
        soil_type: newFieldSoil,
        polygon_geojson
      });
      setShowFieldModal(false);
      setNewFieldName('');
      loadAllData();
    } catch (err) {
      alert('Error creating field');
    }
  };

  const handleIngestTelemetry = async () => {
    if (!selectedFarm) {
      alert('Register a farm first');
      return;
    }
    try {
      // Ingest live telemetry with realistic payload
      const res = await api.ingestTelemetry({
        device_uid: 'ESP32-GW-001',
        sensor_uid: 'SOIL-PROBE-01',
        timestamp: new Date().toISOString(),
        raw_value: parseFloat(testRawVal),
        unit: testSensorType === 'capacitive_soil_moisture' ? '%' : '°C'
      });
      setShowIngestModal(false);
      loadAllData();
      alert(`Ingestion Pipeline Result: ${res.status}\n${res.message}`);
    } catch (err: any) {
      alert('Error during telemetry validation: ' + err.message);
    }
  };

  const navItems = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'digital-twin', label: 'Farm Digital Twin', icon: Building2 },
    { id: 'fields', label: 'Field Management', icon: Map },
    { id: 'telemetry', label: 'Sensors & Telemetry', icon: Cpu },
    { id: 'weather', label: 'Weather & Climate', icon: CloudSun },
    { id: 'satellite', label: 'Satellite & NDVI', icon: Satellite },
    { id: 'soil', label: 'Soil Information', icon: Layers },
    { id: 'water', label: 'Water Management', icon: Droplets },
    { id: 'predictions', label: 'Prediction Models', icon: Sparkles },
    { id: 'optimization', label: 'Resource Optimization', icon: Sliders },
    { id: 'recommendations', label: 'Recommendations', icon: MessageSquareQuote },
    { id: 'harvest', label: 'Harvest Tracker', icon: Calendar },
    { id: 'storage', label: 'Storage Network', icon: Warehouse },
    { id: 'outcomes', label: 'Observed Outcomes', icon: Award },
    { id: 'data-quality', label: 'Data Quality Center', icon: ShieldCheck },
    { id: 'audit', label: 'Audit Trail', icon: FileText }
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Sidebar Navigation */}
      <aside style={{
        width: '280px',
        background: 'rgba(15, 23, 42, 0.85)',
        backdropFilter: 'blur(20px)',
        borderRight: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        flexDirection: 'column',
        position: 'sticky',
        top: 0,
        height: '100vh',
        zIndex: 50
      }}>
        {/* Brand Header */}
        <div style={{ padding: '1.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 15px rgba(16, 185, 129, 0.4)'
            }}>
              <Sprout size={20} color="#ffffff" />
            </div>
            <div>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc', lineHeight: 1 }}>
                AgriCommand
              </h1>
              <span style={{ fontSize: '0.65rem', fontWeight: 600, color: '#34d399', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                Intelligence Platform
              </span>
            </div>
          </div>
          <p style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '0.6rem', fontStyle: 'italic' }}>
            «Data changes decisions»
          </p>
        </div>

        {/* Navigation List */}
        <nav style={{ flex: 1, overflowY: 'auto', padding: '1rem 0.75rem' }}>
          <div style={{ fontSize: '0.65rem', fontWeight: 700, color: '#475569', letterSpacing: '0.08em', textTransform: 'uppercase', padding: '0 0.75rem 0.5rem' }}>
            Core Domains
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.65rem 0.85rem',
                  borderRadius: '8px',
                  marginBottom: '2px',
                  background: isActive ? 'rgba(16, 185, 129, 0.15)' : 'transparent',
                  color: isActive ? '#34d399' : '#94a3b8',
                  border: isActive ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid transparent',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '0.84rem',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease'
                }}
              >
                <Icon size={17} style={{ color: isActive ? '#34d399' : '#64748b' }} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Footer Policy Badge */}
        <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)', background: 'rgba(0,0,0,0.2)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', display: 'inline-block' }} />
            <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '0.04em' }}>
              STRICT DATA POLICY
            </span>
          </div>
          <p style={{ fontSize: '0.65rem', color: '#64748b', lineHeight: 1.3 }}>
            Zero synthetic/fake numbers. Unconnected providers report explicit empty states.
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, minHeight: '100vh', display: 'flex', flexDirection: 'column', overflowX: 'hidden' }}>
        {/* Top Navbar */}
        <header style={{
          height: '68px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          background: 'rgba(15, 23, 42, 0.6)',
          backdropFilter: 'blur(16px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 2rem',
          position: 'sticky',
          top: 0,
          zIndex: 40
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }}>
              {navItems.find(i => i.id === activeTab)?.label}
            </h2>
            {selectedFarm && (
              <span className="badge badge-available">
                FARM: {selectedFarm.name}
              </span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button
              onClick={() => setShowFarmModal(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                color: '#f8fafc',
                padding: '0.45rem 0.9rem',
                borderRadius: '8px',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              <Plus size={15} /> Register Farm
            </button>

            {selectedFarm && (
              <button
                onClick={() => setShowFieldModal(true)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  background: 'rgba(16, 185, 129, 0.15)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  color: '#34d399',
                  padding: '0.45rem 0.9rem',
                  borderRadius: '8px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                <Plus size={15} /> Map Field
              </button>
            )}

            <button
              onClick={loadAllData}
              title="Refresh Platform State"
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: '#94a3b8',
                padding: '0.45rem',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              <RefreshCw size={16} />
            </button>
          </div>
        </header>

        {/* Tab Body */}
        <div style={{ padding: '2rem', flex: 1 }}>
          {error && (
            <div style={{
              background: 'rgba(244, 63, 94, 0.12)',
              border: '1px solid rgba(244, 63, 94, 0.3)',
              borderRadius: '10px',
              padding: '1rem',
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              color: '#f43f5e'
            }}>
              <AlertCircle size={20} />
              <span style={{ fontSize: '0.875rem' }}>{error}</span>
            </div>
          )}

          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div>
              {/* Nine-Stage Decision Loop Component */}
              <div style={{ marginBottom: '1.5rem' }}>
                <DecisionLoopTracker loopData={digitalTwin?.decision_loop} />
              </div>

              {/* Map & Farm Overview */}
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
                <div className="glass-panel" style={{ padding: '1.25rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <div>
                      <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
                        Farm Boundary & Spatial GIS Map
                      </h3>
                      <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                        PostGIS-compatible field polygons and sensor telemetry coordinates
                      </p>
                    </div>
                    <StatusBadge status={fields && fields.length > 0 ? 'AVAILABLE' : 'NO_DATA'} />
                  </div>
                  <FarmMap
                    fields={fields}
                    selectedFieldId={selectedFieldId}
                    onSelectField={(id) => setSelectedFieldId(id)}
                    center={selectedFarm?.latitude ? [selectedFarm.latitude, selectedFarm.longitude] : undefined}
                  />
                </div>

                {/* Subsystem Connection Status Panel */}
                <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.25rem' }}>
                      Integration Boundaries
                    </h3>
                    <p style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '1rem' }}>
                      Operational state of external data pipelines
                    </p>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.65rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)' }}>
                        <div>
                          <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#f8fafc' }}>ESP32 Ingestion</div>
                          <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Hardware Telemetry</div>
                        </div>
                        <StatusBadge status={telemetry && telemetry.length > 0 ? 'AVAILABLE' : 'NO_DATA'} />
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.65rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)' }}>
                        <div>
                          <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#f8fafc' }}>NASA POWER API</div>
                          <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Solar & Daily Climatology</div>
                        </div>
                        <StatusBadge status={weatherProviderStatus?.providers?.NASA_POWER?.status || 'NOT_CONFIGURED'} />
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.65rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)' }}>
                        <div>
                          <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#f8fafc' }}>Sentinel-2 Pipeline</div>
                          <div style={{ fontSize: '0.7rem', color: '#64748b' }}>13-Band Multispectral</div>
                        </div>
                        <StatusBadge status={satellitePipelineStatus?.connection_state || 'NOT_CONFIGURED'} />
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.65rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)' }}>
                        <div>
                          <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#f8fafc' }}>Agricultural ML Model</div>
                          <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Yield & Stress Inferences</div>
                        </div>
                        <StatusBadge status="NOT_CONFIGURED" />
                      </div>
                    </div>
                  </div>

                  <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                    <button
                      onClick={() => setShowIngestModal(true)}
                      style={{
                        width: '100%',
                        padding: '0.6rem',
                        background: 'rgba(6, 182, 212, 0.15)',
                        border: '1px solid rgba(6, 182, 212, 0.3)',
                        borderRadius: '8px',
                        color: '#38bdf8',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '0.4rem'
                      }}
                    >
                      <Terminal size={15} /> Test Telemetry Ingestion Pipeline
                    </button>
                  </div>
                </div>
              </div>

              {/* Latest Explainable Recommendations */}
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
                      Explainable Recommendations
                    </h3>
                    <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                      Derived solely from validated observations — answering the 4 core agronomic questions
                    </p>
                  </div>
                </div>

                {recommendations && recommendations.length > 0 ? (
                  recommendations.map(rec => (
                    <ExplainableRecommendationCard key={rec.id} rec={rec} />
                  ))
                ) : (
                  <EmptyState
                    title="Insufficient validated evidence to generate a recommendation"
                    description="AgriCommand does not create fake recommendations. Ingest validated field sensor or weather observations to trigger advisory logic."
                    icon={MessageSquareQuote}
                    status="NO_DATA"
                    actionText="Ingest Sensor Telemetry"
                    onAction={() => setShowIngestModal(true)}
                  />
                )}
              </div>
            </div>
          )}

          {/* TAB 2: FARM DIGITAL TWIN */}
          {activeTab === 'digital-twin' && (
            <div>
              {!digitalTwin || !digitalTwin.farm ? (
                <EmptyState
                  title="No farm registered"
                  description="Register a farm to begin constructing the Farm Digital Twin."
                  icon={Building2}
                  status="NO_DATA"
                  actionText="Register Farm"
                  onAction={() => setShowFarmModal(true)}
                />
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  {/* Digital Twin Header Card */}
                  <div className="glass-panel" style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(6,182,212,0.04) 100%)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                      <div>
                        <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#34d399', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                          Primary Aggregate Model
                        </span>
                        <h3 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc' }}>
                          {digitalTwin.farm.name} Digital Twin
                        </h3>
                      </div>
                      <StatusBadge status="AVAILABLE" />
                    </div>
                    <p style={{ fontSize: '0.85rem', color: '#94a3b8', maxWidth: '680px', marginBottom: '1rem' }}>
                      The Farm Digital Twin acts as the single unified domain model interconnecting boundaries, telemetry, satellite observations, hydrology, and recommendations.
                    </p>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem' }}>
                      <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.65rem 0.85rem', borderRadius: '8px' }}>
                        <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Total Area</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>{digitalTwin.farm.total_area_hectares} ha</div>
                      </div>
                      <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.65rem 0.85rem', borderRadius: '8px' }}>
                        <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Mapped Fields</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>{digitalTwin.fields?.length || 0}</div>
                      </div>
                      <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.65rem 0.85rem', borderRadius: '8px' }}>
                        <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Hardware Devices</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>{digitalTwin.devices?.length || 0}</div>
                      </div>
                      <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.65rem 0.85rem', borderRadius: '8px' }}>
                        <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Water Balance</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>{digitalTwin.water_resources?.length || 0} Source(s)</div>
                      </div>
                    </div>
                  </div>

                  {/* Connected Subsystems Visual Grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                    <div className="glass-panel" style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc' }}>Field Boundaries</h4>
                        <StatusBadge status={digitalTwin.subsystem_states?.fields} />
                      </div>
                      <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                        {digitalTwin.fields?.length ? `${digitalTwin.fields.length} polygon boundary records loaded.` : 'No fields configured.'}
                      </p>
                    </div>

                    <div className="glass-panel" style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc' }}>Sensor Telemetry</h4>
                        <StatusBadge status={digitalTwin.subsystem_states?.sensors} />
                      </div>
                      <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                        {digitalTwin.latest_telemetry?.length ? `${digitalTwin.latest_telemetry.length} validated readings in window.` : 'No sensor telemetry available.'}
                      </p>
                    </div>

                    <div className="glass-panel" style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc' }}>Weather Baseline</h4>
                        <StatusBadge status={digitalTwin.subsystem_states?.weather} />
                      </div>
                      <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                        {digitalTwin.weather_observations?.length ? `${digitalTwin.weather_observations.length} daily meteorological observations.` : 'Weather data source not connected.'}
                      </p>
                    </div>

                    <div className="glass-panel" style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc' }}>Satellite Observation</h4>
                        <StatusBadge status={digitalTwin.subsystem_states?.satellite} />
                      </div>
                      <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                        {digitalTwin.satellite_observations?.length ? `${digitalTwin.satellite_observations.length} Sentinel-2 scenes.` : 'No satellite observations available.'}
                      </p>
                    </div>

                    <div className="glass-panel" style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc' }}>Prediction Engine</h4>
                        <StatusBadge status="NOT_CONFIGURED" />
                      </div>
                      <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                        Prediction model not connected. Interface awaiting future agricultural models.
                      </p>
                    </div>

                    <div className="glass-panel" style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc' }}>Hydrological Balance</h4>
                        <StatusBadge status={digitalTwin.water_resources?.length ? 'AVAILABLE' : 'NO_DATA'} />
                      </div>
                      <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                        FAO-56 Penman-Monteith ET0 engine calibrated and ready for validated inputs.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: FIELDS */}
          {activeTab === 'fields' && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                    Field Management & Crop Assignment
                  </h3>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                    Configure field polygons, assign crop varieties, and track growth stages
                  </p>
                </div>
                {selectedFarm && (
                  <button
                    onClick={() => setShowFieldModal(true)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.4rem',
                      background: 'rgba(16, 185, 129, 0.2)',
                      border: '1px solid rgba(16, 185, 129, 0.4)',
                      color: '#34d399',
                      padding: '0.5rem 1rem',
                      borderRadius: '8px',
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    <Plus size={16} /> Map New Field
                  </button>
                )}
              </div>

              {!fields || fields.length === 0 ? (
                <EmptyState
                  title="No fields mapped yet"
                  description="Define field boundaries and assign crop varieties to begin precision monitoring."
                  icon={Map}
                  status="NO_DATA"
                  actionText={selectedFarm ? "Map Field Boundary" : "Register Farm First"}
                  onAction={() => selectedFarm ? setShowFieldModal(true) : setShowFarmModal(true)}
                />
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
                  {fields.map(f => (
                    <div key={f.id} className="glass-panel" style={{ padding: '1.25rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                        <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>{f.name}</h4>
                        <StatusBadge status="AVAILABLE" />
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '1rem' }}>
                        <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.5rem', borderRadius: '6px' }}>
                          <span style={{ fontSize: '0.7rem', color: '#64748b' }}>Area</span>
                          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc' }}>{f.area_hectares} ha</div>
                        </div>
                        <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.5rem', borderRadius: '6px' }}>
                          <span style={{ fontSize: '0.7rem', color: '#64748b' }}>Soil Class</span>
                          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc' }}>{f.soil_type || 'Unspecified'}</div>
                        </div>
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#94a3b8', fontFamily: 'monospace' }}>
                        Boundary: GeoJSON Polygon ({f.polygon_geojson?.coordinates?.[0]?.length || 0} vertices)
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 4: SENSORS & TELEMETRY */}
          {activeTab === 'telemetry' && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                    ESP32 Telemetry & Sensor Observations
                  </h3>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                    Dedicated validation pipeline: Identity, Timestamp, Operational Range, and Hardware Safety Interlock
                  </p>
                </div>
                <button
                  onClick={() => setShowIngestModal(true)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    background: 'rgba(6, 182, 212, 0.15)',
                    border: '1px solid rgba(6, 182, 212, 0.3)',
                    color: '#38bdf8',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    fontSize: '0.82rem',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  <Terminal size={15} /> Transmit Sensor Reading
                </button>
              </div>

              {!telemetry || telemetry.length === 0 ? (
                <EmptyState
                  title="No sensor telemetry available"
                  description="Connect an ESP32 gateway to begin receiving field measurements. Unvalidated or synthetic readings are strictly forbidden."
                  icon={Cpu}
                  status="NO_DATA"
                  actionText="Transmit Initial Reading"
                  onAction={() => setShowIngestModal(true)}
                />
              ) : (
                <div className="glass-panel" style={{ overflow: 'hidden' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.82rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', background: 'rgba(0,0,0,0.2)', color: '#94a3b8' }}>
                        <th style={{ padding: '0.75rem 1rem' }}>Observed At</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Sensor ID</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Raw Value</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Calibrated</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Unit</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Validation Status</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Quality Flags</th>
                      </tr>
                    </thead>
                    <tbody>
                      {telemetry.map(t => (
                        <tr key={t.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                          <td style={{ padding: '0.75rem 1rem', color: '#f8fafc' }}>
                            {new Date(t.observed_at).toLocaleString()}
                          </td>
                          <td style={{ padding: '0.75rem 1rem', color: '#38bdf8', fontFamily: 'monospace' }}>
                            {t.sensor_id?.slice(0, 13)}...
                          </td>
                          <td style={{ padding: '0.75rem 1rem', color: '#94a3b8' }}>{t.raw_value}</td>
                          <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#34d399' }}>{t.calibrated_value}</td>
                          <td style={{ padding: '0.75rem 1rem', color: '#94a3b8' }}>{t.unit}</td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <StatusBadge status={t.validation_status} />
                          </td>
                          <td style={{ padding: '0.75rem 1rem', fontSize: '0.72rem', color: '#64748b' }}>
                            {Array.isArray(t.quality_flags) ? t.quality_flags.join(', ') : 'None'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* TAB 5: WEATHER & CLIMATE */}
          {activeTab === 'weather' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Weather & Climate Data Providers
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Real integration boundaries for NASA POWER and IMD Gridded Rainfall
                </p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
                <div className="glass-panel" style={{ padding: '1.25rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>NASA POWER API</h4>
                    <StatusBadge status={weatherProviderStatus?.providers?.NASA_POWER?.status || 'NOT_CONFIGURED'} />
                  </div>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1rem' }}>
                    Meteorological data, solar radiation (ALLSKY_SFC_SW_DWN), T2M_MIN/MAX, and historical agroclimatology.
                  </p>
                  <div style={{ fontSize: '0.72rem', color: '#64748b' }}>
                    Base URL: {weatherProviderStatus?.providers?.NASA_POWER?.configured ? 'Active' : 'Unconfigured'}
                  </div>
                </div>

                <div className="glass-panel" style={{ padding: '1.25rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>IMD Gridded Rainfall</h4>
                    <StatusBadge status="NOT_CONFIGURED" />
                  </div>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1rem' }}>
                    0.25° x 0.25° daily gridded rainfall, monsoon anomalies, and historical regional baselines.
                  </p>
                  <div style={{ fontSize: '0.72rem', color: '#64748b' }}>
                    Integration boundary ready for authorized API credentials.
                  </div>
                </div>
              </div>

              <EmptyState
                title="Weather data source not connected"
                description="Configure an approved weather data provider to retrieve observations. AgriCommand does not display fake temperature or precipitation values."
                icon={CloudSun}
                status="NOT_CONFIGURED"
              />
            </div>
          )}

          {/* TAB 6: SATELLITE & NDVI */}
          {activeTab === 'satellite' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Copernicus Sentinel-2 Multispectral Observation
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  13-band Level-2A BOA reflectance, cloud masking, and deterministic NDVI calculation
                </p>
              </div>

              <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>Spectral Band Architecture</h4>
                  <StatusBadge status="NOT_CONFIGURED" />
                </div>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1rem' }}>
                  Formula: NDVI = (B08 - B04) / (B08 + B04) | Cloud occlusion masking via SCL
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {satellitePipelineStatus?.bands_supported?.map((band: string) => (
                    <span key={band} style={{ padding: '3px 8px', borderRadius: '4px', background: 'rgba(255,255,255,0.05)', fontSize: '0.72rem', color: '#cbd5e1' }}>
                      {band}
                    </span>
                  ))}
                </div>
              </div>

              <EmptyState
                title="No satellite observations available"
                description="Connect the Sentinel-2 data pipeline to begin crop-health analysis. AgriCommand will not fabricate NDVI percentages without real spectral band imagery."
                icon={Satellite}
                status="NO_DATA"
              />
            </div>
          )}

          {/* TAB 7: SOIL */}
          {activeTab === 'soil' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Soil Profiles & ISRIC SoilGrids Integration
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Regional 250m priors separated strictly from certified laboratory soil tests
                </p>
              </div>

              <EmptyState
                title="No soil profiles configured"
                description="Connect field core laboratory samples or query regional ISRIC SoilGrids priors. Regional statistical priors are never presented as local field measurements."
                icon={Layers}
                status="NO_DATA"
              />
            </div>
          )}

          {/* TAB 8: WATER & FAO-56 */}
          {activeTab === 'water' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Water Management & FAO-56 Penman-Monteith
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Deterministic evapotranspiration (ET0), Kc stages, and root-zone water deficit calculations
                </p>
              </div>

              <EmptyState
                title="Insufficient validated data for water-demand calculation"
                description="FAO-56 requires validated weather inputs (temperature, humidity, solar radiation, wind speed) and calibrated crop growth stages. AgriCommand does not substitute random numbers."
                icon={Droplets}
                status="INSUFFICIENT_DATA"
              />
            </div>
          )}

          {/* TAB 9: PREDICTION MODELS */}
          {activeTab === 'predictions' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Agricultural Machine Learning & Predictions
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Production interfaces ready for XGBoost, Random Forest, or PyTorch models
                </p>
              </div>

              <EmptyState
                title="Prediction model not connected"
                description="The prediction interface is ready for a future agricultural model. AgriCommand does not return fake yield or risk numbers merely to populate dashboard cards."
                icon={Sparkles}
                status="NOT_CONFIGURED"
              />
            </div>
          )}

          {/* TAB 10: OPTIMIZATION */}
          {activeTab === 'optimization' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Resource & Water Allocation Optimization
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Mathematical optimization interfaces compatible with Google OR-Tools and Pyomo
                </p>
              </div>

              <EmptyState
                title="Optimization data unavailable"
                description="Provide validated resource and field constraints to run optimization. Schedules cannot be generated from fabricated inputs."
                icon={Sliders}
                status="INSUFFICIENT_DATA"
              />
            </div>
          )}

          {/* TAB 11: RECOMMENDATIONS */}
          {activeTab === 'recommendations' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Explainable Recommendation Engine
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Every recommendation answers: 1. What happened? 2. Why does it matter? 3. Which field is affected? 4. What action should be considered?
                </p>
              </div>

              {recommendations && recommendations.length > 0 ? (
                recommendations.map(rec => (
                  <ExplainableRecommendationCard key={rec.id} rec={rec} />
                ))
              ) : (
                <EmptyState
                  title="Insufficient validated evidence to generate a recommendation"
                  description="AgriCommand does not create fake advisories. Provide validated telemetry or weather alerts to trigger agronomic recommendations."
                  icon={MessageSquareQuote}
                  status="NO_DATA"
                  actionText="Ingest Validated Reading"
                  onAction={() => setShowIngestModal(true)}
                />
              )}
            </div>
          )}

          {/* TAB 12: HARVEST */}
          {activeTab === 'harvest' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Harvest Window Tracker
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Crop maturity tracking, expected harvest window, and yield uncertainty ranges
                </p>
              </div>

              <EmptyState
                title="Harvest estimation unavailable"
                description="Active crop cycles and calibrated yield prediction models are required to estimate harvest windows. Dates and yields are never fabricated."
                icon={Calendar}
                status="NO_DATA"
              />
            </div>
          )}

          {/* TAB 13: STORAGE */}
          {activeTab === 'storage' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Storage Network Evaluator
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Facility capacity, temperature, humidity, CO2 monitoring, and post-harvest loss tracking
                </p>
              </div>

              {storageFacilities && storageFacilities.length > 0 ? (
                <div>Storage facilities list</div>
              ) : (
                <EmptyState
                  title="No storage facilities configured"
                  description="Register cold stores, silos, or warehouse hubs to evaluate atmospheric conditions and prevent post-harvest spoilage."
                  icon={Warehouse}
                  status="NO_DATA"
                />
              )}
            </div>
          )}

          {/* TAB 14: OUTCOMES */}
          {activeTab === 'outcomes' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Observed Outcomes & Model Evaluation
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Step 9 of the closed decision loop — ground-truth outcome verification vs predicted values
                </p>
              </div>

              <EmptyState
                title="No observed outcomes recorded"
                description="Log actual harvest yields and post-irrigation soil responses to evaluate model variance and enable continuous agronomic learning."
                icon={Award}
                status="NO_DATA"
              />
            </div>
          )}

          {/* TAB 15: DATA QUALITY CENTER */}
          {activeTab === 'data-quality' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Data Quality & Telemetry Audit Center
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Traceable validation passes, rejected readings, stale devices, and calibration status
                </p>
              </div>

              {dataQualitySummary ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                  <div className="glass-panel" style={{ padding: '1rem' }}>
                    <div style={{ fontSize: '0.72rem', color: '#64748b' }}>Total Observations</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc' }}>{dataQualitySummary.total_observations_received}</div>
                  </div>
                  <div className="glass-panel" style={{ padding: '1rem' }}>
                    <div style={{ fontSize: '0.72rem', color: '#64748b' }}>Passed Validation</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#34d399' }}>{dataQualitySummary.validated_count}</div>
                  </div>
                  <div className="glass-panel" style={{ padding: '1rem' }}>
                    <div style={{ fontSize: '0.72rem', color: '#64748b' }}>Rejected Readings</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#fb7185' }}>{dataQualitySummary.rejected_count}</div>
                  </div>
                  <div className="glass-panel" style={{ padding: '1rem' }}>
                    <div style={{ fontSize: '0.72rem', color: '#64748b' }}>Stale Sensor Devices</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#fbbf24' }}>{dataQualitySummary.stale_sensor_count}</div>
                  </div>
                </div>
              ) : null}

              {dataQualitySummary?.total_observations_received === 0 && (
                <EmptyState
                  title="No sensor telemetry available"
                  description="Data quality metrics are derived strictly from live database observations. Connect hardware gateways to monitor sensor drift and calibration integrity."
                  icon={ShieldCheck}
                  status="NO_DATA"
                />
              )}
            </div>
          )}

          {/* TAB 16: AUDIT TRAIL */}
          {activeTab === 'audit' && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Immutable Audit Trail
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Traceable history of system actions, farm registrations, and field mutations
                </p>
              </div>

              {!auditTrail || auditTrail.length === 0 ? (
                <EmptyState
                  title="No audit events recorded yet"
                  description="Register a farm or configure a field to begin populating the immutable audit log."
                  icon={FileText}
                  status="NO_DATA"
                />
              ) : (
                <div className="glass-panel" style={{ overflow: 'hidden' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.82rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', background: 'rgba(0,0,0,0.2)', color: '#94a3b8' }}>
                        <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Action</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Entity</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Entity ID</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Source</th>
                      </tr>
                    </thead>
                    <tbody>
                      {auditTrail.map(a => (
                        <tr key={a.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                          <td style={{ padding: '0.75rem 1rem', color: '#f8fafc' }}>
                            {new Date(a.created_at).toLocaleString()}
                          </td>
                          <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#38bdf8' }}>{a.action}</td>
                          <td style={{ padding: '0.75rem 1rem', color: '#34d399' }}>{a.entity_type}</td>
                          <td style={{ padding: '0.75rem 1rem', color: '#64748b', fontFamily: 'monospace' }}>{a.entity_id?.slice(0, 10)}...</td>
                          <td style={{ padding: '0.75rem 1rem', color: '#94a3b8' }}>{a.source}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* MODAL: REGISTER FARM */}
      {showFarmModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100
        }}>
          <div className="glass-panel" style={{ width: '480px', padding: '1.5rem', border: '1px solid rgba(255,255,255,0.15)' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.5rem' }}>
              Register Agricultural Farm
            </h3>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1.25rem' }}>
              Step 1 of Decision Loop: Establish real farm identity & geo-coordinates
            </p>

            <form onSubmit={handleCreateFarm}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.35rem' }}>
                  Farm Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Green Valley Research Farm"
                  value={newFarmName}
                  onChange={(e) => setNewFarmName(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.8rem',
                    background: 'rgba(0,0,0,0.4)',
                    border: '1px solid rgba(255,255,255,0.12)',
                    borderRadius: '6px',
                    color: '#f8fafc',
                    fontSize: '0.85rem'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.35rem' }}>
                    Total Area (Hectares)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={newFarmArea}
                    onChange={(e) => setNewFarmArea(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      background: 'rgba(0,0,0,0.4)',
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: '6px',
                      color: '#f8fafc',
                      fontSize: '0.85rem'
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.35rem' }}>
                    Location Name
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Pune Ag Tech Zone"
                    value={newFarmLocation}
                    onChange={(e) => setNewFarmLocation(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      background: 'rgba(0,0,0,0.4)',
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: '6px',
                      color: '#f8fafc',
                      fontSize: '0.85rem'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.5rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.35rem' }}>
                    Latitude
                  </label>
                  <input
                    type="text"
                    value={newFarmLat}
                    onChange={(e) => setNewFarmLat(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      background: 'rgba(0,0,0,0.4)',
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: '6px',
                      color: '#f8fafc',
                      fontSize: '0.85rem'
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.35rem' }}>
                    Longitude
                  </label>
                  <input
                    type="text"
                    value={newFarmLon}
                    onChange={(e) => setNewFarmLon(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      background: 'rgba(0,0,0,0.4)',
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: '6px',
                      color: '#f8fafc',
                      fontSize: '0.85rem'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowFarmModal(false)}
                  style={{
                    padding: '0.5rem 1rem',
                    background: 'transparent',
                    border: '1px solid rgba(255,255,255,0.1)',
                    color: '#94a3b8',
                    borderRadius: '6px',
                    fontSize: '0.82rem',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '0.5rem 1.25rem',
                    background: '#10b981',
                    border: 'none',
                    color: '#ffffff',
                    fontWeight: 600,
                    borderRadius: '6px',
                    fontSize: '0.82rem',
                    cursor: 'pointer'
                  }}
                >
                  Register Farm
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: MAP FIELD */}
      {showFieldModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100
        }}>
          <div className="glass-panel" style={{ width: '480px', padding: '1.5rem', border: '1px solid rgba(255,255,255,0.15)' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.5rem' }}>
              Map Field Boundary
            </h3>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1.25rem' }}>
              Step 2 of Decision Loop: Establish GeoJSON field polygon & soil properties
            </p>

            <form onSubmit={handleCreateField}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.35rem' }}>
                  Field Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. North Plot - Durum Wheat"
                  value={newFieldName}
                  onChange={(e) => setNewFieldName(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.8rem',
                    background: 'rgba(0,0,0,0.4)',
                    border: '1px solid rgba(255,255,255,0.12)',
                    borderRadius: '6px',
                    color: '#f8fafc',
                    fontSize: '0.85rem'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.5rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.35rem' }}>
                    Area (Hectares)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={newFieldArea}
                    onChange={(e) => setNewFieldArea(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      background: 'rgba(0,0,0,0.4)',
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: '6px',
                      color: '#f8fafc',
                      fontSize: '0.85rem'
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.35rem' }}>
                    Soil Classification
                  </label>
                  <input
                    type="text"
                    value={newFieldSoil}
                    onChange={(e) => setNewFieldSoil(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      background: 'rgba(0,0,0,0.4)',
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: '6px',
                      color: '#f8fafc',
                      fontSize: '0.85rem'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowFieldModal(false)}
                  style={{
                    padding: '0.5rem 1rem',
                    background: 'transparent',
                    border: '1px solid rgba(255,255,255,0.1)',
                    color: '#94a3b8',
                    borderRadius: '6px',
                    fontSize: '0.82rem',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '0.5rem 1.25rem',
                    background: '#10b981',
                    border: 'none',
                    color: '#ffffff',
                    fontWeight: 600,
                    borderRadius: '6px',
                    fontSize: '0.82rem',
                    cursor: 'pointer'
                  }}
                >
                  Save Field Polygon
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: INGEST SENSOR TELEMETRY */}
      {showIngestModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100
        }}>
          <div className="glass-panel" style={{ width: '480px', padding: '1.5rem', border: '1px solid rgba(6,182,212,0.3)' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.5rem' }}>
              Transmit Telemetry to Ingestion Boundary
            </h3>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1.25rem' }}>
              Sends telemetry directly into the TelemetryValidator pipeline with real bounds and hardware safety checks.
            </p>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.35rem' }}>
                Sensor Probe
              </label>
              <select
                value={testSensorType}
                onChange={(e) => setTestSensorType(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.8rem',
                  background: 'rgba(0,0,0,0.4)',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  fontSize: '0.85rem'
                }}
              >
                <option value="capacitive_soil_moisture">Capacitive Soil Moisture Sensor (%)</option>
                <option value="sht31_temperature">SHT31 Ambient Temperature (°C)</option>
              </select>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.35rem' }}>
                Raw Measured Value ({testSensorType === 'capacitive_soil_moisture' ? '%' : '°C'})
              </label>
              <input
                type="number"
                step="0.1"
                value={testRawVal}
                onChange={(e) => setTestRawVal(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.8rem',
                  background: 'rgba(0,0,0,0.4)',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  fontSize: '0.85rem'
                }}
              />
              <span style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '0.3rem', display: 'block' }}>
                Try values &lt; 20% to test moisture deficit advisory, or &gt; 120% to test validation pipeline rejection!
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button
                type="button"
                onClick={() => setShowIngestModal(false)}
                style={{
                  padding: '0.5rem 1rem',
                  background: 'transparent',
                  border: '1px solid rgba(255,255,255,0.1)',
                  color: '#94a3b8',
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleIngestTelemetry}
                style={{
                  padding: '0.5rem 1.25rem',
                  background: '#06b6d4',
                  border: 'none',
                  color: '#ffffff',
                  fontWeight: 600,
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  cursor: 'pointer'
                }}
              >
                Ingest & Validate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
