// Simplified socket utility - WebSockets disabled for stability
let socket = null;

export const initializeSocket = () => {
  // Return null - WebSockets disabled for production stability
  console.log('WebSockets disabled - using polling for updates');
  return null;
};

export const getSocket = () => {
  // Always return null to disable WebSocket functionality
  return null;
};

export const closeSocket = () => {
  // No-op since we're not using sockets
  return;
};