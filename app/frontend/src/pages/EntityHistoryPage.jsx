import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useStore } from '../store/store';
import RiskBadge from '../components/RiskBadge';

const EntityHistoryPage = () => {
  const { entityId } = useParams();
  const { fetchEntityHistory } = useStore();
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchEntityHistory(entityId);
        setHistory(data);
      } catch (err) {
        setError(err.message || 'Could not load entity history');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [entityId, fetchEntityHistory]);

  return (
    <div className="min-h-screen bg-transparent text-slate-100 p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Entity History</h1>
          <p className="text-slate-400 mt-2">Behavior history and risk trends for {entityId}.</p>
        </div>

        {loading ? (
          <div className="rounded-3xl bg-slate-800/70 border border-slate-700 p-10 text-center text-slate-400">
            Loading history...
          </div>
        ) : error ? (
          <div className="rounded-3xl bg-red-500/10 border border-red-500/20 p-10 text-red-200">
            {error}
          </div>
        ) : history ? (
          <div className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="rounded-3xl bg-slate-800/70 border border-slate-700 p-6">
                <p className="text-slate-400 text-sm uppercase">Entity</p>
                <p className="mt-3 text-2xl font-semibold text-white">{history.profile.name || entityId}</p>
                <p className="mt-2 text-slate-500">{history.profile.department || 'Unknown department'}</p>
              </div>
              <div className="rounded-3xl bg-slate-800/70 border border-slate-700 p-6">
                <p className="text-slate-400 text-sm uppercase">Typical location</p>
                <p className="mt-3 text-white">{history.profile.office || 'Unknown'}</p>
              </div>
              <div className="rounded-3xl bg-slate-800/70 border border-slate-700 p-6">
                <p className="text-slate-400 text-sm uppercase">Risk level</p>
                <div className="mt-3">
                  <RiskBadge level={history.stats.risk_level || 'low'} />
                </div>
              </div>
            </div>

            <div className="rounded-3xl bg-slate-800/70 border border-slate-700 p-6">
              <h2 className="text-xl font-semibold text-white">Behavior timeline</h2>
              <div className="mt-5 h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={history.timeline || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                    <XAxis dataKey="timestamp" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)' }} />
                    <Line type="monotone" dataKey="risk_score" stroke="#f97316" dot={false} strokeWidth={2} />
                    <Line type="monotone" dataKey="session_duration" stroke="#3b82f6" dot={false} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-3xl bg-slate-800/70 border border-slate-700 p-6">
              <h2 className="text-xl font-semibold text-white">Recent flagged events</h2>
              <div className="mt-4 space-y-3">
                {(history.recent_anomalies || []).map((event, index) => (
                  <div key={index} className="rounded-2xl bg-slate-900/80 border border-slate-700 p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm text-slate-400">{new Date(event.timestamp).toLocaleString()}</p>
                        <p className="text-white font-medium">{event.attack_type || 'unknown'}</p>
                      </div>
                      <RiskBadge level={event.risk_level || 'low'} />
                    </div>
                    <p className="mt-3 text-slate-300">{(event.reasons || []).join(', ')}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-3xl bg-slate-800/70 border border-slate-700 p-10 text-slate-400">
            No history available.
          </div>
        )}
      </div>
    </div>
  );
};

export default EntityHistoryPage;
