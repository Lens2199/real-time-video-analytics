import { useEffect } from 'react'
import Dashboard from './components/Dashboard'
import Footer from './components/Footer'
import { initializeSocket, closeSocket } from './utils/socket'
import "./styles/styles.css";

function App() {
  // Initialize socket on component mount
  useEffect(() => {
    initializeSocket();
    
    // Cleanup on component unmount
    return () => {
      closeSocket();
    };
  }, []);
  
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <main className="flex-grow">
        <Dashboard />
      </main>
      <Footer />
    </div>
  )
}

export default App