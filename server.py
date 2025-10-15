#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask server for data generator with Predictabar widget integration
"""

import os
import json
import time
import threading
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sse import sse
from queue import Queue
from datetime import datetime

from config import GeneratorConfig
from data_generator import DataGenerator
from exceptions import DataGenerationError

app = Flask(__name__, static_folder='frontend/build')
CORS(app)

# Store active generation jobs
active_jobs = {}
job_queue = Queue()


class ProgressTracker:
    """Track progress and estimate completion time"""
    
    def __init__(self, job_id, total_rows, total_days):
        self.job_id = job_id
        self.total_rows = total_rows
        self.total_days = total_days
        self.rows_completed = 0
        self.days_completed = 0
        self.start_time = time.time()
        self.status = "running"
        self.error = None
        
    def update(self, rows_completed, days_completed):
        """Update progress"""
        self.rows_completed = rows_completed
        self.days_completed = days_completed
        
    def get_progress_percentage(self):
        """Get overall progress percentage"""
        if self.total_rows == 0:
            return 0
        return min(100, (self.rows_completed / self.total_rows) * 100)
    
    def get_estimated_time_remaining(self):
        """Estimate time remaining in seconds"""
        elapsed = time.time() - self.start_time
        progress = self.get_progress_percentage()
        
        if progress == 0:
            return None
        
        # Estimate based on current rate
        total_estimated = (elapsed / progress) * 100
        remaining = total_estimated - elapsed
        return max(0, remaining)
    
    def get_status_dict(self):
        """Get status as dictionary for API"""
        return {
            'job_id': self.job_id,
            'status': self.status,
            'progress_percentage': round(self.get_progress_percentage(), 2),
            'rows_completed': self.rows_completed,
            'total_rows': self.total_rows,
            'days_completed': self.days_completed,
            'total_days': self.total_days,
            'elapsed_seconds': round(time.time() - self.start_time, 2),
            'estimated_remaining_seconds': self.get_estimated_time_remaining(),
            'error': self.error
        }


def generate_data_worker(job_id, config_dict, tracker):
    """Worker thread to generate data"""
    try:
        # Create config from dict
        config = GeneratorConfig.from_dict(config_dict)
        
        # Create generator
        generator = DataGenerator(config)
        
        # Monkey-patch to track progress
        original_write_output = generator._write_output_data
        
        def tracked_write_output():
            """Wrapped output writer that tracks progress"""
            from tqdm import tqdm
            import sqlite3
            from output_writers import OutputWriterFactory
            
            writer = OutputWriterFactory.create_writer(config.output_format)
            extension = writer.get_file_extension()
            
            for day_index in range(config.num_days):
                # Get field names
                field_names = []
                for column_space in generator.column_spaces:
                    field_name = column_space.get_field_name(day_index, config.num_days)
                    field_names.append(field_name)
                
                # Open cache connections
                connections = {}
                try:
                    for column_space in generator.column_spaces:
                        cache_path = column_space._get_cache_path(day_index)
                        connections[column_space.config.name] = sqlite3.connect(cache_path)
                    
                    # Write the day's data
                    output_path = os.path.join(config.output_dir, f"{day_index}.{extension}")
                    rows_for_day = generator.rows_per_day_map[day_index]
                    
                    writer.write_day(day_index, field_names, connections, rows_for_day, output_path)
                    writer.set_file_timestamp(output_path, day_index, config.num_days)
                    
                    generator.metrics.files_written += 1
                    
                    # Update tracker
                    total_completed = sum(
                        generator.rows_per_day_map[i] 
                        for i in range(day_index + 1)
                    )
                    tracker.update(total_completed, day_index + 1)
                    
                finally:
                    for conn in connections.values():
                        conn.close()
        
        generator._write_output_data = tracked_write_output
        
        # Generate data
        metrics = generator.generate()
        
        tracker.status = "completed"
        tracker.rows_completed = metrics.total_rows_generated
        
    except Exception as e:
        tracker.status = "failed"
        tracker.error = str(e)
        print(f"Generation failed: {e}")


@app.route('/api/generate', methods=['POST'])
def start_generation():
    """Start a new data generation job"""
    try:
        data = request.json
        
        # Generate job ID
        job_id = f"job_{int(time.time() * 1000)}"
        
        # Extract configuration
        config_dict = data.get('config', {})
        
        # Set defaults if not provided
        config_dict.setdefault('num_days', 10)
        config_dict.setdefault('approx_rows_per_day', 1000)
        config_dict.setdefault('output_dir', f'generated_data/{job_id}')
        config_dict.setdefault('output_format', 'csv')
        
        # Calculate total expected rows
        total_rows = config_dict['num_days'] * config_dict['approx_rows_per_day']
        
        # Create progress tracker
        tracker = ProgressTracker(
            job_id, 
            total_rows,
            config_dict['num_days']
        )
        active_jobs[job_id] = tracker
        
        # Start generation in background thread
        thread = threading.Thread(
            target=generate_data_worker,
            args=(job_id, config_dict, tracker),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': tracker.get_status_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get status of a generation job"""
    if job_id not in active_jobs:
        return jsonify({
            'success': False,
            'error': 'Job not found'
        }), 404
    
    tracker = active_jobs[job_id]
    return jsonify({
        'success': True,
        'status': tracker.get_status_dict()
    })


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    jobs = []
    for job_id, tracker in active_jobs.items():
        jobs.append(tracker.get_status_dict())
    
    return jsonify({
        'success': True,
        'jobs': jobs
    })


@app.route('/api/config/example', methods=['GET'])
def get_example_config():
    """Get example configuration"""
    return jsonify({
        'success': True,
        'config': {
            'num_days': 10,
            'approx_rows_per_day': 1000,
            'output_format': 'csv',
            'max_workers': 2,
            'columns': [
                {
                    'name': 'id',
                    'data_type': 'INTEGER',
                    'distribution_flags': 1
                },
                {
                    'name': 'sensor_reading',
                    'data_type': 'FLOAT',
                    'distribution_flags': 4
                }
            ]
        }
    })


# Serve React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React frontend"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    print("🚀 Starting Data Generator Server...")
    print("📊 Server running at: http://localhost:5000")
    print("📡 API available at: http://localhost:5000/api")
    app.run(debug=True, host='0.0.0.0', port=5000)

