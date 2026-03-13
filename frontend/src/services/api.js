import axios from 'axios';

const getBaseURL = () => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL.replace(/\/+$/, '');
  }
  if (process.env.REACT_APP_BACKEND_URL) {
    const baseUrl = process.env.REACT_APP_BACKEND_URL.replace(/\/+$/, '');
    return `${baseUrl}/api`;
  }
  return 'http://localhost:8000/api';
};

const API_URL = getBaseURL();

const api = axios.create({
  baseURL: API_URL,
});

export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export default api;
