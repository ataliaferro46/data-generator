import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import PredictabarWidget from './components/PredictabarWidget';
import ConfigForm from './components/ConfigForm';
import StatusDisplay from './components/StatusDisplay';

function App() {
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  // Poll for job status when a job is active
  useEffect(() => {
    if (!jobId || !isGenerating) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`/api/status/${jobId}`);
        if (response.data.success) {
          const status = response.data.status;
          setJobStatus(status);

          // Stop polling if job is complete or failed
          if (status.status === 'completed' || status.status === 'failed') {
            setIsGenerating(false);
            clearInterval(pollInterval);
          }
        }
      } catch (err) {
        console.error('Error polling job status:', err);
        setError('Failed to get job status');
      }
    }, 1000); // Poll every second

    return () => clearInterval(pollInterval);
  }, [jobId, isGenerating]);

  const handleStartGeneration = async (config) => {
    try {
      setError(null);
      setIsGenerating(true);
      
      const response = await axios.post('/api/generate', {
        config: config
      });

      if (response.data.success) {
        setJobId(response.data.job_id);
        setJobStatus(response.data.status);
      } else {
        throw new Error(response.data.error || 'Failed to start generation');
      }
    } catch (err) {
      console.error('Error starting generation:', err);
      setError(err.response?.data?.error || err.message || 'Failed to start generation');
      setIsGenerating(false);
    }
  };

  const handleReset = () => {
    setJobId(null);
    setJobStatus(null);
    setIsGenerating(false);
    setError(null);
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

        {!isGenerating && !jobStatus ? (
          <ConfigForm onSubmit={handleStartGeneration} />
        ) : (
          <div className="generation-container">
            <PredictabarWidget 
              jobStatus={jobStatus}
              isGenerating={isGenerating}
            />
            
            <StatusDisplay 
              jobStatus={jobStatus}
              isGenerating={isGenerating}
            />

            {jobStatus && (jobStatus.status === 'completed' || jobStatus.status === 'failed') && (
              <button 
                className="reset-button"
                onClick={handleReset}
              >
                Start New Generation
              </button>
            )}
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>Built with React + Flask | Powered by Predictabar</p>
      </footer>
    </div>
  );
}

export default App;

