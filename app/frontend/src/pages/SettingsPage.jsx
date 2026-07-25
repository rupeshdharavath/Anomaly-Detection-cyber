import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, RefreshCw, Download, Upload } from 'lucide-react';
import { useStore } from '../store/store';

const SettingsPage = () => {
  const { fetchModelsInfo, models, loading } = useStore();
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchModelsInfo();
  }, []);

  const handleRefreshModels = async () => {
    setRefreshing(true);
    try {
      await fetchModelsInfo();
    } catch (err) {
      console.error('Error refreshing models:', err);
    }
    setRefreshing(false);
  };

  return (
    <div className="min-h-screen bg-transparent text-slate-100">
      <div className="p-6 space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-2">
              <SettingsIcon size={32} />
              Settings
            </h1>
            <p className="text-slate-300 mt-1">System configuration and model management</p>
          </div>

          {/* Model Information */}
          <div className="space-y-6">
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center justify-between">
                Detection Models
                <button
                  onClick={handleRefreshModels}
                  disabled={refreshing || loading}
                  className="p-2 bg-blue-500/20 border border-blue-500/50 text-blue-300 hover:bg-blue-500/30 rounded transition disabled:opacity-50 flex items-center gap-2"
                >
                  <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
                  Refresh
                </button>
              </h2>

              {models ? (
                // Support both detailed models object and simple `models` array from mock
                (models.baseline || models.lstm || models.ensemble_config) ? (
                  <div className="space-y-6">
                  {/* Baseline Model */}
                  <div className="border-l-4 border-blue-500 pl-4">
                    <h3 className="font-semibold text-white flex items-center gap-2">
                      {models.baseline.name}
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          models.baseline.status === 'loaded'
                            ? 'bg-green-500/20 text-green-300'
                            : 'bg-red-500/20 text-red-300'
                        }`}
                      >
                        {models.baseline.status}
                      </span>
                    </h3>
                    <p className="text-slate-400 text-sm mt-1">
                      Type: {models.baseline.parameters.type}
                    </p>
                    <p className="text-slate-400 text-sm">
                      Profiles: {models.baseline.parameters.profiles_count}
                    </p>
                    <div className="mt-2 text-sm">
                      <p className="text-slate-400">Detection Methods:</p>
                      <ul className="mt-1 space-y-1">
                        {models.baseline.parameters.detection_methods.map((method, idx) => (
                          <li key={idx} className="text-slate-300 ml-4">• {method}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* LSTM Model */}
                  <div className="border-l-4 border-purple-500 pl-4">
                    <h3 className="font-semibold text-white flex items-center gap-2">
                      {models.lstm.name}
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          models.lstm.status === 'loaded'
                            ? 'bg-green-500/20 text-green-300'
                            : 'bg-yellow-500/20 text-yellow-300'
                        }`}
                      >
                        {models.lstm.status}
                      </span>
                    </h3>
                    <p className="text-slate-400 text-sm mt-1">
                      Architecture: {models.lstm.parameters.architecture}
                    </p>
                    <p className="text-slate-400 text-sm">
                      Layers: {models.lstm.parameters.layers.length}
                    </p>
                    <p className="text-slate-400 text-sm">
                      Epochs: {models.lstm.parameters.epochs} | Batch Size: {models.lstm.parameters.batch_size}
                    </p>
                  </div>

                  {/* Ensemble Config */}
                  <div className="border-l-4 border-green-500 pl-4">
                    <h3 className="font-semibold text-white">Ensemble Configuration</h3>
                    <div className="mt-2 space-y-1 text-sm text-slate-300">
                      <p>
                        Baseline Weight: <span className="font-mono">{models.ensemble_config.baseline_weight * 100}%</span>
                      </p>
                      <p>
                        LSTM Weight: <span className="font-mono">{models.ensemble_config.lstm_weight * 100}%</span>
                      </p>
                      <p>
                        Anomaly Threshold: <span className="font-mono">{models.ensemble_config.anomaly_threshold}</span>
                      </p>
                      <p>
                        Decision Logic: <span className="font-mono">{models.ensemble_config.decision_logic}</span>
                      </p>
                    </div>
                  </div>
                </div>
                ) : (
                  // Fallback: show simple list if backend returned an array under `models.models` or `models` array
                  <div>
                    {Array.isArray(models.models) || Array.isArray(models) ? (
                      <ul className="text-slate-300 space-y-2">
                        {(Array.isArray(models.models) ? models.models : models).map((m, i) => (
                          <li key={i} className="bg-slate-800/30 p-2 rounded">
                            <div className="flex items-center justify-between">
                              <div>
                                <div className="font-semibold">{m.name || m}</div>
                                <div className="text-slate-400 text-sm">version: {m.version || 'n/a'}</div>
                              </div>
                              <div className="text-sm text-slate-300">loaded: {String(m.loaded)}</div>
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-slate-400">No model information available.</p>
                    )}
                  </div>
                )
              ) : null}
            </div>

            {/* Data Export */}
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Data & Export</h2>
              <div className="space-y-3">
                <button className="w-full px-4 py-2 bg-blue-500/20 border border-blue-500/50 text-blue-300 hover:bg-blue-500/30 rounded flex items-center justify-center gap-2 transition">
                  <Download size={18} />
                  Export Anomalies
                </button>
                <button className="w-full px-4 py-2 bg-blue-500/20 border border-blue-500/50 text-blue-300 hover:bg-blue-500/30 rounded flex items-center justify-center gap-2 transition">
                  <Download size={18} />
                  Export Alerts
                </button>
                <button className="w-full px-4 py-2 bg-blue-500/20 border border-blue-500/50 text-blue-300 hover:bg-blue-500/30 rounded flex items-center justify-center gap-2 transition">
                  <Download size={18} />
                  Export Analytics
                </button>
              </div>
            </div>

            {/* System Information */}
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-4">System Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-slate-400">API Version</p>
                  <p className="text-white font-mono">1.0.0</p>
                </div>
                <div>
                  <p className="text-slate-400">Frontend Version</p>
                  <p className="text-white font-mono">1.0.0</p>
                </div>
                <div>
                  <p className="text-slate-400">Last Updated</p>
                  <p className="text-white">{new Date().toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-slate-400">Status</p>
                  <p className="text-green-400 font-semibold">Operational</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
