#!/usr/bin/env python3
"""
Simple Flask server to serve the Predictabar widget demo page
"""

from flask import Flask, render_template, jsonify
import random
import time
import os
import uuid
from predictabar import configure, post_started, post_progress, post_finished, post_crashed

app = Flask(__name__)

# Configure PredictaBar SDK
PREDICTABAR_BAR_ID = os.getenv('PREDICTABAR_BAR_ID', '41ff9432-fc34-4c9b-8236-865aef4b1250')
PREDICTABAR_API_KEY = os.getenv('PREDICTABAR_API_KEY', 'pk_prod_3d4g3uml_zm66g4zbtapu31sxxi6vp')

# Configure PredictaBar
configure(api_key=PREDICTABAR_API_KEY, bar_id=PREDICTABAR_BAR_ID)

# Simulate job progress
job_progress = {
    'progress': 0,
    'start_time': None,
    'status': 'idle',
    'run_id': None
}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html',
                         predictabar_bar_id=PREDICTABAR_BAR_ID,
                         predictabar_api_key=PREDICTABAR_API_KEY)

@app.route('/api/start', methods=['POST'])
def start_job():
    """Start a demo job"""
    global job_progress

    # Generate unique run ID
    run_id = f"data_gen_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    job_progress = {
        'progress': 0,
        'start_time': time.time(),
        'status': 'running',
        'total_rows': 10000,
        'run_id': run_id
    }

    # Notify PredictaBar that job started
    try:
        post_started("Data Generation Job", run_id)
        print(f"✅ PredictaBar: Job started - {run_id}")
    except Exception as e:
        print(f"⚠️ PredictaBar: Failed to notify job start - {e}")

    return jsonify({'success': True, 'run_id': run_id})

@app.route('/api/progress')
def get_progress():
    """Get current progress"""
    global job_progress

    if job_progress['status'] == 'running':
        # Simulate progress
        elapsed = time.time() - job_progress['start_time']
        progress = min(100, (elapsed / 30) * 100)  # 30 second simulation
        job_progress['progress'] = progress

        # Send progress updates to PredictaBar every 10%
        if int(progress) % 10 == 0 and int(progress) > 0:
            try:
                post_progress(
                    "Data Generation Job",
                    job_progress['run_id'],
                    int(progress),
                    100,
                    stage_name="generating_data"
                )
                print(f"📊 PredictaBar: Progress update - {int(progress)}%")
            except Exception as e:
                print(f"⚠️ PredictaBar: Failed to send progress - {e}")

        if progress >= 100:
            job_progress['status'] = 'completed'

            # Notify PredictaBar that job completed
            try:
                post_finished(
                    "Data Generation Job",
                    job_progress['run_id'],
                    {
                        "total_rows": job_progress['total_rows'],
                        "duration_seconds": elapsed,
                        "status": "success"
                    }
                )
                print(f"✅ PredictaBar: Job completed - {job_progress['run_id']}")
            except Exception as e:
                print(f"⚠️ PredictaBar: Failed to notify completion - {e}")

    return jsonify({
        'progress': job_progress['progress'],
        'status': job_progress['status'],
        'elapsed': time.time() - job_progress['start_time'] if job_progress['start_time'] else 0,
        'estimated_remaining': max(0, 30 - (time.time() - job_progress['start_time'])) if job_progress['start_time'] else 30,
        'run_id': job_progress.get('run_id')
    })

if __name__ == '__main__':
    print("🚀 Starting server at http://localhost:3000")
    print("📊 Open your browser and navigate to: http://localhost:3000")
    app.run(debug=True, host='0.0.0.0', port=3000)
