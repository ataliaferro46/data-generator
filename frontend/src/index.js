import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { configurePredictaBar } from '@predictabar/react-widget';

// Configure PredictaBar once at app startup using env vars
// Define REACT_APP_PREDICTABAR_BAR_ID and REACT_APP_PREDICTABAR_API_KEY in .env
configurePredictaBar({
  bar_id: process.env.REACT_APP_PREDICTABAR_BAR_ID,
  api_key: process.env.REACT_APP_PREDICTABAR_API_KEY
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

