# 🚀 Quick Start Guide

## Running the Predictabar Widget Demo

### 1. Install Dependencies

```bash
pip install flask
```

### 2. Start the Server

```bash
python app.py
```

### 3. Open in Browser

Navigate to: **http://localhost:3000**

---

## What You'll See

- A beautiful landing page with a demo progress tracker
- Placeholder for the Predictabar widget integration
- Start button to trigger a demo data generation job (30 second simulation)
- Real-time progress updates

---

## Integrating the Real Predictabar Widget

1. Visit https://test.predictabar.com/widget to get the SDK
2. Replace the SDK script URL in `templates/index.html` (line 10)
3. The JavaScript in `static/js/app.js` already has hooks to update Predictabar
4. Customize the widget initialization in `app.js` (line 155)

---

## File Structure

```
├── app.py                    # Flask server
├── templates/
│   └── index.html           # Main landing page
├── static/
│   ├── css/
│   │   └── style.css        # Styles
│   └── js/
│       └── app.js           # Client-side logic
```

---

## Next Steps

- Replace the demo simulation with real data generation
- Connect to the actual Predictabar SDK from https://test.predictabar.com/widget
- Add configuration options for data generation parameters

