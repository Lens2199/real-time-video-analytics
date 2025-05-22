import React, { useState, useEffect } from 'react';
import { videoAPI } from '../services/api';
import VideoInput from './VideoInput';
import ObjectDisplay from './ObjectDisplay';
import Charts from './Charts';

const Dashboard = () => {
  const [analysisId, setAnalysisId] = useState(null);
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [apiConnected, setApiConnected] = useState(false);
  
  // Test API connection on component mount
  useEffect(() => {
    const testConnection = async () => {
      try {
        await videoAPI.testConnection();
        setApiConnected(true);
        console.log('API connection successful');
      } catch (error) {
        setApiConnected(false);
        console.warn('API connection failed:', error.message);
      }
    };
    
    testConnection();
  }, []);
  
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
  
  // Poll for status updates
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
        // Continue polling after a delay
        setTimeout(() => pollStatus(id), 4000); // Poll every 4 seconds
      } else if (statusData.status === 'error') {
        setError(statusData.message || 'An error occurred during processing');
      }
    } catch (error) {
      console.error('Error polling status:', error);
      setError(`Failed to get processing status: ${error.message}`);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">AI Video Analysis Dashboard</h1>
      
      {/* Connection Status */}
      <div className="mb-4">
        <div className={`p-3 rounded-md ${apiConnected ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
          <span className="font-medium">Backend Status:</span> {apiConnected ? 'Connected ✓' : 'Checking connection...'}
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <VideoInput onUploadSuccess={handleUploadSuccess} disabled={!apiConnected} />
          
          {analysisId && (
            <div className="card mb-6">
              <h2 className="text-xl font-bold mb-4">Analysis Status</h2>
              <div className="mb-4">
                <span className="font-medium">Analysis ID:</span>{' '}
                <span className="font-mono text-xs break-all">{analysisId}</span>
              </div>
              <div className="mb-4">
                <span className="font-medium">Status:</span>{' '}
                <span className={`inline-block px-2 py-1 rounded text-sm ${
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
                  <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                    <div 
                      className="bg-blue-600 h-3 rounded-full transition-all duration-300" 
                      style={{ width: `${Math.max(progress, 10)}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600">Processing video... Please wait.</p>
                </div>
              )}
              {error && (
                <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md">
                  <p className="font-medium">Error:</p>
                  <p className="text-sm">{error}</p>
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
                <svg className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p className="text-gray-800 font-medium">Processing your video...</p>
                <p className="text-sm text-gray-600 mt-2">This may take a few minutes depending on the video size.</p>
                <p className="text-xs text-gray-500 mt-2">Status updates every 4 seconds</p>
              </div>
            </div>
          )}
          
          {!results && !status && (
            <div className="card bg-blue-50 border border-blue-200">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-blue-800 mb-2">How It Works</h3>
                <p className="text-blue-700 mb-4">
                  This system uses AI to analyze videos:
                </p>
                <ol className="list-decimal list-inside space-y-2 text-blue-700">
                  <li>Upload a video file using the panel on the left</li>
                  <li>Our AI processes the video using YOLOv8 object detection</li>
                  <li>Multiple AI agents collaborate to track and analyze objects</li>
                  <li>View detailed results and visualizations when processing completes</li>
                </ol>
                <div className="mt-4 p-3 bg-blue-100 rounded-md">
                  <p className="text-sm text-blue-800">
                    <strong>Note:</strong> First upload may take longer as the backend initializes.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;