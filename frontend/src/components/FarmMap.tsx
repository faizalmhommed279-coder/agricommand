import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { Layers } from 'lucide-react';

interface Field {
  id: string;
  name: string;
  area_hectares?: number;
  polygon_geojson?: any;
}

interface FarmMapProps {
  fields: Field[];
  selectedFieldId?: string;
  onSelectField?: (fieldId: string) => void;
  center?: [number, number];
}

export const FarmMap: React.FC<FarmMapProps> = ({
  fields,
  selectedFieldId,
  onSelectField,
  center = [20.5937, 78.9629] // Default overview center
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const leafletInstance = useRef<L.Map | null>(null);
  const geojsonLayer = useRef<L.GeoJSON | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;

    if (!leafletInstance.current) {
      const map = L.map(mapRef.current, {
        zoomControl: true,
        attributionControl: false
      }).setView(center, 5);

      // CartoDB Dark Matter tiles for sleek high-tech agricultural command center aesthetic
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19
      }).addTo(map);

      leafletInstance.current = map;
    }

    return () => {
      // Keep instance alive during state re-renders
    };
  }, []);

  // Update field polygons
  useEffect(() => {
    const map = leafletInstance.current;
    if (!map) return;

    if (geojsonLayer.current) {
      map.removeLayer(geojsonLayer.current);
      geojsonLayer.current = null;
    }

    if (fields && fields.length > 0) {
      const features: any[] = [];
      fields.forEach(f => {
        if (f.polygon_geojson) {
          features.push({
            type: 'Feature',
            properties: { id: f.id, name: f.name, area: f.area_hectares },
            geometry: f.polygon_geojson
          });
        }
      });

      if (features.length > 0) {
        const featureCollection = {
          type: 'FeatureCollection',
          features
        };

        const layer = L.geoJSON(featureCollection as any, {
          style: (feature) => {
            const isSelected = feature?.properties?.id === selectedFieldId;
            return {
              color: isSelected ? '#06b6d4' : '#10b981',
              weight: isSelected ? 3 : 2,
              opacity: 0.9,
              fillColor: isSelected ? '#06b6d4' : '#10b981',
              fillOpacity: isSelected ? 0.35 : 0.15
            };
          },
          onEachFeature: (feature, layer) => {
            layer.bindPopup(`<b>${feature.properties.name}</b><br/>Area: ${feature.properties.area || 'N/A'} ha`);
            layer.on('click', () => {
              if (onSelectField) onSelectField(feature.properties.id);
            });
          }
        }).addTo(map);

        geojsonLayer.current = layer;

        try {
          const bounds = layer.getBounds();
          if (bounds.isValid()) {
            map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16 });
          }
        } catch (e) {
          console.warn('Map fitBounds failed:', e);
        }
      }
    }
  }, [fields, selectedFieldId, onSelectField]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '440px', borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.08)' }}>
      <div ref={mapRef} style={{ width: '100%', height: '100%' }} />

      {(!fields || fields.length === 0) && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(15, 23, 42, 0.88)',
          backdropFilter: 'blur(8px)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          padding: '1.25rem 2rem',
          borderRadius: '12px',
          textAlign: 'center',
          zIndex: 400,
          pointerEvents: 'none'
        }}>
          <Layers size={28} style={{ color: '#10b981', margin: '0 auto 0.5rem auto' }} />
          <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '0.25rem' }}>No field boundaries configured</h4>
          <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Map field coordinates to render spatial polygons</p>
        </div>
      )}

      <div style={{
        position: 'absolute',
        bottom: '12px',
        left: '12px',
        background: 'rgba(15, 23, 42, 0.8)',
        backdropFilter: 'blur(6px)',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: '6px',
        padding: '4px 10px',
        fontSize: '0.72rem',
        color: '#94a3b8',
        zIndex: 400
      }}>
        CartoDB Dark Basemap | PostGIS / GeoJSON Compatible
      </div>
    </div>
  );
};
