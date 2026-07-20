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
<<<<<<< HEAD
  getNextRecommendation: async (courseId) => {
    const params = courseId ? { course_id: courseId } : {};
    const response = await api.get('/recommendations/next-video', { params });
=======
  getNextRecommendation: async () => {
    const response = await api.get('/recommendations/next-video');
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
    return response.data;
  },
  getOverallProgress: async () => {
      const response = await api.get('/analytics/progress');
      return response.data;
  }
}
