import { create } from 'zustand';
import { anomaliesAPI, alertsAPI, analyticsAPI, entitiesAPI, modelsAPI } from '../api/client';

export const useStore = create((set, get) => ({
  // State
  anomalies: [],
  alerts: [],
  activeAlerts: [],
  analytics: null,
  entities: { users: [], devices: [] },
  models: null,
  loading: false,
  error: null,
  selectedAnomaly: null,
  selectedAlert: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Anomalies
  fetchAnomalies: async (page = 1, filters = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await anomaliesAPI.list(page, 50, filters);
      set({ anomalies: response.data.data || [], loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  getAnomalyDetail: async (anomalyId) => {
    set({ loading: true, error: null });
    try {
      const response = await anomaliesAPI.getDetail(anomalyId);
      set({ selectedAnomaly: response.data, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  getAlertDetail: async (alertId) => {
    set({ loading: true, error: null });
    try {
      const response = await alertsAPI.getDetail(alertId);
      const alert = response.data;
      let relatedAnomaly = null;
      if (alert.anomaly_id) {
        try {
          const anomalyResponse = await anomaliesAPI.getDetail(alert.anomaly_id);
          relatedAnomaly = anomalyResponse.data;
        } catch (err) {
          console.warn('Related anomaly detail not available', err);
        }
      }
      set({ selectedAlert: { alert, relatedAnomaly }, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  getAnomalyStats: async () => {
    try {
      const response = await anomaliesAPI.getStatistics();
      return response.data;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  // Alerts
  fetchAlerts: async (page = 1) => {
    set({ loading: true, error: null });
    try {
      const response = await alertsAPI.list(page);
      set({ alerts: response.data.data || [], loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  fetchActiveAlerts: async (page = 1) => {
    set({ loading: true, error: null });
    try {
      const response = await alertsAPI.getActive(page);
      set({ activeAlerts: response.data.data || [], loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  runSimulation: async (eventData) => {
    set({ loading: true, error: null });
    try {
      const response = await anomaliesAPI.detect(eventData);
      set({ loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  acknowledgeAlert: async (alertId, user = 'analyst') => {
    set({ loading: true, error: null });
    try {
      const response = await alertsAPI.acknowledge(alertId, user);
      // Refresh alerts
      await get().fetchActiveAlerts();
      set({ loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // Analytics
  fetchAnalytics: async () => {
    set({ loading: true, error: null });
    try {
      const overview = await analyticsAPI.getOverview();
      const timeSeries = await analyticsAPI.getTimeSeries();
      const performance = await analyticsAPI.getModelPerformance();

      // Normalize time series to always be an object with `points` array
      const tsPayload = timeSeries?.data?.data ?? timeSeries?.data;
      let tsPoints = [];
      if (Array.isArray(tsPayload)) {
        tsPoints = tsPayload;
      } else if (tsPayload && Array.isArray(tsPayload.points)) {
        tsPoints = tsPayload.points;
      }

      // Ensure each point has expected keys and sort by timestamp
      const normalizedPoints = (tsPoints || [])
        .map((p) => ({
          timestamp: p.timestamp || p.hour || p.hour?.toString?.() || p["hour"] || null,
          value: typeof p.value === 'number' ? p.value : Number(p.count || 0),
          risk_score: typeof p.risk_score === 'number' ? p.risk_score : Number(p.risk_score || 0),
        }))
        .filter((p) => p.timestamp !== null)
        .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

      set({
        analytics: {
          overview: overview.data,
          timeSeries: { points: normalizedPoints },
          performance: performance.data,
        },
        loading: false,
      });
      return { overview, timeSeries, performance };
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // Entities
  fetchUsers: async (page = 1) => {
    set({ loading: true, error: null });
    try {
      const response = await entitiesAPI.listUsers(page);
      set((state) => ({
        entities: { ...state.entities, users: response.data.data || [] },
        loading: false,
      }));
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  fetchDevices: async (page = 1) => {
    set({ loading: true, error: null });
    try {
      const response = await entitiesAPI.listDevices(page);
      set((state) => ({
        entities: { ...state.entities, devices: response.data.data || [] },
        loading: false,
      }));
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  searchEntities: async (q, type = null) => {
    set({ loading: true, error: null });
    try {
      const response = await entitiesAPI.search(q, type);
      set({ loading: false });
      return response.data.data || [];
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // Models
  fetchModelsInfo: async () => {
    set({ loading: true, error: null });
    try {
      const response = await modelsAPI.getInfo();
      set({ models: response.data, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },
}));
