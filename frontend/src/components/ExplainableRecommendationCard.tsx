import React from 'react';
import { AlertTriangle, HelpCircle, Target, ArrowRight, ShieldCheck } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

interface RecommendationProps {
  rec: {
    id: string;
    title: string;
    what_happened: string;
    why_it_matters: string;
    affected_field_summary: string;
    suggested_action: string;
    urgency: string;
    evidence_provenance?: any;
    human_status?: string;
    created_at?: string;
  };
}

export const ExplainableRecommendationCard: React.FC<RecommendationProps> = ({ rec }) => {
  return (
    <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '1rem', borderLeft: rec.urgency === 'HIGH' ? '4px solid #f43f5e' : '4px solid #10b981' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertTriangle size={18} style={{ color: rec.urgency === 'HIGH' ? '#f43f5e' : '#10b981' }} />
          <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
            {rec.title}
          </h4>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{
            fontSize: '0.7rem',
            padding: '2px 8px',
            borderRadius: '4px',
            fontWeight: 600,
            background: rec.urgency === 'HIGH' ? 'rgba(244, 63, 94, 0.2)' : 'rgba(16, 185, 129, 0.2)',
            color: rec.urgency === 'HIGH' ? '#fb7185' : '#34d399'
          }}>
            {rec.urgency} PRIORITY
          </span>
          <StatusBadge status={rec.human_status || 'PENDING_REVIEW'} />
        </div>
      </div>

      {/* The 4 Explainable Core Questions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.85rem', marginBottom: '1rem' }}>
        {/* 1. What happened? */}
        <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#38bdf8', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <HelpCircle size={13} /> 1. WHAT HAPPENED?
          </div>
          <p style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.4 }}>
            {rec.what_happened}
          </p>
        </div>

        {/* 2. Why does it matter? */}
        <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#fbbf24', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <AlertTriangle size={13} /> 2. WHY DOES IT MATTER?
          </div>
          <p style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.4 }}>
            {rec.why_it_matters}
          </p>
        </div>

        {/* 3. Which field is affected? */}
        <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#a78bfa', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Target size={13} /> 3. WHICH FIELD IS AFFECTED?
          </div>
          <p style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.4 }}>
            {rec.affected_field_summary}
          </p>
        </div>

        {/* 4. What action should be considered? */}
        <div style={{ background: 'rgba(16, 185, 129, 0.05)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#34d399', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <ArrowRight size={13} /> 4. SUGGESTED ACTION
          </div>
          <p style={{ fontSize: '0.82rem', color: '#f8fafc', lineHeight: 1.4, fontWeight: 500 }}>
            {rec.suggested_action}
          </p>
        </div>
      </div>

      {/* Safety Interlock & Provenance */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid rgba(255,255,255,0.04)', paddingTop: '0.65rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.72rem', color: '#64748b' }}>
          <ShieldCheck size={14} style={{ color: '#10b981' }} />
          Hardware Safety Rule: Actuator trigger requires explicit human authorization.
        </div>

        <button
          style={{
            background: 'rgba(16, 185, 129, 0.15)',
            color: '#34d399',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            padding: '4px 12px',
            borderRadius: '6px',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer'
          }}
          onClick={() => alert(`Advisory acknowledged for: ${rec.title}`)}
        >
          Confirm & Authorize Action
        </button>
      </div>
    </div>
  );
};
