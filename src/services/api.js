import axios from 'axios';

// Base URL configuration
const API_BASE_URL = 'https://chemical-equipment-parameter-zw76.onrender.com/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// FIXED Interceptor (Do NOT send token for login & register)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');

  if (token && !config.url.includes("login") && !config.url.includes("register")) {
    config.headers.Authorization = `Token ${token}`;
  }

  return config;
}, (error) => Promise.reject(error));

/**
 * Login
 */
export const login = async (username, password) => {
  const response = await api.post('/login/', { username, password });
  const { token } = response.data;
  localStorage.setItem('token', token);
  return token;
};

/**
 * Register
 */
export const register = async (username, email, password) => {
  const response = await api.post('/register/', { username, email, password });
  return response.data;
};

/**
 * Logout
 */
export const logout = () => {
  localStorage.removeItem('token');
};

/**
 * Upload file
 */
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  return response.data;
};

/**
 * Get summary
 */
export const getSummary = async () => {
  const response = await api.get('/summary/');
  return response.data;
};

/**
 * Get history
 */
export const getHistory = async () => {
  const response = await api.get('/history/');
  return response.data;
};

/**
 * Download PDF
 */
export const downloadReport = async (id) => {
  const response = await api.get(`/report/${id}/`, {
    responseType: 'blob',
  });
  return response.data;
};

export default api;
