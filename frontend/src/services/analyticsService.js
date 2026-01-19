import api from './api';

export const analyticsService = {
  getDashboardData: async () => {
      const [recRes, progRes] = await Promise.all([
        api.get('/recommendations/next-video'),
        api.get('/analytics/progress')
      ]);
      return {
          recommendation: recRes.data,
          progress: progRes.data
      };
  },
  getMasteryScores: async () => {
      const response = await api.get('/analytics/mastery');
      return response.data;
  },
  getNextRecommendation: async () => {
    const response = await api.get('/recommendations/next-video');
    return response.data;
  },
  getOverallProgress: async () => {
      const response = await api.get('/analytics/progress');
      return response.data;
  }
}
