import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Anomalies API
export const anomaliesAPI = {
  detect: (event) => apiClient.post('/anomalies/detect', event),
  detectBatch: (events) => apiClient.post('/anomalies/detect/batch', { events }),
  list: (page = 1, pageSize = 50, filters = {}) =>
    apiClient.get('/anomalies/list', { params: { page, page_size: pageSize, ...filters } }),
  getDetail: (anomalyId) => apiClient.get(`/anomalies/${anomalyId}`),
  getStatistics: () => apiClient.get('/anomalies/statistics'),
};

// Alerts API
export const alertsAPI = {
  list: (page = 1, pageSize = 50, filters = {}) =>
    apiClient.get('/alerts', { params: { page, page_size: pageSize, ...filters } }),
  getActive: (page = 1, pageSize = 50) =>
    apiClient.get('/alerts/active', { params: { page, page_size: pageSize } }),
  getDetail: (alertId) => apiClient.get(`/alerts/${alertId}`),
  acknowledge: (alertId, acknowledgedBy = 'system') =>
    apiClient.patch(`/alerts/${alertId}/acknowledge`, { acknowledged: true, acknowledged_by: acknowledgedBy }),
  getStatistics: () => apiClient.get('/alerts/statistics'),
};

// Analytics API
export const analyticsAPI = {
  getOverview: () => apiClient.get('/analytics/overview'),
  getRiskDistribution: () => apiClient.get('/analytics/risk-distribution'),
  getTimeSeries: (hours = 24) => apiClient.get('/analytics/time-series', { params: { hours } }),
  getTopResources: (limit = 10) => apiClient.get('/analytics/top-resources', { params: { limit } }),
  getTopLocations: (limit = 10) => apiClient.get('/analytics/top-locations', { params: { limit } }),
  getModelPerformance: () => apiClient.get('/analytics/model-performance'),
  getEntityRiskSummary: () => apiClient.get('/analytics/entity-risk-summary'),
};

// Entities API
export const entitiesAPI = {
  listUsers: (page = 1, pageSize = 50) =>
    apiClient.get('/entities/users', { params: { page, page_size: pageSize } }),
  listDevices: (page = 1, pageSize = 50) =>
    apiClient.get('/entities/devices', { params: { page, page_size: pageSize } }),
  getUserDetail: (userId) => apiClient.get(`/entities/users/${userId}`),
  getDeviceDetail: (deviceId) => apiClient.get(`/entities/devices/${deviceId}`),
  search: (q, entityType = null, limit = 20) =>
    apiClient.get('/entities/search', { params: { q, entity_type: entityType, limit } }),
};

// Models API
export const modelsAPI = {
  getInfo: () => apiClient.get('/models/info'),
  getStatus: () => apiClient.get('/models/status'),
  getPerformance: () => apiClient.get('/models/performance'),
};

// Health API
export const healthAPI = {
  check: () => apiClient.get('/health'),
  ready: () => apiClient.get('/health/ready'),
  live: () => apiClient.get('/health/live'),
};

export default apiClient;
