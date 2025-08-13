import { useState, useEffect } from 'react';
import { Login } from './components/Login';
import { Dashboard } from './components/Dashboard';
import { api } from './services/api';

function App() {
  const [studentId, setStudentId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await api.getHealth();
        setIsHealthy(health.models_loaded);
      } catch (error) {
        console.error('Health check failed:', error);
        setIsHealthy(false);
      }
    };

    checkHealth();
  }, []);

  const handleLogin = async (id: string) => {
    setIsLoading(true);
    try {
      // Verify the API is working by trying to get recommendations
      await api.getRecommendations(id, 1);
      setStudentId(id);
    } catch (error) {
      console.error('Login failed:', error);
      alert('Failed to login. Please check if the backend API is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    setStudentId(null);
  };

  // Show loading state while checking health
  if (isHealthy === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Checking system status...</p>
        </div>
      </div>
    );
  }

  // Show error if API is not healthy
  if (isHealthy === false) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Service Unavailable</h2>
          <p className="text-gray-600 mb-6">
            The recommendation service is currently unavailable. Please ensure the backend API is running on port 8000.
          </p>
          <button 
            onClick={() => window.location.reload()} 
            className="btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {studentId ? (
        <Dashboard studentId={studentId} onLogout={handleLogout} />
      ) : (
        <Login onLogin={handleLogin} isLoading={isLoading} />
      )}
    </div>
  );
}

export default App;
