import axios from 'axios';

// API base URL - change this in production
const API_BASE_URL = 'http://localhost:8000/api';

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
};