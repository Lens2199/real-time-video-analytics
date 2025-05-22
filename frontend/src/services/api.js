import axios from 'axios';

// API base URL - automatically switches between development and production
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://video-analysis-api-vt2g.onrender.com/api'  // Your deployed backend
  : 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API methods
export const videoAPI = {
  // Upload a video file
  uploadVideo: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },
  
  // Get analysis status
  getStatus: async (analysisId) => {
    const response = await apiClient.get(`/status/${analysisId}`);
    return response.data;
  },
  
  // Get analysis results
  getResults: async (analysisId) => {
    const response = await apiClient.get(`/results/${analysisId}`);
    return response.data;
  },
  
  // Get video URL
  getVideoUrl: (analysisId) => {
    const baseUrl = process.env.NODE_ENV === 'production' 
      ? 'https://video-analysis-api-vt2g.onrender.com/api'
      : 'http://localhost:8000/api';
    return `${baseUrl}/video/${analysisId}`;
  }
};