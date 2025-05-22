import { io } from 'socket.io-client';

// Socket.io server URL - automatically switches between development and production
const SOCKET_URL = process.env.NODE_ENV === 'production' 
  ? 'https://video-analysis-api-vt2g.onrender.com'  // Your deployed backend
  : 'http://localhost:8000';

// Create socket instance
let socket;
let connectionAttempts = 0;
const maxConnectionAttempts = 3;

export const initializeSocket = () => {
  if (!socket && connectionAttempts < maxConnectionAttempts) {
    connectionAttempts++;
    
    try {
      socket = io(SOCKET_URL, {
        transports: ['polling'], // Use polling first, then upgrade to websocket
        autoConnect: true,
        withCredentials: false,
        timeout: 10000,
        reconnection: true,
        reconnectionAttempts: 2,
        reconnectionDelay: 2000,
        forceNew: true,
      });
      
      // Connection event handlers
      socket.on('connect', () => {
        console.log('Socket connected successfully');
        connectionAttempts = 0; // Reset on successful connection
      });
      
      socket.on('disconnect', (reason) => {
        console.log('Socket disconnected:', reason);
      });
      
      socket.on('connect_error', (error) => {
        console.warn('Socket connection failed:', error.message);
        
        // If we've tried multiple times, stop trying
        if (connectionAttempts >= maxConnectionAttempts) {
          console.log('Max connection attempts reached, disabling socket');
          socket = null;
        }
      });

      socket.on('reconnect', (attemptNumber) => {
        console.log('Socket reconnected after', attemptNumber, 'attempts');
        connectionAttempts = 0;
      });

      socket.on('reconnect_failed', () => {
        console.warn('Socket reconnection failed permanently');
        socket = null;
      });
      
    } catch (error) {
      console.warn('Socket initialization failed:', error.message);
      socket = null;
    }
  }
  
  return socket;
};

// Get socket instance
export const getSocket = () => {
  if (!socket && connectionAttempts < maxConnectionAttempts) {
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
  connectionAttempts = 0;
};