import React, { useEffect, useState } from 'react';
import { CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AlertCard from '../components/AlertCard';
import { useStore } from '../store/store';

const AlertsPage = () => {
  const [activeTab, setActiveTab] = useState('active');
  const navigate = useNavigate();
  const { fetchActiveAlerts, fetchAlerts, acknowledgeAlert, activeAlerts, alerts, loading } = useStore();

  useEffect(() => {
    loadAlerts();
  }, [activeTab]);

  const loadAlerts = async () => {
    try {
      if (activeTab === 'active') {
        await fetchActiveAlerts(1);
      } else {
        await fetchAlerts(1);
      }
    } catch (err) {
      console.error('Error loading alerts:', err);
    }
  };

  const handleAcknowledge = async (alertId) => {
    try {
      await acknowledgeAlert(alertId);
    } catch (err) {
      console.error('Error acknowledging alert:', err);
    }
  };

  const handleAlertClick = (alertId) => {
    navigate(`/alerts/${alertId}`);
  };

  const displayAlerts = activeTab === 'active' ? activeAlerts : alerts;

  return (
    <div className="min-h-screen bg-transparent text-slate-100">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-white">Alerts</h1>
          <p className="text-slate-300 mt-1">Security alerts and notifications</p>
        </div>

        {/* Tabs */}
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between border-b border-slate-700 pb-4">
          <div className="flex gap-4 overflow-x-auto">
            <button
              onClick={() => setActiveTab('active')}
              className={`px-4 py-3 font-medium border-b-2 transition ${
                activeTab === 'active'
                  ? 'text-blue-400 border-blue-500'
                  : 'text-slate-400 border-transparent hover:text-slate-300'
              }`}
            >
              Active ({activeAlerts?.length || 0})
            </button>
            <button
              onClick={() => setActiveTab('all')}
              className={`px-4 py-3 font-medium border-b-2 transition ${
                activeTab === 'all'
                  ? 'text-blue-400 border-blue-500'
                  : 'text-slate-400 border-transparent hover:text-slate-300'
              }`}
            >
              All ({alerts?.length || 0})
            </button>
          </div>
          <div className="text-slate-400 text-sm">
            {displayAlerts?.length || 0} alerts loaded • click any alert for full details
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.45fr_0.95fr]">
          <div className="space-y-3">
            {loading ? (
              <div className="flex justify-center py-12">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent mx-auto mb-2"></div>
                  <p className="text-slate-600">Loading alerts...</p>
                </div>
              </div>
            ) : displayAlerts && displayAlerts.length > 0 ? (
              displayAlerts.map((alert) => (
                <AlertCard
                  key={alert.alert_id}
                  alert={alert}
                  onAcknowledge={handleAcknowledge}
                  onClick={() => handleAlertClick(alert.alert_id)}
                />
              ))
            ) : (
              <div className="bg-black text-white border border-slate-300/20 rounded-3xl p-12 text-center shadow-xl">
                <CheckCircle size={48} className="mx-auto text-green-400 mb-4 opacity-50" />
                <p className="text-slate-200">No alerts to display</p>
              </div>
            )}
          </div>

          <div className="space-y-4">
              <div className="bg-slate-900/80 border border-slate-700 rounded-3xl p-6 text-slate-300 shadow-xl">
                <p className="text-lg font-semibold text-white mb-3">Alert details dashboard</p>
                <p className="leading-7">
                  Click any alert to open the full alert dashboard route and inspect every field in a dedicated view.
                </p>
              </div>
            </div>
          </div>

        {displayAlerts && displayAlerts.length > 0 && (
          <div className="bg-black text-white border border-slate-300/20 rounded-3xl shadow-xl p-6 hover:shadow-2xl transition">
            <h3 className="text-lg font-semibold text-white mb-4">Alert Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-slate-400 text-sm">Total Alerts</p>
                <p className="text-2xl font-bold text-white mt-1">{displayAlerts.length}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Critical</p>
                <p className="text-2xl font-bold text-red-400 mt-1">
                  {displayAlerts.filter((a) => a.severity === 'critical').length}
                </p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Action Required</p>
                <p className="text-2xl font-bold text-orange-400 mt-1">
                  {displayAlerts.filter((a) => a.action_required && !a.acknowledged).length}
                </p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Acknowledged</p>
                <p className="text-2xl font-bold text-green-400 mt-1">
                  {displayAlerts.filter((a) => a.acknowledged).length}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertsPage;
