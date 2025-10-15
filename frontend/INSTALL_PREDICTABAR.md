# Installing Predictabar React Widget

## Steps to Install the Predictabar React Component

### 1. Navigate to frontend directory
```bash
cd /Users/alextaliaferro/Development/python/data-generator/frontend
```

### 2. Install dependencies (if not already done)
```bash
npm install
```

### 3. Install Predictabar React package
```bash
# Check the official package name from https://test.predictabar.com/widget
npm install @predictabar/react
# OR if it's a different package name:
# npm install predictabar-widget
```

### 4. Update the PredictabarWidget component

The component is located at:
`frontend/src/components/PredictabarWidget.js`

Replace the placeholder implementation with the actual Predictabar React component:

```javascript
import React from 'react';
import { PredictabarWidget as PredictabarSDK } from '@predictabar/react';
import './PredictabarWidget.css';

function PredictabarWidget({ jobStatus, isGenerating }) {
  if (!jobStatus) return null;

  return (
    <div className="predictabar-widget">
      <PredictabarSDK
        progress={jobStatus.progress_percentage}
        estimatedTime={jobStatus.estimated_remaining_seconds}
        status={jobStatus.status}
        // Add other props as needed from Predictabar docs
      />
    </div>
  );
}

export default PredictabarWidget;
```

### 5. Start the React dev server
```bash
npm start
```

This will run on http://localhost:3001 (React default)

### 6. Update Flask server proxy (optional)
If you want everything on one port, you can serve the React build through Flask.

## Current Setup

Right now you're using the **simple HTML/JS version** at:
- Server: `app.py` 
- Template: `templates/index.html`
- JavaScript: `static/js/app.js`

This is easier to work with if you just need to embed a vanilla JS widget!

