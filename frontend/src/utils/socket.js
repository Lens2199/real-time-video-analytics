import { io } from 'socket.io-client';

// Socket.io server URL - automatically switches between development and production
const SOCKET_URL = process.env.NODE_ENV === 'production' 
  ? 'https://video-analysis-api-vt2g.onrender.com'  // Your deployed backend
  : 'http://localhost:8000';

// Create socket instance
let socket;

export const initializeSocket = () => {
  if (!socket) {
    socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'], // Add polling as fallback
      autoConnect: true,
      withCredentials: false, // Change to false for cross-origin
      timeout: 20000,
      forceNew: true,
      reconnection: true,
      reconnectionAttempts: 3,
      reconnectionDelay: 1000,
    });
    
    // Connection event handlers
    socket.on('connect', () => {
      console.log('Socket connected successfully');
    });
    
    socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
    });
    
    socket.on('connect_error', (error) => {
      console.warn('Socket connection error:', error.message);
      // Don't retry immediately if it's a persistent error
      if (error.type === 'TransportError') {
        console.log('Falling back to polling transport...');
      }
    });

    socket.on('reconnect', (attemptNumber) => {
      console.log('Socket reconnected after', attemptNumber, 'attempts');
    });

    socket.on('reconnect_error', (error) => {
      console.warn('Socket reconnection failed:', error.message);
    });
  }
  
  return socket;
};

// Get socket instance
export const getSocket = () => {
  if (!socket) {
    return initializeSocket();
  }
  return socket;
};

// Close socket connection
export const closeSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};