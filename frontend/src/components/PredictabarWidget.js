import React, { useEffect, useRef } from 'react';
import './PredictabarWidget.css';

/**
 * Predictabar Widget Component
 * 
 * This component integrates the Predictabar widget to show real-time
 * time estimation for data generation jobs.
 * 
 * Based on the Predictabar SDK from https://test.predictabar.com/widget
 */
function PredictabarWidget({ jobStatus, isGenerating }) {
  const widgetRef = useRef(null);

  useEffect(() => {
    // Initialize Predictabar widget
    // This would typically load the Predictabar SDK script
    // For now, we'll create a custom progress bar that mimics the functionality
    
    if (window.Predictabar) {
      // If Predictabar SDK is loaded, initialize it
      window.Predictabar.init({
        container: widgetRef.current,
        theme: 'modern',
        showTimeRemaining: true,
        showPercentage: true
      });
    }
  }, []);

  useEffect(() => {
    // Update widget with current progress
    if (jobStatus && window.Predictabar) {
      window.Predictabar.update({
        progress: jobStatus.progress_percentage,
        estimatedTimeRemaining: jobStatus.estimated_remaining_seconds,
        status: jobStatus.status
      });
    }
  }, [jobStatus]);

  if (!jobStatus) {
    return null;
  }

  const progressPercentage = jobStatus.progress_percentage || 0;
  const estimatedRemaining = jobStatus.estimated_remaining_seconds;
  
  // Format time remaining
  const formatTime = (seconds) => {
    if (!seconds || seconds < 0) return 'Calculating...';
    
    if (seconds < 60) {
      return `${Math.round(seconds)}s`;
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      const secs = Math.round(seconds % 60);
      return `${minutes}m ${secs}s`;
    } else {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}h ${minutes}m`;
    }
  };

  return (
    <div className="predictabar-widget" ref={widgetRef}>
      <div className="predictabar-header">
        <h3>📊 Generation Progress</h3>
        <span className={`status-badge ${jobStatus.status}`}>
          {jobStatus.status === 'running' ? '⚡ Running' : 
           jobStatus.status === 'completed' ? '✓ Complete' : 
           jobStatus.status === 'failed' ? '✗ Failed' : jobStatus.status}
        </span>
      </div>

      <div className="predictabar-body">
        <div className="progress-info">
          <div className="progress-stat">
            <span className="stat-value">{Math.round(progressPercentage)}%</span>
            <span className="stat-label">Complete</span>
          </div>
          
          <div className="progress-stat">
            <span className="stat-value">{formatTime(estimatedRemaining)}</span>
            <span className="stat-label">Est. Remaining</span>
          </div>
          
          <div className="progress-stat">
            <span className="stat-value">{jobStatus.elapsed_seconds.toFixed(1)}s</span>
            <span className="stat-label">Elapsed</span>
          </div>
        </div>

        <div className="progress-bar-container">
          <div 
            className="progress-bar-fill"
            style={{ 
              width: `${progressPercentage}%`,
              background: jobStatus.status === 'failed' ? '#f44336' :
                         jobStatus.status === 'completed' ? '#4caf50' :
                         'linear-gradient(90deg, #667eea 0%, #764ba2 100%)'
            }}
          >
            <div className="progress-bar-shimmer"></div>
          </div>
          <div className="progress-bar-text">
            {jobStatus.rows_completed.toLocaleString()} / {jobStatus.total_rows.toLocaleString()} rows
          </div>
        </div>

        <div className="progress-details">
          <div className="detail-item">
            <span className="detail-label">Days Completed:</span>
            <span className="detail-value">{jobStatus.days_completed} / {jobStatus.total_days}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Throughput:</span>
            <span className="detail-value">
              {jobStatus.elapsed_seconds > 0 
                ? `${Math.round(jobStatus.rows_completed / jobStatus.elapsed_seconds).toLocaleString()} rows/s`
                : 'Calculating...'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PredictabarWidget;

