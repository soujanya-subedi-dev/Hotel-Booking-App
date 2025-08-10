import axios from 'axios';
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api',
});
api.interceptors.request.use((config) => {
  const t = localStorage.getItem('access_token');
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});
