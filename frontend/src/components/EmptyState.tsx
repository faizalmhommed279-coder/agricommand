import React from 'react';
import { LucideIcon, HelpCircle } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: LucideIcon;
  status?: string;
  actionText?: string;
  onAction?: () => void;
  subtleInfo?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon: Icon = HelpCircle,
  status = 'NO_DATA',
  actionText,
  onAction,
  subtleInfo
}) => {
  return (
    <div className="empty-state-box">
      <div className="icon-wrapper">
        <Icon size={26} />
      </div>
      <div className="mb-2">
        <StatusBadge status={status} />
      </div>
      <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#f8fafc', marginBottom: '0.4rem' }}>
        {title}
      </h3>
      <p style={{ color: '#94a3b8', fontSize: '0.875rem', maxWidth: '440px', lineHeight: 1.5, marginBottom: '1.25rem' }}>
        {description}
      </p>

      {actionText && onAction && (
        <button
          onClick={onAction}
          style={{
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: '#ffffff',
            fontWeight: 600,
            fontSize: '0.85rem',
            padding: '0.5rem 1.25rem',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 4px 14px rgba(16, 185, 129, 0.35)',
            transition: 'all 0.2s ease'
          }}
        >
          {actionText}
        </button>
      )}

      {subtleInfo && (
        <p style={{ marginTop: '1rem', fontSize: '0.75rem', color: '#64748b' }}>
          {subtleInfo}
        </p>
      )}
    </div>
  );
};
