import { io } from 'socket.io-client';

// Socket.io server URL - change this in production
const SOCKET_URL = 'http://localhost:8000';

// Create socket instance
let socket;

export const initializeSocket = () => {
  if (!socket) {
    socket = io(SOCKET_URL, {
      transports: ['websocket'],
      autoConnect: true,
      withCredentials: true,
      extraHeaders: {
        "Access-Control-Allow-Origin": "http://localhost:5173"
      }
    });
    
    // Connection event handlers
    socket.on('connect', () => {
      console.log('Socket connected');
    });
    
    socket.on('disconnect', () => {
      console.log('Socket disconnected');
    });
    
    socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
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