import React, { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { AlertTriangle, TrendingUp, Shield, Activity, Zap } from 'lucide-react';
import StatCard from '../components/StatCard';
import AlertCard from '../components/AlertCard';
import AlertDetail from '../components/AlertDetail';
import AnomalyTable from '../components/AnomalyTable';
import { useStore } from '../store/store';

const Dashboard = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { fetchAnalytics, fetchAnomalies, fetchActiveAlerts, acknowledgeAlert, getAlertDetail, loading } = useStore();
  const { analytics, anomalies, activeAlerts, selectedAlert } = useStore();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      await Promise.all([fetchAnalytics(), fetchAnomalies(1, { limit: 10 }), fetchActiveAlerts(1)]);
    } catch (err) {
      console.error('Error loading dashboard:', err);
    }
  };

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await acknowledgeAlert(alertId);
    } catch (err) {
      console.error('Error acknowledging alert:', err);
    }
  };

  const handleAlertClick = async (alertId) => {
    try {
      await getAlertDetail(alertId);
    } catch (err) {
      console.error('Error fetching alert detail:', err);
    }
  };

  const riskData = analytics?.overview?.data?.risk_distribution
    ? Object.entries(analytics.overview.data.risk_distribution).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value,
      }))
    : [];

  const colors = ['#10b981', '#f59e0b', '#ef4444', '#dc2626'];

  return (
    <div className="min-h-screen bg-transparent text-slate-100">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Shield size={32} className="text-blue-400" />
            Security Operations Center
          </h1>
          <p className="text-slate-300 mt-1">Real-time anomaly detection and threat monitoring</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Events"
            value={analytics?.overview?.data?.total_events ? analytics.overview.data.total_events.toLocaleString() : '0'}
            icon={Activity}
            trend="+5.2% today"
            color="blue"
          />
          <StatCard
            title="Anomalies Detected"
            value={analytics?.overview?.data?.total_anomalies || '0'}
            icon={AlertTriangle}
            trend={`${(analytics?.overview?.data?.anomaly_rate * 100).toFixed(2)}% rate`}
            color="red"
          />
          <StatCard
            title="Active Alerts"
            value={activeAlerts?.length || '0'}
            icon={Zap}
            trend="Requires attention"
            color="yellow"
          />
          <StatCard
            title="System Status"
            value="Operational"
            icon={TrendingUp}
            trend="All systems healthy"
            color="green"
          />
        </div>

        {/* Charts and Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-black text-white border border-slate-300/20 rounded-3xl shadow-xl p-6 hover:shadow-2xl transition">
            <h2 className="text-lg font-semibold text-white mb-4">Anomalies Over Time</h2>
            <ResponsiveContainer width="100%" height={300}>
              {(() => {
                const ts = analytics?.timeSeries;
                const points = Array.isArray(ts) ? ts : ts?.points || [];
                // Debug: log points when available
                if (points && points.length > 0) {
                  // eslint-disable-next-line no-console
                  console.debug('Anomalies time series points:', points);
                  return (
                    <LineChart data={points}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,116,139,0.2)" />
                      <XAxis dataKey="timestamp" stroke="rgb(148,163,184)" />
                      <YAxis stroke="rgb(148,163,184)" />
                      <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.8)', border: '1px solid rgba(71,85,105,0.5)' }} />
                      <Line type="monotone" dataKey="value" stroke="#3b82f6" dot={false} />
                    </LineChart>
                  );
                }

                return (
                  <div className="flex items-center justify-center h-full text-slate-400">
                    No time-series data available
                  </div>
                );
              })()}
            </ResponsiveContainer>
          </div>

          <div className="bg-black text-white border border-slate-300/20 rounded-3xl shadow-xl p-6 hover:shadow-2xl transition">
            <h2 className="text-lg font-semibold text-white mb-4">Risk Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {colors.map((color, index) => (
                    <Cell key={`cell-${index}`} fill={color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Active Alerts */}
        <div>
          <h2 className="text-lg font-semibold text-white mb-4">Active Alerts</h2>
          <div className="space-y-3">
            {activeAlerts && activeAlerts.length > 0 ? (
              activeAlerts.slice(0, 5).map((alert) => (
                <AlertCard
                  key={alert.alert_id}
                  alert={alert}
                  onAcknowledge={handleAcknowledgeAlert}
                  onClick={() => handleAlertClick(alert.alert_id)}
                />
              ))
            ) : (
              <div className="bg-black text-white border border-slate-300/20 rounded-3xl p-4 text-center shadow-lg">
                No active alerts
              </div>
            )}
          </div>
        </div>

        {selectedAlert && selectedAlert.alert && (
          <AlertDetail selectedAlert={selectedAlert} />
        )}

        <div>
          <h2 className="text-lg font-semibold text-white mb-4">Recent Anomalies</h2>
          <AnomalyTable anomalies={anomalies} loading={loading} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
