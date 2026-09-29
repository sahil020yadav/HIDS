// Centralized API layer. Every page calls into these functions instead of
// calling fetch() directly.

const API_BASE = 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('hids_token');
}

function getUser() {
  const raw = localStorage.getItem('hids_user');
  return raw ? JSON.parse(raw) : null;
}

function clearSession() {
  localStorage.removeItem('hids_token');
  localStorage.removeItem('hids_user');
}

async function apiRequest(path, { method = 'GET', body = null, isForm = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (body && !isForm) headers['Content-Type'] = 'application/json';

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
  });

  if (res.status === 401) {
    clearSession();
    if (!location.pathname.endsWith('login.html')) {
      location.href = 'login.html';
    }
    throw new Error('Unauthorized');
  }

  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }

  if (!res.ok) {
    const detail = (data && (data.detail || JSON.stringify(data))) || `Request failed (${res.status})`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }

  return data;
}

// ---- Auth -------------------------------------------------------------
const registerUser = (payload) => apiRequest('/api/auth/register', { method: 'POST', body: payload });
const loginUser = (payload) => apiRequest('/api/auth/login', { method: 'POST', body: payload });

// ---- Model / Prediction -------------------------------------------------
const getModelInfo = () => apiRequest('/api/model/info');
const predict = (values) => apiRequest('/api/predict', { method: 'POST', body: { values } });
const getPredictions = (limit = 100) => apiRequest(`/api/predictions?limit=${limit}`);
const getPredictionById = (id) => apiRequest(`/api/predictions/${id}`);

// ---- Dashboard / Analytics / Logs ----------------------------------------
const getDashboardStats = () => apiRequest('/api/dashboard/stats');
const getAnalytics = () => apiRequest('/api/analytics');
const uploadDatasetSummary = (file) => {
  const form = new FormData();
  form.append('file', file);
  return apiRequest('/api/analytics/dataset-summary', { method: 'POST', body: form, isForm: true });
};
const getLogs = (limit = 200) => apiRequest(`/api/logs?limit=${limit}`);