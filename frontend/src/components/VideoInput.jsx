import React, { useState, useRef } from 'react';
import { videoAPI } from '../services/api';

const VideoInput = ({ onUploadSuccess }) => {
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
      setError(err.response?.data?.detail || 'Failed to upload video');
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
          className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-medium
                    file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100"
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
          {error}
        </div>
      )}
      
      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className={`btn ${!file || loading ? 'bg-gray-300 cursor-not-allowed' : 'btn-primary'}`}
      >
        {loading ? 'Uploading...' : 'Upload Video'}
      </button>
    </div>
  );
};

export default VideoInput;