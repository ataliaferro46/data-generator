#!/usr/bin/env python3
"""
Simple Flask server to serve the Predictabar widget demo page
"""

from flask import Flask, render_template, jsonify
import random
import time

app = Flask(__name__)

# Simulate job progress
job_progress = {
    'progress': 0,
    'start_time': None,
    'status': 'idle'
}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_job():
    """Start a demo job"""
    global job_progress
    job_progress = {
        'progress': 0,
        'start_time': time.time(),
        'status': 'running',
        'total_rows': 10000
    }
    return jsonify({'success': True})

@app.route('/api/progress')
def get_progress():
    """Get current progress"""
    global job_progress
    
    if job_progress['status'] == 'running':
        # Simulate progress
        elapsed = time.time() - job_progress['start_time']
        progress = min(100, (elapsed / 30) * 100)  # 30 second simulation
        job_progress['progress'] = progress
        
        if progress >= 100:
            job_progress['status'] = 'completed'
    
    return jsonify({
        'progress': job_progress['progress'],
        'status': job_progress['status'],
        'elapsed': time.time() - job_progress['start_time'] if job_progress['start_time'] else 0,
        'estimated_remaining': max(0, 30 - (time.time() - job_progress['start_time'])) if job_progress['start_time'] else 30
    })

if __name__ == '__main__':
    print("🚀 Starting server at http://localhost:3000")
    print("📊 Open your browser and navigate to: http://localhost:3000")
    app.run(debug=True, host='0.0.0.0', port=3000)

