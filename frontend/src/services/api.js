import axios from 'axios';

// Get the API URL from environment variables or use default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

console.log('API URL:', API_URL); // Debug log to verify the API URL

// Create an axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include credentials in cross-origin requests
});

// Add a request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    // Get auth token from localStorage
    const token = localStorage.getItem('auth_token');

    // Log request details for debugging
    console.log(`API Request [${config.method.toUpperCase()} ${config.url}]:`, {
      url: config.url,
      method: config.method,
      data: config.data,
      hasToken: !!token
    });

    // Add authorization header if token exists
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    // Log successful responses for debugging
    console.log(`API Response [${response.config.method.toUpperCase()} ${response.config.url}]:`, response.data);
    return response;
  },
  (error) => {
    // Log detailed error information
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method?.toUpperCase(),
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    });

    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      // Clear local storage and redirect to login if not already there
      if (window.location.pathname !== '/signin') {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        window.location.href = '/signin';
      }
    }

    // Handle CORS errors
    if (error.message === 'Network Error') {
      console.error('Network Error: This might be a CORS issue or the server is not running');
    }

    return Promise.reject(error);
  }
);

export default api;
