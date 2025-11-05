import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Verify backend connection
    fetch('/health')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        setBackendStatus(data);
        console.log('Backend connection successful:', data);
      })
      .catch(err => {
        setError(err.message);
        console.error('Backend connection failed:', err);
      });
  }, []);

  return (
    <div className="App">
      <header>
        <h1>OMNIVID Video Generator</h1>
      </header>
      
      <main className="container">
        <div className="status-card">
          <h2>Backend Status</h2>
          {backendStatus ? (
            <div className="status-success">
              <p>Connected to {backendStatus.app} v{backendStatus.version}</p>
              <p>Status: {backendStatus.status}</p>
            </div>
          ) : error ? (
            <div className="status-error">
              <p>Connection failed: {error}</p>
              <p>Make sure backend is running on port 8000</p>
            </div>
          ) : (
            <p>Checking connection...</p>
          )}
        </div>
        
        <div className="instructions">
          <h2>Next Steps</h2>
          <ol>
            <li>Start backend server: <code>cd backend && python main.py</code></li>
            <li>Start frontend: <code>cd frontend && npm start</code></li>
            <li>Verify both services are running</li>
          </ol>
        </div>
      </main>
    </div>
  );
}

export default App;