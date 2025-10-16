import React from 'react';
import './PredictabarWidget.css';
import { PredictaBarWidget } from '@predictabar/react-widget';

/**
 * Predictabar Widget Component
 * 
 * This component integrates the Predictabar widget to show real-time
 * time estimation for data generation jobs.
 * 
 * Based on the Predictabar SDK from https://test.predictabar.com/widget
 */
function PredictabarWidget({ jobStatus, isGenerating, title = 'Data Generation', description = 'Real-time progress tracking' }) {
  // Render official PredictaBar React widget with your credentials
  return (
    <div className="predictabar-widget">
      <PredictaBarWidget
        barId="41ff9432-fc34-4c9b-8236-865aef4b1250"
        apiKey="pk_prod_3d4g3uml_zm66g4zbtapu31sxxi6vp"
        title={title}
        description={description}
        refreshInterval={2000}
      />
    </div>
  );
}

export default PredictabarWidget;

