import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import PredictabarWidget from './components/PredictabarWidget';

function App() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  const handleStartGeneration = async () => {
    try {
      setError(null);
      setIsGenerating(true);
      
      // Call Flask backend to start generation
      const response = await axios.post('http://localhost:5000/api/start');
      
      if (response.data.success) {
        console.log('✅ Generation started:', response.data.run_id);
        // The PredictaBar widget will automatically show progress from your account
      } else {
        throw new Error('Failed to start generation');
      }
    } catch (err) {
      console.error('Error starting generation:', err);
      setError('Failed to start generation: ' + err.message);
      setIsGenerating(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎲 Data Generator</h1>
        <p>Generate synthetic time-series data with real-time progress tracking</p>
      </header>

      <main className="App-main">
        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <div className="generation-container">
          {/* PredictaBar widget - this is the real UI from PredictaBar */}
          <PredictabarWidget />
          
          {/* Simple start button */}
          <div className="controls">
            <button 
              className="start-button"
              onClick={handleStartGeneration}
              disabled={isGenerating}
            >
              {isGenerating ? 'Generating...' : 'Start Generation'}
            </button>
            
            <p className="instruction">
              Click "Start Generation" to begin a 30-second data generation job.
              The progress bar above will show real-time updates from PredictaBar.
            </p>
          </div>
        </div>
      </main>

      <footer className="App-footer">
        <p>Built with React + Flask | Powered by Predictabar</p>
      </footer>
    </div>
  );
}

export default App;

