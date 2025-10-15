// Main application JavaScript

let pollInterval = null;
let isRunning = false;

// DOM Elements
const startBtn = document.getElementById('startBtn');
const resetBtn = document.getElementById('resetBtn');
const progressElement = document.getElementById('progress');
const remainingElement = document.getElementById('remaining');
const elapsedElement = document.getElementById('elapsed');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const statusMessage = document.getElementById('statusMessage');

// Format time in seconds to readable format
function formatTime(seconds) {
    if (!seconds || seconds < 0) return '--';
    
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
}

// Update UI with progress data
function updateUI(data) {
    const progress = Math.round(data.progress);
    
    progressElement.textContent = `${progress}%`;
    elapsedElement.textContent = formatTime(data.elapsed);
    remainingElement.textContent = formatTime(data.estimated_remaining);
    
    progressBar.style.width = `${progress}%`;
    progressText.textContent = `${progress}% Complete`;
    
    if (data.status === 'completed') {
        statusMessage.textContent = '✅ Generation completed successfully!';
        statusMessage.style.background = '#d4edda';
        statusMessage.style.color = '#155724';
        stopPolling();
        startBtn.style.display = 'none';
        resetBtn.style.display = 'inline-block';
    } else if (data.status === 'running') {
        statusMessage.textContent = '⚡ Generating data...';
        statusMessage.style.background = '#d1ecf1';
        statusMessage.style.color = '#0c5460';
    }
    
    // Update Predictabar React component if available
    if (window.updatePredictabar) {
        window.updatePredictabar({
            progress: progress,
            estimated_remaining: data.estimated_remaining,
            status: data.status
        });
    }
}

// Poll for progress updates
function startPolling() {
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/progress');
            const data = await response.json();
            updateUI(data);
        } catch (error) {
            console.error('Error fetching progress:', error);
        }
    }, 500); // Poll every 500ms
}

function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
    isRunning = false;
}

// Start generation
async function startGeneration() {
    try {
        startBtn.disabled = true;
        statusMessage.textContent = '🚀 Starting generation...';
        
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            isRunning = true;
            startPolling();
        } else {
            throw new Error('Failed to start generation');
        }
    } catch (error) {
        console.error('Error starting generation:', error);
        statusMessage.textContent = '❌ Failed to start generation';
        statusMessage.style.background = '#f8d7da';
        statusMessage.style.color = '#721c24';
        startBtn.disabled = false;
    }
}

// Reset
function reset() {
    stopPolling();
    progressElement.textContent = '0%';
    remainingElement.textContent = '--';
    elapsedElement.textContent = '0s';
    progressBar.style.width = '0%';
    progressText.textContent = 'Ready to start';
    statusMessage.textContent = 'Click "Start Generation" to begin';
    statusMessage.style.background = '#f8f9fa';
    statusMessage.style.color = '#666';
    startBtn.disabled = false;
    startBtn.style.display = 'inline-block';
    resetBtn.style.display = 'none';
}

// Event listeners
startBtn.addEventListener('click', startGeneration);
resetBtn.addEventListener('click', reset);

// Initialize Predictabar React component
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Predictabar widget...');
    console.log('React available:', !!window.React);
    console.log('ReactDOM available:', !!window.ReactDOM);
    console.log('Predictabar available:', !!window.Predictabar);
    
    const widgetContainer = document.getElementById('predictabar-widget');
    const fallbackContainer = document.getElementById('fallback-progress');
    
    // Check if React and Predictabar are available
    if (window.React && window.ReactDOM && window.Predictabar) {
        try {
            console.log('✅ All dependencies loaded, creating widget...');
            
            // Create Predictabar React component
            const { Predictabar } = window.Predictabar;
            
            // Create a simple wrapper component
            const PredictabarWrapper = () => {
                const [progress, setProgress] = React.useState(0);
                const [status, setStatus] = React.useState('idle');
                const [estimatedTime, setEstimatedTime] = React.useState(null);
                
                // Listen for progress updates
                React.useEffect(() => {
                    const updateProgress = (data) => {
                        console.log('📊 Updating Predictabar:', data);
                        setProgress(data.progress || 0);
                        setStatus(data.status || 'idle');
                        setEstimatedTime(data.estimated_remaining || null);
                    };
                    
                    // Store the update function globally
                    window.updatePredictabar = updateProgress;
                }, []);
                
                return React.createElement(Predictabar, {
                    progress: progress,
                    status: status,
                    estimatedTime: estimatedTime
                });
            };
            
            // Render the component
            const root = ReactDOM.createRoot(widgetContainer);
            root.render(React.createElement(PredictabarWrapper));
            
            console.log('✅ Predictabar React component initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing Predictabar:', error);
            // Show fallback UI
            widgetContainer.style.display = 'none';
            fallbackContainer.style.display = 'block';
        }
    } else {
        console.log('⚠️ Missing dependencies - using fallback UI');
        console.log('React:', !!window.React);
        console.log('ReactDOM:', !!window.ReactDOM);
        console.log('Predictabar:', !!window.Predictabar);
        // Show fallback UI
        widgetContainer.style.display = 'none';
        fallbackContainer.style.display = 'block';
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopPolling();
});

