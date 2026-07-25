import React from 'react';
import RiskBadge from './RiskBadge';

const AnomalyTable = ({ anomalies, loading, onRowClick }) => {
  if (loading) {
    return (
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent mx-auto mb-2"></div>
          <p className="text-slate-400">Loading anomalies...</p>
        </div>
      </div>
    );
  }

  if (!anomalies || anomalies.length === 0) {
    return (
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-8 text-center text-slate-400">
        No anomalies detected
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg overflow-hidden">
      <div className="overflow-x-auto scrollbar-thin scrollbar-track-slate-800 scrollbar-thumb-slate-600">
        <table className="w-full text-sm">
          <thead className="bg-slate-900/50 border-b border-slate-700/50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-300">Entity ID</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-300">Risk Level</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-300">Confidence</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-300">Flagged By</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-300">Resource</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-300">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {anomalies.map((anomaly, idx) => (
              <tr
                key={idx}
                onClick={() => onRowClick && onRowClick(anomaly)}
                className="hover:bg-slate-700/30 transition cursor-pointer"
              >
                <td className="px-4 py-3 text-white">{anomaly.entity_id}</td>
                <td className="px-4 py-3">
                  <RiskBadge level={anomaly.risk_level} />
                </td>
                <td className="px-4 py-3 text-slate-300">
                  {(anomaly.confidence * 100).toFixed(0)}%
                </td>
                <td className="px-4 py-3">
                  <span className="text-xs bg-slate-700/50 px-2 py-1 rounded text-slate-300">
                    {anomaly.flagged_by}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-300">{anomaly.resource_accessed}</td>
                <td className="px-4 py-3 text-slate-400 text-xs">
                  {new Date(anomaly.timestamp).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AnomalyTable;
