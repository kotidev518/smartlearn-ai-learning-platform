import api from './api';

export const authService = {
  getProfile: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  register: async (name, initial_level) => {
    const response = await api.post('/auth/register', {
      name,
      initial_level
    });
    return response.data;
  }
};
