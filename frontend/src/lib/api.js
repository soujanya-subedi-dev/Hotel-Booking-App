import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api',
  timeout: 15000,
  headers: { 'Accept': 'application/json' }
});

// Attach JWT if present
api.interceptors.request.use((config) => {
  const t = localStorage.getItem('access_token');
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

// Normalize errors and handle 401 logout
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const status = err?.response?.status;
    if (status === 401) {
      // token invalid/expired -> clear and surface message
      localStorage.removeItem('access_token');
    }
    err.normalized = {
      status: status || 0,
      message: err?.response?.data?.error || err?.message || 'Request failed'
    };
    return Promise.reject(err);
  }
);
