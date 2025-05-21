import React, { useState, useEffect } from 'react';
import { videoAPI } from '../services/api';
import { getSocket } from '../utils/socket';
import VideoInput from './VideoInput';

const Dashboard = () => {
  const [analysisId, setAnalysisId] = useState(null);
  const [status, setStatus] = useState(null);
  const [results, setResults] = useState(null);
  
  // Handle successful upload
  const handleUploadSuccess = (response) => {
    setAnalysisId(response.analysis_id);
    setStatus(response.status);
    
    // Start polling for status updates
    if (response.analysis_id) {
      pollStatus(response.analysis_id);
    }
  };
  
  // Poll for status updates
  const pollStatus = async (id) => {
    try {
      const statusData = await videoAPI.getStatus(id);
      setStatus(statusData.status);
      
      // If processing is complete, get results
      if (statusData.status === 'completed') {
        const resultsData = await videoAPI.getResults(id);
        setResults(resultsData);
      } else if (statusData.status === 'processing') {
        // Continue polling after a delay
        setTimeout(() => pollStatus(id), 2000);
      }
    } catch (error) {
      console.error('Error polling status:', error);
    }
  };
  
  // Set up socket connection for real-time updates
  useEffect(() => {
    const socket = getSocket();
    
    // Listen for analysis status updates
    socket.on('analysis_update', (data) => {
      if (data.analysis_id === analysisId) {
        setStatus(data.status);
        
        // If processing is complete, get results
        if (data.status === 'completed') {
          videoAPI.getResults(data.analysis_id)
            .then(resultsData => setResults(resultsData))
            .catch(error => console.error('Error getting results:', error));
        }
      }
    });
    
    // Cleanup on component unmount
    return () => {
      socket.off('analysis_update');
    };
  }, [analysisId]);
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">AI Video Analysis Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <VideoInput onUploadSuccess={handleUploadSuccess} />
          
          {status && (
            <div className="card mb-6">
              <h2 className="text-xl font-bold mb-4">Analysis Status</h2>
              <div className="mb-4">
                <span className="font-medium">Analysis ID:</span> {analysisId}
              </div>
              <div className="mb-4">
                <span className="font-medium">Status:</span>{' '}
                <span className={`inline-block px-2 py-1 rounded ${
                  status === 'completed' ? 'bg-green-100 text-green-800' : 
                  status === 'processing' ? 'bg-blue-100 text-blue-800' : 
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {status}
                </span>
              </div>
              {status === 'processing' && (
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-blue-600 h-2.5 rounded-full w-1/2"></div>
                </div>
              )}
            </div>
          )}
        </div>
        
        <div>
          {results && (
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Analysis Results</h2>
              <p className="text-gray-600 italic mb-4">
                Note: This is a placeholder. We'll add real visualizations in the next phase!
              </p>
              <pre className="bg-gray-100 p-4 rounded-md overflow-auto max-h-96">
                {JSON.stringify(results, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;