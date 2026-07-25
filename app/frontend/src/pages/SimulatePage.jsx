import React, { useState } from 'react';
import { useStore } from '../store/store';
import RiskBadge from '../components/RiskBadge';

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
  'Chennai',
  'Hyderabad',
  'Mumbai',
  'Pune',
  'Others',
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

const SimulatePage = () => {
  const { runSimulation } = useStore();
  const [form, setForm] = useState({
    event_id: 'EVT-001',
    timestamp: new Date().toISOString().slice(0, 19),
    entity_id: 'U0001',
    resource_accessed: 'Internal Server',
    geo_location: 'Bangalore',
    auth_method: 'Password',
    device_type: 'Laptop',
    failed_login_attempts: 0,
    session_duration: 120,
    custom_geo_location: '',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => {
      if (name === 'geo_location' && value !== 'Others') {
        return {
          ...prev,
          geo_location: value,
          custom_geo_location: '',
        };
      }

      return {
        ...prev,
        [name]:
          name === 'failed_login_attempts' || name === 'session_duration'
            ? Number(value)
            : value,
      };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const requestData = {
        ...form,
        geo_location:
          form.geo_location === 'Others' && form.custom_geo_location
            ? form.custom_geo_location
            : form.geo_location,
        failed_login_attempts: Number(form.failed_login_attempts),
        session_duration: Number(form.session_duration),
      };
      const response = await runSimulation(requestData);
      setResult(response);
    } catch (err) {
      setError(err.message || 'Simulation failed');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const formatAttackType = (type) => {
    const map = {
      brute_force: 'Brute Force',
      impossible_travel: 'Impossible Travel',
      lateral_movement: 'Lateral Movement',
      credential_stuffing: 'Credential Stuffing',
      long_session: 'Long Session',
      unknown: 'Unknown',
    };
    return map[type] || type || 'Unknown';
  };

  const safeResult = {
    risk_score: result?.risk_score ?? 0,
    confidence: result?.confidence ?? 0,
    risk_level: result?.risk_level ?? 'low',
    is_anomaly: result?.is_anomaly ?? false,
    attack_type: result?.attack_type ?? 'unknown',
    reasons: Array.isArray(result?.reasons) ? result.reasons : [],
    entity_id: result?.entity_id ?? form.entity_id,
    resource_accessed: result?.resource_accessed ?? form.resource_accessed,
    geo_location: result?.geo_location ?? form.geo_location,
    auth_method: result?.auth_method ?? form.auth_method,
    device_type: result?.device_type ?? form.device_type,
    failed_login_attempts: result?.failed_login_attempts ?? form.failed_login_attempts,
    session_duration: result?.session_duration ?? form.session_duration,
  };

  return (
    <div className="min-h-screen bg-transparent text-slate-100 p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Live Simulation</h1>
          <p className="text-slate-300 mt-2">
            Test a hypothetical event and see the analyst-facing risk verdict instantly.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="bg-black text-white border border-slate-300/20 rounded-3xl shadow-xl p-6 hover:shadow-2xl transition">
            <h2 className="text-xl font-semibold mb-4">Incident Scenario</h2>
            <form className="space-y-4" onSubmit={handleSubmit}>
              <label className="block">
                <span className="text-sm text-slate-300">Entity ID</span>
                <input
                  type="text"
                  name="entity_id"
                  value={form.entity_id}
                  onChange={handleChange}
                  className="mt-2 w-full rounded-3xl border border-slate-700 bg-black text-white px-4 py-3 focus:border-black focus:outline-none"
                />
              </label>

              <label className="block">
                <span className="text-sm text-slate-300">Resource Accessed</span>
                <select
                  name="resource_accessed"
                  value={form.resource_accessed}
                  onChange={handleChange}
                  className="mt-2 w-full rounded-3xl border border-slate-700 bg-black text-white px-4 py-3 focus:border-black focus:outline-none"
                >
                  {RESOURCE_OPTIONS.map((option) => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </label>

              <label className="block">
                <span className="text-sm text-slate-300">Geo Location</span>
                <select
                  name="geo_location"
                  value={form.geo_location}
                  onChange={handleChange}
                  className="mt-2 w-full rounded-3xl border border-slate-700 bg-black text-white px-4 py-3 focus:border-black focus:outline-none"
                >
                  {LOCATION_OPTIONS.map((option) => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </label>

              {form.geo_location === 'Others' && (
                <label className="block">
                  <span className="text-sm text-slate-300">Enter Location</span>
                  <input
                    type="text"
                    name="custom_geo_location"
                    value={form.custom_geo_location}
                    onChange={handleChange}
                    placeholder="Type location manually"
                    className="mt-2 w-full rounded-3xl border border-slate-700 bg-black text-white px-4 py-3 focus:border-black focus:outline-none"
                  />
                </label>
              )}

              <label className="block">
                <span className="text-sm text-slate-300">Auth Method</span>
                <select
                  name="auth_method"
                  value={form.auth_method}
                  onChange={handleChange}
                  className="mt-2 w-full rounded-3xl border border-slate-700 bg-black text-white px-4 py-3 focus:border-black focus:outline-none"
                >
                  {AUTH_OPTIONS.map((option) => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </label>

              <label className="block">
                <span className="text-sm text-slate-300">Device Type</span>
                <select
                  name="device_type"
                  value={form.device_type}
                  onChange={handleChange}
                  className="mt-2 w-full rounded-3xl border border-slate-700 bg-black text-white px-4 py-3 focus:border-black focus:outline-none"
                >
                  {DEVICE_OPTIONS.map((option) => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </label>

              <div className="grid grid-cols-2 gap-4">
                <label className="block">
                  <span className="text-sm text-slate-300">Failed Login Attempts</span>
                  <input
                    type="number"
                    name="failed_login_attempts"
                    value={form.failed_login_attempts}
                    onChange={handleChange}
                    className="mt-2 w-full rounded-3xl border border-slate-700 bg-black text-white px-4 py-3 outline-none focus:border-black"
                  />
                </label>
                <label className="block">
                  <span className="text-sm text-slate-300">Session Duration (s)</span>
                  <input
                    type="number"
                    name="session_duration"
                    value={form.session_duration}
                    onChange={handleChange}
                    className="mt-2 w-full rounded-3xl border border-slate-700 bg-black text-white px-4 py-3 outline-none focus:border-black"
                  />
                </label>
              </div>

              <button
                type="submit"
                className="mt-4 inline-flex items-center justify-center rounded-lg bg-blue-500 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-400 transition"
              >
                {loading ? 'Analyzing…' : 'Analyze Event'}
              </button>
            </form>
          </div>

          <div className="bg-slate-800/70 border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-4">Analysis result</h2>
            {error && (
              <div className="rounded-xl bg-red-500/10 border border-red-500/20 p-4 text-red-200">
                {error}
              </div>
            )}

            {!result && !error && (
              <div className="text-slate-400">Run a simulation to see risk score, attack type, and contributing factors.</div>
            )}

            {result && (
              <div className="space-y-4">
                <div className="rounded-3xl bg-slate-900/70 p-5 border border-slate-700">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-slate-400 uppercase text-xs tracking-[0.2em]">Risk score</p>
                      <p className="mt-2 text-4xl font-bold text-white">{safeResult.risk_score.toFixed(2)}</p>
                    </div>
                    <RiskBadge level={safeResult.risk_level} />
                  </div>
                  <p className="mt-4 text-slate-300">{safeResult.is_anomaly ? 'Attack detected' : 'Normal behavior'}</p>
                </div>

                <div className="rounded-3xl bg-slate-900/70 p-5 border border-slate-700">
                  <h3 className="text-sm font-semibold text-slate-300">Prediction</h3>
                  <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <div>
                      <p className="text-slate-400 text-xs uppercase">Attack Type</p>
                      <p className="text-white mt-1">{formatAttackType(safeResult.attack_type)}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-xs uppercase">Confidence</p>
                      <p className="text-white mt-1">{(safeResult.confidence * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                </div>

                <div className="rounded-3xl bg-slate-900/70 p-5 border border-slate-700">
                  <h3 className="text-sm font-semibold text-slate-300">Contributing factors</h3>
                  <ul className="mt-4 space-y-3">
                    {safeResult.reasons.map((reason, index) => (
                      <li key={index} className="rounded-2xl bg-slate-800/80 border border-slate-700 p-4 text-slate-100">
                        {reason}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="rounded-3xl bg-slate-900/70 p-5 border border-slate-700">
                  <h3 className="text-sm font-semibold text-slate-300">Raw event details</h3>
                  <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                    {[
                      ['Entity', safeResult.entity_id],
                      ['Resource', safeResult.resource_accessed],
                      ['Location', safeResult.geo_location],
                      ['Device', safeResult.device_type],
                      ['Auth method', safeResult.auth_method],
                      ['Failed logins', safeResult.failed_login_attempts],
                      ['Session duration', `${safeResult.session_duration}s`],
                    ].map(([label, value]) => (
                      <div key={label} className="text-slate-300">
                        <p className="text-xs uppercase text-slate-500">{label}</p>
                        <p className="mt-1 text-white">{value ?? 'n/a'}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimulatePage;
