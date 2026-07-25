import React from 'react';
import { AlertCircle, TrendingUp, Shield, Activity } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, trend, color = 'blue' }) => {
  const colorClasses = {
    blue: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
    red: 'bg-red-500/10 border-red-500/20 text-red-400',
    green: 'bg-green-500/10 border-green-500/20 text-green-400',
    yellow: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
  };

  return (
    <div className={`border rounded-lg p-6 backdrop-blur-sm ${colorClasses[color]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-white mt-2">{value}</p>
          {trend && (
            <p className="text-xs mt-2 flex items-center gap-1">
              <TrendingUp size={14} />
              {trend}
            </p>
          )}
        </div>
        <Icon size={32} className="opacity-50" />
      </div>
    </div>
  );
};

export default StatCard;
