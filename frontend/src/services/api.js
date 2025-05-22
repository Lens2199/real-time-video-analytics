import axios from 'axios';

// API base URL - automatically switches between development and production
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://video-analysis-api-vt2g.onrender.com/api'  // Your deployed backend
  : 'http://localhost:8000/api';

// Create axios instance with better error handling
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Add response interceptor for better error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Handle specific error cases
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout - please try again');
    } else if (error.response?.status === 404) {
      throw new Error('Resource not found');
    } else if (error.response?.status >= 500) {
      throw new Error('Server error - please try again later');
    } else if (!error.response) {
      throw new Error('Network error - please check your connection');
    }
    
    throw error;
  }
);

// API methods
export const videoAPI = {
  // Upload a video file
  uploadVideo: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 1 minute timeout for uploads
      });
      
      return response.data;
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  },
  
  // Get analysis status
  getStatus: async (analysisId) => {
    try {
      const response = await apiClient.get(`/status/${analysisId}`);
      return response.data;
    } catch (error) {
      console.error('Status error:', error);
      throw error;
    }
  },
  
  // Get analysis results
  getResults: async (analysisId) => {
    try {
      const response = await apiClient.get(`/results/${analysisId}`);
      return response.data;
    } catch (error) {
      console.error('Results error:', error);
      throw error;
    }
  },
  
  // Get video URL
  getVideoUrl: (analysisId) => {
    const baseUrl = process.env.NODE_ENV === 'production' 
      ? 'https://video-analysis-api-vt2g.onrender.com/api'
      : 'http://localhost:8000/api';
    return `${baseUrl}/video/${analysisId}`;
  },

  // Test API connection
  testConnection: async () => {
    try {
      const response = await apiClient.get('/../health');
      return response.data;
    } catch (error) {
      console.error('Connection test failed:', error);
      throw error;
    }
  }
};