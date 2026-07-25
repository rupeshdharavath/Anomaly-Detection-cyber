import React, { useEffect, useState } from 'react';
import { Search, Filter, Download } from 'lucide-react';
import AnomalyTable from '../components/AnomalyTable';
import RiskBadge from '../components/RiskBadge';
import { useStore } from '../store/store';

const RESOURCE_OPTIONS = [
  'Internal Server',
  'Finance DB',
  'Database',
  'Admin Portal',
  'Email Service',
  'Cloud Storage',
];

const LOCATION_OPTIONS = [
  'Bangalore',
  'US',
  'EU',
  'London',
  'Mumbai',
  'APAC',
];

const AUTH_OPTIONS = [
  'Password',
  'MFA',
  'Biometric',
  'API Key',
  'SSO',
];

const DEVICE_OPTIONS = [
  'Laptop',
  'Mobile',
  'Desktop',
  'Server',
  'Tablet',
];

const AnomaliesPage = () => {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [geoLocationChoice, setGeoLocationChoice] = useState('');
  const [customGeoLocation, setCustomGeoLocation] = useState('');
  const { fetchAnomalies, getAnomalyDetail, getAnomalyStats, anomalies, loading, selectedAnomaly } = useStore();
  const [stats, setStats] = useState(null);

  const updateFilter = (key, value) => {
    setPage(1);
    setFilters((prevFilters) => ({
      ...prevFilters,
      [key]: value || undefined,
    }));
  };

  const handleGeoLocationFilter = (value) => {
    setGeoLocationChoice(value);
    setCustomGeoLocation('');
    setPage(1);
    setFilters((prevFilters) => ({
      ...prevFilters,
      geo_location: value === 'Others' ? undefined : value || undefined,
    }));
  };

  useEffect(() => {
    loadAnomalies();
    loadStats();
  }, [page, filters]);

  const loadAnomalies = async () => {
    try {
      await fetchAnomalies(page, filters);
    } catch (err) {
      console.error('Error loading anomalies:', err);
    }
  };

  const loadStats = async () => {
    try {
      const data = await getAnomalyStats();
      setStats(data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const handleSearch = (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    // Filter locally or make API call
  };

  const handleAnomalyClick = async (anomaly) => {
    try {
      await getAnomalyDetail(anomaly.event_id);
    } catch (err) {
      console.error('Error loading anomaly detail:', err);
    }
  };

  return (
    <div className="min-h-screen bg-transparent text-slate-100">
        <div className="p-6 space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-white">Anomalies</h1>
            <p className="text-slate-400 mt-1">Detected and analyzed security anomalies</p>
          </div>

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4">
                <p className="text-slate-400 text-sm">Total Events</p>
                <p className="text-2xl font-bold text-white mt-1">{stats.total_events}</p>
              </div>
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4">
                <p className="text-slate-400 text-sm">Total Anomalies</p>
                <p className="text-2xl font-bold text-white mt-1">{stats.total_anomalies}</p>
              </div>
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4">
                <p className="text-slate-400 text-sm">Anomaly Rate</p>
                <p className="text-2xl font-bold text-white mt-1">{(stats.anomaly_rate * 100).toFixed(2)}%</p>
              </div>
            </div>
          )}

          {/* Filters */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4 space-y-4">
            <div className="flex gap-4 flex-wrap">
              <div className="flex-1 min-w-64 relative">
                <Search className="absolute left-3 top-3 text-slate-400" size={20} />
                <input
                  type="text"
                  placeholder="Search entity ID..."
                  value={searchTerm}
                  onChange={handleSearch}
                  className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <select
                onChange={(e) => updateFilter('risk_level', e.target.value)}
                className="px-4 py-2 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-blue-500"
              >
                <option value="">All Risk Levels</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>

              <select
                onChange={(e) => updateFilter('flagged_by', e.target.value)}
                className="px-4 py-2 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-blue-500"
              >
                <option value="">All Sources</option>
                <option value="baseline">Baseline</option>
                <option value="lstm">LSTM</option>
                <option value="both">Both</option>
              </select>

              <select
                onChange={(e) => updateFilter('resource_accessed', e.target.value)}
                className="px-4 py-2 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-blue-500"
              >
                <option value="">All Resources</option>
                {RESOURCE_OPTIONS.map((resource) => (
                  <option key={resource} value={resource}>
                    {resource}
                  </option>
                ))}
              </select>

              <div className="flex items-center gap-3">
                <select
                  value={geoLocationChoice}
                  onChange={(e) => handleGeoLocationFilter(e.target.value)}
                  className="px-4 py-2 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="">All Locations</option>
                  {LOCATION_OPTIONS.map((location) => (
                    <option key={location} value={location}>
                      {location}
                    </option>
                  ))}
                </select>
                {geoLocationChoice === 'Others' && (
                  <input
                    type="text"
                    value={customGeoLocation}
                    onChange={(e) => {
                      const value = e.target.value;
                      setCustomGeoLocation(value);
                      setPage(1);
                      setFilters((prevFilters) => ({
                        ...prevFilters,
                        geo_location: value || undefined,
                      }));
                    }}
                    placeholder="Type location manually"
                    className="px-4 py-2 bg-slate-900 border border-slate-700 rounded text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                )}
              </div>

              <select
                onChange={(e) => updateFilter('auth_method', e.target.value)}
                className="px-4 py-2 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-blue-500"
              >
                <option value="">All Auth Methods</option>
                {AUTH_OPTIONS.map((method) => (
                  <option key={method} value={method}>
                    {method}
                  </option>
                ))}
              </select>

              <select
                onChange={(e) => updateFilter('device_type', e.target.value)}
                className="px-4 py-2 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-blue-500"
              >
                <option value="">All Device Types</option>
                {DEVICE_OPTIONS.map((device) => (
                  <option key={device} value={device}>
                    {device}
                  </option>
                ))}
              </select>

              <button className="px-4 py-2 bg-blue-500/20 border border-blue-500/50 text-blue-300 hover:bg-blue-500/30 rounded flex items-center gap-2 transition">
                <Download size={20} />
                Export
              </button>
            </div>
          </div>

          {/* Anomalies Table */}
          <AnomalyTable
            anomalies={anomalies}
            loading={loading}
            onRowClick={handleAnomalyClick}
          />

          {/* Detail View */}
          {selectedAnomaly && (
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Anomaly Detail</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <p className="text-slate-400 text-sm">Entity ID</p>
                    <p className="text-white font-medium">{selectedAnomaly.entity_id}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Risk Level</p>
                    <div className="mt-2">
                      <RiskBadge level={selectedAnomaly.risk_level} />
                    </div>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Confidence Score</p>
                    <p className="text-white font-medium">{(selectedAnomaly.confidence * 100).toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Flagged By</p>
                    <p className="text-white font-medium capitalize">{selectedAnomaly.flagged_by}</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <p className="text-slate-400 text-sm">Resource Accessed</p>
                    <p className="text-white font-medium">{selectedAnomaly.resource_accessed}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Location</p>
                    <p className="text-white font-medium">{selectedAnomaly.geo_location}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Authentication Method</p>
                    <p className="text-white font-medium">{selectedAnomaly.auth_method}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Device Type</p>
                    <p className="text-white font-medium">{selectedAnomaly.device_type}</p>
                  </div>
                </div>
              </div>

              {selectedAnomaly.reasons && selectedAnomaly.reasons.length > 0 && (
                <div className="mt-6 pt-6 border-t border-slate-700">
                  <p className="text-slate-400 text-sm mb-3">Detection Reasons</p>
                  <ul className="space-y-2">
                    {selectedAnomaly.reasons.map((reason, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-slate-300 text-sm">
                        <span className="text-blue-400 mt-1">•</span>
                        <span>{reason.reason || reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Pagination */}
          <div className="flex justify-between items-center">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-slate-800 border border-slate-700 rounded text-white disabled:opacity-50 hover:bg-slate-700 transition"
            >
              Previous
            </button>
            <span className="text-slate-400">Page {page}</span>
            <button
              onClick={() => setPage(page + 1)}
              className="px-4 py-2 bg-slate-800 border border-slate-700 rounded text-white hover:bg-slate-700 transition"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnomaliesPage;
