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
  timeout: 60000, // 60 second timeout (Render can be slow on free tier)
});

// Add response interceptor for better error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Handle specific error cases
    if (error.code === 'ECONNABORTED') {
      throw new Error('Server is starting up, please try again in a moment');
    } else if (error.response?.status === 404) {
      throw new Error('Resource not found');
    } else if (error.response?.status >= 500) {
      throw new Error('Server error - please try again later');
    } else if (!error.response) {
      throw new Error('Unable to connect to server - it may be starting up');
    }
    
    throw error;
  }
);

// Retry function for important requests
const retryRequest = async (requestFn, maxRetries = 2, delay = 3000) => {
  for (let i = 0; i <= maxRetries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      if (i === maxRetries) throw error;
      
      console.log(`Request failed, retrying in ${delay}ms... (attempt ${i + 1}/${maxRetries + 1})`);
      await new Promise(resolve => setTimeout(resolve, delay));
      delay *= 1.5; // Exponential backoff
    }
  }
};

// API methods
export const videoAPI = {
  // Upload a video file
  uploadVideo: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await retryRequest(
        () => apiClient.post('/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 120000, // 2 minutes for uploads
        }),
        1, // Only 1 retry for uploads
        5000
      );
      
      return response.data;
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  },
  
  // Get analysis status
  getStatus: async (analysisId) => {
    try {
      const response = await apiClient.get(`/status/${analysisId}`, {
        timeout: 15000 // 15 seconds for status checks
      });
      return response.data;
    } catch (error) {
      console.error('Status error:', error);
      throw error;
    }
  },
  
  // Get analysis results
  getResults: async (analysisId) => {
    try {
      const response = await apiClient.get(`/results/${analysisId}`, {
        timeout: 30000 // 30 seconds for results
      });
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

  // Test API connection with retry logic
  testConnection: async () => {
    try {
      const response = await retryRequest(
        () => apiClient.get('/../health', { timeout: 30000 }),
        2, // 2 retries
        5000 // 5 second delay
      );
      return response.data;
    } catch (error) {
      console.error('Connection test failed:', error);
      throw error;
    }
  },

  // Simpler connection test (just check if server responds)
  pingServer: async () => {
    try {
      const response = await fetch(
        process.env.NODE_ENV === 'production' 
          ? 'https://video-analysis-api-vt2g.onrender.com/' 
          : 'http://localhost:8000/',
        { 
          method: 'GET',
          signal: AbortSignal.timeout(20000) // 20 second timeout
        }
      );
      return response.ok;
    } catch (error) {
      console.warn('Server ping failed:', error.message);
      return false;
    }
  }
};