import React from 'react';
import { AlertTriangle, AlertCircle, Info, CheckCircle } from 'lucide-react';

const RiskBadge = ({ level }) => {
  const colors = {
    low: 'bg-green-500/20 text-green-300 border-green-500/30',
    medium: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
    high: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
    critical: 'bg-red-500/20 text-red-300 border-red-500/30',
  };

  const icons = {
    low: <CheckCircle size={14} />,
    medium: <Info size={14} />,
    high: <AlertCircle size={14} />,
    critical: <AlertTriangle size={14} />,
  };

  return (
    <div className={`border rounded-full px-3 py-1 text-xs font-semibold flex items-center gap-1 w-fit ${colors[level] || colors.low}`}>
      {icons[level]}
      {level.charAt(0).toUpperCase() + level.slice(1)}
    </div>
  );
};

export default RiskBadge;
