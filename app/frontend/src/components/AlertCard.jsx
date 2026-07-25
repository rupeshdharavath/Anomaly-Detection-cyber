import React from 'react';
import { AlertTriangle } from 'lucide-react';
import RiskBadge from './RiskBadge';

const AlertCard = ({ alert, onAcknowledge, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="bg-black text-white border border-slate-300/20 rounded-3xl p-4 shadow-lg hover:shadow-2xl transition cursor-pointer"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={18} className="text-red-400" />
            <RiskBadge level={alert.severity} />
            {alert.action_required && (
              <span className="text-xs bg-red-500/20 text-red-300 px-2 py-1 rounded">
                Action Required
              </span>
            )}
          </div>
          <p className="text-white font-medium">{alert.message}</p>
          <p className="text-slate-400 text-xs mt-1">
            ID: {alert.alert_id} • {new Date(alert.created_at).toLocaleString()}
          </p>
        </div>
        {!alert.acknowledged && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onAcknowledge(alert.alert_id);
            }}
            className="px-3 py-1 bg-blue-500/20 border border-blue-500/50 text-blue-300 hover:bg-blue-500/30 rounded text-xs font-medium transition whitespace-nowrap"
          >
            Acknowledge
          </button>
        )}
      </div>
    </div>
  );
};

export default AlertCard;
