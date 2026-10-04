import { 
  Building2, Map, Cpu, ShieldCheck, Sparkles, 
  Sliders, MessageSquareQuote, Play, Award 
} from 'lucide-react';
import { StatusBadge } from './StatusBadge';

interface Stage {
  key: string;
  name: string;
  description: string;
  status: string;
  details?: string;
  icon: any;
}

interface Props {
  loopData?: Record<string, { status: string; details: string }>;
}

export const DecisionLoopTracker: React.FC<Props> = ({ loopData }) => {
  const stages: Stage[] = [
    {
      key: 'step_1_registration',
      name: '1. Registration',
      description: 'Farm identity & metadata',
      status: loopData?.step_1_registration?.status || 'NOT_STARTED',
      details: loopData?.step_1_registration?.details || 'No farm registered',
      icon: Building2
    },
    {
      key: 'step_2_field_mapping',
      name: '2. Field Mapping',
      description: 'Polygon GIS boundaries & crops',
      status: loopData?.step_2_field_mapping?.status || 'AWAITING_DATA',
      details: loopData?.step_2_field_mapping?.details || 'No fields mapped yet',
      icon: Map
    },
    {
      key: 'step_3_data_collection',
      name: '3. Data Collection',
      description: 'ESP32 & sensor telemetry',
      status: loopData?.step_3_data_collection?.status || 'AWAITING_DATA',
      details: loopData?.step_3_data_collection?.details || 'No sensor telemetry available',
      icon: Cpu
    },
    {
      key: 'step_4_validation',
      name: '4. Validation',
      description: 'Integrity checks & safety interlocks',
      status: loopData?.step_4_validation?.status || 'NOT_STARTED',
      details: loopData?.step_4_validation?.details || 'Awaiting observations',
      icon: ShieldCheck
    },
    {
      key: 'step_5_prediction',
      name: '5. Prediction',
      description: 'Yield & climate-risk ML models',
      status: loopData?.step_5_prediction?.status || 'NOT_CONFIGURED',
      details: loopData?.step_5_prediction?.details || 'Prediction model not connected',
      icon: Sparkles
    },
    {
      key: 'step_6_optimization',
      name: '6. Optimization',
      description: 'Resource & water allocation solver',
      status: loopData?.step_6_optimization?.status || 'AWAITING_DATA',
      details: loopData?.step_6_optimization?.details || 'Optimization data unavailable',
      icon: Sliders
    },
    {
      key: 'step_7_recommendation',
      name: '7. Recommendation',
      description: 'Explainable 4-question advisories',
      status: loopData?.step_7_recommendation?.status || 'NO_DATA',
      details: loopData?.step_7_recommendation?.details || 'Insufficient validated evidence',
      icon: MessageSquareQuote
    },
    {
      key: 'step_8_action',
      name: '8. Action',
      description: 'Safety-interlocked dispatch',
      status: loopData?.step_8_action?.status || 'NOT_STARTED',
      details: loopData?.step_8_action?.details || 'Human confirmation required',
      icon: Play
    },
    {
      key: 'step_9_outcome_learning',
      name: '9. Outcome & Learning',
      description: 'Model evaluation vs ground truth',
      status: loopData?.step_9_outcome_learning?.status || 'NOT_STARTED',
      details: loopData?.step_9_outcome_learning?.details || 'No observed outcomes recorded',
      icon: Award
    }
  ];

  return (
    <div className="glass-panel" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '0.75rem' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
            Nine-Step Closed-Loop Decision Cycle
          </h3>
          <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
            Data changes decisions — each stage reflects real system provenance
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '0.75rem' }}>
        {stages.map((stage) => {
          const Icon = stage.icon;
          const isComplete = stage.status === 'COMPLETE';

          return (
            <div 
              key={stage.key}
              style={{
                background: isComplete ? 'rgba(16, 185, 129, 0.05)' : 'rgba(255, 255, 255, 0.02)',
                border: isComplete ? '1px solid rgba(16, 185, 129, 0.25)' : '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: '8px',
                padding: '0.85rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <div style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    background: isComplete ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: isComplete ? '#34d399' : '#94a3b8'
                  }}>
                    <Icon size={16} />
                  </div>
                  <StatusBadge status={stage.status} />
                </div>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc', marginBottom: '0.2rem' }}>
                  {stage.name}
                </h4>
                <p style={{ fontSize: '0.72rem', color: '#64748b', marginBottom: '0.5rem' }}>
                  {stage.description}
                </p>
              </div>
              <p style={{ fontSize: '0.7rem', color: '#94a3b8', borderTop: '1px solid rgba(255,255,255,0.04)', paddingTop: '0.4rem' }}>
                {stage.details}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
