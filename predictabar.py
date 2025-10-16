"""
PredictaBar Python SDK - Standalone Version
============================================

A lightweight SDK for tracking job progress with PredictaBar.
Copy this file into your project and use it without any external dependencies (except requests).

Usage:
    from predictabar import configure, post_started, post_progress, post_finished, post_crashed
    
    # Configure once at startup
    configure(api_key="your-api-key", bar_id="your-bar-id")
    
    # Track your job
    post_started("ML Model Training", "run_123")
    post_progress("ML Model Training", "run_123", 50, 100)
    post_finished("ML Model Training", "run_123", {"accuracy": 0.95})
"""

import requests
import threading
from typing import Optional, Dict, Any

# Global configuration
_config = {
    "api_key": None,
    "bar_id": None,
    "base_url": "https://zohtkprgnaovmbrvzgsb.supabase.co/functions/v1"
}


def configure(api_key: str, bar_id: str, base_url: Optional[str] = None) -> None:
    """
    Configure the PredictaBar SDK with your API credentials.
    
    Args:
        api_key: Your PredictaBar API key
        bar_id: Your product's bar ID (external_uuid)
        base_url: Optional custom base URL for the API endpoint
        
    Example:
        configure(api_key="pk_live_123...", bar_id="prod_abc...")
    """
    _config["api_key"] = api_key
    _config["bar_id"] = bar_id
    if base_url:
        _config["base_url"] = base_url


def _send_update(payload: Dict[str, Any]) -> None:
    """
    Internal function to send updates to the PredictaBar API.
    
    Args:
        payload: The data payload to send
    """
    if not _config["api_key"]:
        raise ValueError("PredictaBar not configured. Call configure() first.")
    
    if not _config["bar_id"]:
        raise ValueError("bar_id not configured. Call configure() with bar_id.")
    
    url = f"{_config['base_url']}/submit-job-data"
    
    headers = {
        "apikey": _config["api_key"],
        "Content-Type": "application/json"
    }
    
    # Add bar_id to payload
    payload["bar_id"] = _config["bar_id"]
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Warning: Failed to send PredictaBar update: {e}")


def post_started(job_description: str, run_external_id: str) -> threading.Thread:
    """
    Mark a job as started (non-blocking).
    
    Args:
        job_description: Human-readable description of the job
        run_external_id: Unique identifier for this job run
        
    Returns:
        Thread: The background thread handling the API call
        
    Example:
        post_started("ML Model Training", "run_20250108_001")
    """
    payload = {
        "metadata": {
            "job_description": job_description,
            "started": True
        },
        "run_external_id": run_external_id
    }
    
    thread = threading.Thread(target=_send_update, args=(payload,), daemon=True)
    thread.start()
    return thread


def post_progress(
    job_description: str,
    run_external_id: str,
    job_progress_count: int,
    job_progress_total_count: int,
    stage_name: str = "processing"
) -> threading.Thread:
    """
    Report progress for a running job (non-blocking).
    
    Args:
        job_description: Human-readable description of the job
        run_external_id: Unique identifier for this job run
        job_progress_count: Current progress value (e.g., 50)
        job_progress_total_count: Total progress value (e.g., 100)
        stage_name: Optional stage/step name (default: "processing")
        
    Returns:
        Thread: The background thread handling the API call
        
    Example:
        for i in range(0, 101, 10):
            post_progress("Training", "run_123", i, 100, "epoch_training")
            # Do work...
    """
    payload = {
        "metadata": {
            "job_description": job_description,
            "job_progress_count": job_progress_count,
            "job_progress_total_count": job_progress_total_count,
            "stage_name": stage_name
        },
        "run_external_id": run_external_id
    }
    
    thread = threading.Thread(target=_send_update, args=(payload,), daemon=True)
    thread.start()
    return thread


def post_finished(
    job_description: str,
    run_external_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> threading.Thread:
    """
    Mark a job as successfully finished (non-blocking).
    
    Args:
        job_description: Human-readable description of the job
        run_external_id: Unique identifier for this job run
        metadata: Optional additional metadata to store with the completion
        
    Returns:
        Thread: The background thread handling the API call
        
    Example:
        post_finished("Training", "run_123", {"accuracy": 0.95, "loss": 0.05})
    """
    payload_metadata = {
        "job_description": job_description,
        "finished": True
    }
    
    if metadata:
        payload_metadata.update(metadata)
    
    payload = {
        "metadata": payload_metadata,
        "run_external_id": run_external_id
    }
    
    thread = threading.Thread(target=_send_update, args=(payload,), daemon=True)
    thread.start()
    return thread


def post_crashed(
    job_description: str,
    run_external_id: str,
    error: Optional[str] = None
) -> threading.Thread:
    """
    Mark a job as crashed/failed (non-blocking).
    
    Args:
        job_description: Human-readable description of the job
        run_external_id: Unique identifier for this job run
        error: Optional error message or exception details
        
    Returns:
        Thread: The background thread handling the API call
        
    Example:
        try:
            # Your code...
        except Exception as e:
            post_crashed("Training", "run_123", str(e))
            raise
    """
    payload_metadata = {
        "job_description": job_description,
        "crashed": True
    }
    
    if error:
        payload_metadata["error"] = error
    
    payload = {
        "metadata": payload_metadata,
        "run_external_id": run_external_id
    }
    
    thread = threading.Thread(target=_send_update, args=(payload,), daemon=True)
    thread.start()
    return thread


# Example usage
if __name__ == "__main__":
    # Configure the SDK
    configure(
        api_key="your-api-key-here",
        bar_id="your-bar-id-here"
    )
    
    # Example: Track a simple job
    run_id = "example_run_001"
    
    # Start the job
    post_started("Example Job", run_id)
    
    # Report progress
    for i in range(0, 101, 20):
        post_progress("Example Job", run_id, i, 100, stage_name="processing")
        # Simulate work
        import time
        time.sleep(1)
    
    # Mark as complete
    post_finished("Example Job", run_id, {"status": "success", "items_processed": 1000})
