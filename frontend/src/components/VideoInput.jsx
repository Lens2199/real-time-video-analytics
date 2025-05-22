import React, { useState, useRef } from 'react';
import { videoAPI } from '../services/api';

const VideoInput = ({ onUploadSuccess, disabled = false }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  
  // Handle file selection
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    if (selectedFile) {
      // Check if file is a video
      if (!selectedFile.type.startsWith('video/')) {
        setError('Please select a valid video file');
        setFile(null);
        return;
      }
      
      // Check file size (limit to 50MB for free tier)
      if (selectedFile.size > 50 * 1024 * 1024) {
        setError('File size too large. Please select a video under 50MB.');
        setFile(null);
        return;
      }
      
      setFile(selectedFile);
      setError(null);
    }
  };
  
  // Handle file upload
  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }
    
    if (disabled) {
      setError('Backend is not available. Please try again later.');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Upload the video file
      const response = await videoAPI.uploadVideo(file);
      
      // Call the success callback with the response
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
      
      // Reset the file input
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      console.error('Upload error:', err);
      if (err.message.includes('Network Error')) {
        setError('Unable to connect to server. Please check if the backend is running and try again.');
      } else {
        setError(err.response?.data?.detail || err.message || 'Failed to upload video');
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="card mb-6">
      <h2 className="text-xl font-bold mb-4">Upload Video</h2>
      
      <div className="mb-4">
        <input
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          ref={fileInputRef}
          disabled={disabled || loading}
          className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-medium
                    file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100
                    disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>
      
      {file && (
        <div className="mb-4 p-3 bg-gray-100 rounded-md">
          <p className="text-sm">
            <span className="font-medium">Selected file:</span> {file.name}
          </p>
          <p className="text-sm">
            <span className="font-medium">Size:</span> {(file.size / (1024 * 1024)).toFixed(2)} MB
          </p>
        </div>
      )}
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md">
          <p className="text-sm">{error}</p>
        </div>
      )}
      
      <button
        onClick={handleUpload}
        disabled={!file || loading || disabled}
        className={`w-full py-2 px-4 rounded-md font-medium transition-colors ${
          !file || loading || disabled 
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Uploading...
          </span>
        ) : (
          'Upload Video'
        )}
      </button>
      
      <div className="mt-3 text-xs text-gray-500">
        <p>• Supported formats: MP4, AVI, MOV, MKV</p>
        <p>• Maximum file size: 50MB</p>
        <p>• Best results with videos containing people, animals, or vehicles</p>
      </div>
    </div>
  );
};

export default VideoInput;