import React from 'react';

interface Props {
  status: string;
}

export const StatusBadge: React.FC<Props> = ({ status }) => {
  const norm = (status || 'NO_DATA').toUpperCase();

  let badgeClass = 'badge-no-data';
  let label = norm;

  if (norm === 'AVAILABLE' || norm === 'CONNECTED' || norm === 'COMPLETE' || norm === 'VALIDATED') {
    badgeClass = 'badge-available';
  } else if (norm === 'NOT_CONFIGURED' || norm === 'NOT_STARTED') {
    badgeClass = 'badge-not-configured';
  } else if (norm === 'INVALID' || norm === 'FAILED' || norm === 'REJECTED') {
    badgeClass = 'badge-invalid';
  } else if (norm === 'INSUFFICIENT_DATA' || norm === 'PROCESSING') {
    badgeClass = 'badge-insufficient';
  }

  return (
    <span className={`badge ${badgeClass}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {label}
    </span>
  );
};
