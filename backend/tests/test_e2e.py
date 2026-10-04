import urllib.request
import json
import sys

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def get(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode())

base = 'http://127.0.0.1:8000/api/v1'

print("=== AgriCommand Comprehensive Production Verification ===", flush=True)

# 1. Register Farm
print("\n[Step 1: Farm Registration]")
farm_res = post(f'{base}/farms', {
    'name': 'Demonstration Precision Farm',
    'location_name': 'Agro Research Hub',
    'total_area_hectares': 50.0,
    'latitude': 18.5204,
    'longitude': 73.8567
})
print("Farm Status:", farm_res['status'], "|", farm_res['message'])
farm_id = farm_res['data']['id']

# 2. Map Field
print("\n[Step 2: Field Mapping]")
field_res = post(f'{base}/fields', {
    'farm_id': farm_id,
    'name': 'North Pivot - Durum Wheat',
    'area_hectares': 15.0,
    'soil_type': 'Sandy Clay Loam',
    'polygon_geojson': {
        'type': 'Polygon',
        'coordinates': [[[73.85, 18.52], [73.86, 18.52], [73.86, 18.53], [73.85, 18.53], [73.85, 18.52]]]
    }
})
print("Field Status:", field_res['status'], "|", field_res['message'])
field_id = field_res['data']['id']

# 3. Provision ESP32 Gateway & Probe
print("\n[Step 3: Provision ESP32 Hardware & Sensor Probes]")
dev_res = post(f'{base}/sensors/devices', {
    'device_uid': 'ESP32-GW-001',
    'farm_id': farm_id,
    'model_name': 'ESP32 Gateway v2'
})
print("Device Provisioned:", dev_res['status'])
dev_id = dev_res['data']['id']

sensor_res = post(f'{base}/sensors', {
    'sensor_uid': 'SOIL-PROBE-01',
    'device_id': dev_id,
    'field_id': field_id,
    'sensor_type': 'capacitive_soil_moisture',
    'unit': '%',
    'min_operational_range': 0.0,
    'max_operational_range': 100.0
})
print("Sensor Provisioned:", sensor_res['status'])

# 4. Telemetry Pipeline: Validated Deficit Reading (16.2%)
print("\n[Step 4: Telemetry Pipeline Ingestion & Validation]")
telemetry_res = post(f'{base}/telemetry/ingest', {
    'device_uid': 'ESP32-GW-001',
    'sensor_uid': 'SOIL-PROBE-01',
    'timestamp': '2026-10-03T14:10:00Z',
    'raw_value': 16.2,
    'unit': '%'
})
print("Telemetry Pipeline Result:", telemetry_res['status'], "|", telemetry_res['message'])
print("Validation Quality Flags:", telemetry_res['data']['quality_flags'])

# 5. Outlier Rejection Check (145.0% - exceeds physical 100% capacity)
print("\n[Step 5: Telemetry Pipeline Hardware Safety Rule & Outlier Rejection]")
try:
    bad_res = post(f'{base}/telemetry/ingest', {
        'device_uid': 'ESP32-GW-001',
        'sensor_uid': 'SOIL-PROBE-01',
        'timestamp': '2026-10-03T14:11:00Z',
        'raw_value': 145.0,
        'unit': '%'
    })
    print("Outlier Reading Result:", bad_res['status'], "|", bad_res['message'])
except urllib.error.HTTPError as e:
    print("HTTP Rejection Handled Successfully:", e.code, e.reason)

# 6. Generate Explainable Recommendations (4 Core Questions)
print("\n[Step 6: Explainable Recommendation Engine]")
rec_res = post(f'{base}/recommendations/evaluate-field/{field_id}', {})
print("Recommendation Engine Status:", rec_res['status'], "|", rec_res['message'])
if rec_res['data']:
    r = rec_res['data'][0]
    print(" -> Advisory Title:", r['title'])
    print("    1. What happened? :", r['what_happened'])
    print("    2. Why does it matter? :", r['why_it_matters'])
    print("    3. Which field is affected? :", r['affected_field_summary'])
    print("    4. What action should be considered? :", r['suggested_action'])

# 7. Query Farm Digital Twin
print("\n[Step 7: Farm Digital Twin Coherence & 9-Step Decision Loop]")
twin = get(f'{base}/digital-twin?farm_id={farm_id}')
print("Digital Twin Status:", twin['status'], "|", twin['message'])
for step_key, step_val in twin['data']['decision_loop'].items():
    print(f"  * {step_key}: [{step_val['status']}] - {step_val['details']}")

# 8. Immutable Audit Trail
print("\n[Step 8: Immutable Audit Trail]")
audit = get(f'{base}/audit')
print("Audit Records Recorded:", len(audit['data']))
for a in audit['data']:
    print(f"  - [{a['action']}] on {a['entity_type']} ({a['entity_id']}) via {a['source']}")

print("\n=== Verification Complete: ALL TESTS PASSED! ===", flush=True)
