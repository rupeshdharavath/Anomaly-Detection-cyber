import React from 'react';
import RiskBadge from './RiskBadge';

const AlertDetail = ({ selectedAlert }) => {
  if (!selectedAlert?.alert) {
    return null;
  }

  const { alert, relatedAnomaly } = selectedAlert;
  const attackType = relatedAnomaly?.attack_type || alert.attack_type || 'unknown';
  const createdAt = alert.created_at ? new Date(alert.created_at).toLocaleString() : 'Unknown';
  const acknowledgedAt = alert.acknowledged_at ? new Date(alert.acknowledged_at).toLocaleString() : 'Not acknowledged';
  const entityId = alert.entity_id || relatedAnomaly?.entity_id || 'Unknown';
  const resource = relatedAnomaly?.resource_accessed || alert.resource_accessed || 'Unknown';
  const location = relatedAnomaly?.geo_location || alert.geo_location || 'Unknown';
  const authMethod = relatedAnomaly?.auth_method || alert.auth_method || 'Unknown';
  const attacker = alert.acknowledged_by || 'N/A';
  const statusLabel = alert.acknowledged ? 'Acknowledged' : 'Open';
  const source = alert.flagged_by || 'Unknown';

  return (
    <div className="bg-black text-white border border-slate-300/20 rounded-3xl shadow-xl p-6 hover:shadow-2xl transition">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <h3 className="text-2xl font-semibold text-white">Alert details dashboard</h3>
          <p className="text-slate-400 mt-2 max-w-2xl">
            This view shows every key detail for the selected alert, including actor, event, time, and model metadata.
          </p>
        </div>
        <RiskBadge level={alert.severity} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <div className="rounded-3xl bg-slate-900/80 border border-slate-700 p-5">
            <p className="text-slate-400 text-sm uppercase tracking-[0.18em]">Alert summary</p>
            <div className="mt-4 grid gap-3">
              {[
                ['Alert ID', alert.alert_id],
                ['Status', statusLabel],
                ['Severity', alert.severity],
                ['Created', createdAt],
                ['Acknowledged at', acknowledgedAt],
                ['Acknowledged by', attacker],
                ['Action Required', alert.action_required ? 'Yes' : 'No'],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between gap-4 text-sm text-slate-300">
                  <span className="font-medium text-slate-400">{label}</span>
                  <span className="text-white text-right">{value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl bg-slate-900/80 border border-slate-700 p-5">
            <p className="text-slate-400 text-sm uppercase tracking-[0.18em]">Event data</p>
            <div className="mt-4 grid gap-3 text-sm text-slate-300">
              {[
                ['Entity', entityId],
                ['Anomaly ID', alert.anomaly_id || relatedAnomaly?.anomaly_id || 'N/A'],
                ['Attack Type', attackType.replace('_', ' ')],
                ['Resource', resource],
                ['Location', location],
                ['Auth Method', authMethod],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between gap-4">
                  <span className="font-medium text-slate-400">{label}</span>
                  <span className="text-white text-right">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-3xl bg-slate-900/80 border border-slate-700 p-5">
            <p className="text-slate-400 text-sm uppercase tracking-[0.18em]">Risk & model metadata</p>
            <div className="mt-4 grid gap-3 text-sm text-slate-300">
              {[
                ['Risk Score', alert.risk_score?.toFixed(2) ?? '0.00'],
                ['Confidence', `${((alert.confidence ?? 0) * 100).toFixed(0)}%`],
                ['Flagged by', source],
                ['Message', alert.message || 'No message'],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between gap-4">
                  <span className="font-medium text-slate-400">{label}</span>
                  <span className="text-white text-right">{value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl bg-slate-900/80 border border-slate-700 p-5">
            <p className="text-slate-400 text-sm uppercase tracking-[0.18em]">Related anomaly insight</p>
            {relatedAnomaly ? (
              <div className="mt-4 grid gap-3 text-sm text-slate-300">
                {[
                  ['Anomaly Score', relatedAnomaly.risk_score?.toFixed(2) ?? 'N/A'],
                  ['Accuracy', `${((relatedAnomaly.confidence ?? 0) * 100).toFixed(0)}%`],
                  ['Source', relatedAnomaly.flagged_by || 'Unknown'],
                  [
                    'Detected',
                    relatedAnomaly.created_at
                      ? new Date(relatedAnomaly.created_at).toLocaleString()
                      : relatedAnomaly.timestamp
                      ? new Date(relatedAnomaly.timestamp).toLocaleString()
                      : 'N/A',
                  ],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between gap-4">
                    <span className="font-medium text-slate-400">{label}</span>
                    <span className="text-white text-right">{value}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-400 mt-4">No related anomaly details available.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertDetail;
