import React, { useState, useEffect } from 'react';
import { videoAPI } from '../services/api';
import { getSocket } from '../utils/socket';
import VideoInput from './VideoInput';
import ObjectDisplay from './ObjectDisplay';
import Charts from './Charts';

const Dashboard = () => {
  const [analysisId, setAnalysisId] = useState(null);
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [socketConnected, setSocketConnected] = useState(false);
  
  // Handle successful upload
  const handleUploadSuccess = (response) => {
    setAnalysisId(response.analysis_id);
    setStatus(response.status);
    setProgress(0);
    setResults(null);
    setError(null);
    
    // Start polling for status updates
    if (response.analysis_id) {
      pollStatus(response.analysis_id);
    }
  };
  
  // Poll for status updates (fallback when WebSocket fails)
  const pollStatus = async (id) => {
    try {
      const statusData = await videoAPI.getStatus(id);
      setStatus(statusData.status);
      setProgress(statusData.progress || 0);
      
      // If processing is complete, get results
      if (statusData.status === 'completed') {
        const resultsData = await videoAPI.getResults(id);
        setResults(resultsData);
      } else if (statusData.status === 'processing') {
        // Continue polling after a delay (only if socket is not connected)
        if (!socketConnected) {
          setTimeout(() => pollStatus(id), 3000);
        }
      } else if (statusData.status === 'error') {
        setError(statusData.message || 'An error occurred during processing');
      }
    } catch (error) {
      console.error('Error polling status:', error);
      setError('Failed to get processing status');
    }
  };
  
  // Set up socket connection for real-time updates (with graceful fallback)
  useEffect(() => {
    let socket;
    
    try {
      socket = getSocket();
      
      // Check if socket connects successfully
      socket.on('connect', () => {
        console.log('Socket connected successfully');
        setSocketConnected(true);
      });
      
      socket.on('disconnect', () => {
        console.log('Socket disconnected');
        setSocketConnected(false);
      });
      
      socket.on('connect_error', (error) => {
        console.warn('Socket connection failed, using polling fallback');
        setSocketConnected(false);
      });
      
      // Listen for analysis status updates (only if socket works)
      socket.on('analysis_update', (data) => {
        if (data.analysis_id === analysisId) {
          setStatus(data.status);
          setProgress(data.progress || 0);
          
          // If processing is complete, get results
          if (data.status === 'completed') {
            videoAPI.getResults(data.analysis_id)
              .then(resultsData => setResults(resultsData))
              .catch(error => {
                console.error('Error getting results:', error);
                setError('Failed to get analysis results');
              });
          } else if (data.status === 'error') {
            setError(data.message || 'An error occurred during processing');
          }
        }
      });
      
    } catch (error) {
      console.warn('Socket.IO initialization failed, using polling fallback');
      setSocketConnected(false);
    }
    
    // Cleanup on component unmount
    return () => {
      if (socket) {
        socket.off('analysis_update');
        socket.off('connect');
        socket.off('disconnect');
        socket.off('connect_error');
      }
    };
  }, [analysisId]);
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">AI Video Analysis Dashboard</h1>
      
      {!socketConnected && (
        <div className="mb-4 p-3 bg-yellow-50 text-yellow-800 rounded-md">
          Real-time updates unavailable. Using polling for status updates.
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <VideoInput onUploadSuccess={handleUploadSuccess} />
          
          {analysisId && (
            <div className="card mb-6">
              <h2 className="text-xl font-bold mb-4">Analysis Status</h2>
              <div className="mb-4">
                <span className="font-medium">Analysis ID:</span>{' '}
                <span className="font-mono text-sm">{analysisId}</span>
              </div>
              <div className="mb-4">
                <span className="font-medium">Status:</span>{' '}
                <span className={`inline-block px-2 py-1 rounded ${
                  status === 'completed' ? 'bg-green-100 text-green-800' : 
                  status === 'processing' ? 'bg-blue-100 text-blue-800' : 
                  status === 'error' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {status}
                </span>
              </div>
              {status === 'processing' && (
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">Progress: {progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                    <div 
                      className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>
              )}
              {error && (
                <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md">
                  <p className="font-medium">Error:</p>
                  <p>{error}</p>
                </div>
              )}
            </div>
          )}
        </div>
        
        <div className="lg:col-span-2">
          {results && (
            <>
              <ObjectDisplay results={results} />
              <div className="mt-6">
                <Charts results={results} />
              </div>
            </>
          )}
          
          {!results && status === 'processing' && (
            <div className="card flex items-center justify-center p-12">
              <div className="text-center">
                <svg className="animate-spin h-10 w-10 text-blue-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p className="text-gray-600">Processing your video...</p>
                <p className="text-sm text-gray-500 mt-2">This may take a few minutes depending on the video size.</p>
              </div>
            </div>
          )}
          
          {!results && !status && (
            <div className="card bg-blue-50 border border-blue-200">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-blue-800 mb-2">How It Works</h3>
                <p className="text-blue-700 mb-4">
                  This system uses AI to analyze videos in real-time:
                </p>
                <ol className="list-decimal list-inside space-y-2 text-blue-700">
                  <li>Upload a video file using the panel on the left</li>
                  <li>Our AI processes the video using YOLOv8 object detection</li>
                  <li>Multiple AI agents collaborate to track and analyze objects</li>
                  <li>View detailed results and visualizations when processing completes</li>
                </ol>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
