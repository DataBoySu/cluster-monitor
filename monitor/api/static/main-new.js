// main.js - Main initialization and tab handling
// All functions are now modularized across simulation.js, benchmark.js, charts.js, and utils.js

// Global variables
let countdown = 5;
let historyChart = null;
let benchmarkPollInterval = null;
let benchCharts = {};
let selectedMode = 'quick';
let selectedBenchType = 'gemm';

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
        
        if (tab.dataset.tab === 'history') loadHistory();
        if (tab.dataset.tab === 'processes') loadProcesses();
        if (tab.dataset.tab === 'benchmark') { loadBenchmarkResults(); loadBaseline(); }
    });
});

// Sync input to slider for custom controls
['duration', 'temp', 'memory', 'power', 'matrix', 'particles'].forEach(type => {
    const input = document.getElementById('custom-' + type + '-val');
    if (input) {
        input.addEventListener('change', () => {
            document.getElementById('custom-' + type).value = input.value;
        });
    }
});

// Fetch and update dashboard status
async function fetchStatus() {
    try {
        console.log('Fetching status from /api/status...');
        const response = await fetch('/api/status');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Received data:', data);
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching status:', error);
        document.getElementById('gpu-list').innerHTML = '<div class="gpu-card" style="color: #ef4444;">Error: Failed to fetch GPU data. Check console for details.</div>';
        document.getElementById('system-info').innerHTML = '<div style="color: #ef4444;">Error loading system info</div>';
    }
}

async function loadBenchmarkResults() {
    try {
        const response = await fetch('/api/benchmark/results');
        const results = await response.json();
        if (results && results.status !== 'no_results') {
            displayBenchmarkResults(results);
        }
    } catch (error) {
        console.error('Error loading benchmark results:', error);
    }
}

async function shutdownServer() {
    if (!confirm('Are you sure you want to exit? This will stop the server and close the application.')) {
        return;
    }
    
    const btn = document.getElementById('shutdown-btn');
    btn.disabled = true;
    btn.textContent = 'Shutting down...';
    
    try {
        await fetch('/api/shutdown', { method: 'POST' });
        document.body.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100vh; flex-direction: column; background: var(--bg-primary); color: var(--text-primary);"><h1>Server Shutting Down</h1><p>You can close this window now.</p></div>';
    } catch (error) {
        // Server shut down, connection closed - this is expected
        document.body.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100vh; flex-direction: column; background: var(--bg-primary); color: var(--text-primary);"><h1>Server Shut Down</h1><p>You can close this window now.</p></div>';
    }
}

// Initialize dashboard
fetchStatus();
setInterval(fetchStatus, 5000);

// Initialize benchmark tab
selectBenchType('gemm');
selectMode('quick');

console.log('Dashboard initialized - all modules loaded');
