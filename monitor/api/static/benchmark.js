// benchmark.js - Benchmark control functions

function selectBenchType(type) {
    selectedBenchType = type;
    // Reload baseline when benchmark type changes
    loadBaseline();
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === type);
    });
    
    // Update description
    const descriptions = {
        'gemm': 'Dense matrix multiplication for maximum GPU compute stress. Measures TFLOPS.',
        'particle': '2D particle physics simulation with millions of particles. Measures steps/second.'
    };
    document.getElementById('type-description').textContent = descriptions[type] || '';
    
    // Show/hide type-specific settings in custom mode
    document.getElementById('gemm-settings').style.display = type === 'gemm' ? 'block' : 'none';
    document.getElementById('particle-settings').style.display = type === 'particle' ? 'block' : 'none';
    
    // Simulation button is always enabled
}

function selectMode(mode) {
    selectedMode = mode;
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    document.getElementById('custom-controls').style.display = mode === 'custom' ? 'block' : 'none';
    
    // Disable Start Simulation button for stress-test and custom modes
    // (or if GPU features not available - checked by loadFeatures)
    const simBtn = document.getElementById('start-sim-btn');
    if (simBtn) {
        if (mode === 'stress-test' || mode === 'custom') {
            simBtn.disabled = true;
            simBtn.style.opacity = '0.5';
            simBtn.style.cursor = 'not-allowed';
        } else {
            // Only enable if not already disabled by loadFeatures
            // Check if it's disabled due to missing GPU libraries
            if (simBtn.title !== 'Install CuPy or PyTorch for simulation') {
                simBtn.disabled = false;
                simBtn.style.opacity = '1';
                simBtn.style.cursor = 'pointer';
            }
        }
    }
    
    // Update mode description
    const descriptions = {
        'quick': 'Quick baseline test - 15 seconds with fixed workload size',
        'standard': 'Standard benchmark - 60 seconds with fixed workload size',
        'extended': 'Extended burn-in test - 180 seconds with fixed workload size for thorough validation',
        'stress-test': 'Stress test - 60 seconds with AUTO-SCALING workload that dynamically increases to push GPU to 98% utilization',
        'custom': 'Custom configuration - set your own duration, limits, and workload parameters'
    };
    document.getElementById('mode-description').textContent = descriptions[mode] || '';
}

function updateSliderValue(type) {
    const slider = document.getElementById('custom-' + type);
    const input = document.getElementById('custom-' + type + '-val');
    input.value = slider.value;
}

async function startBenchmark() {
    const btn = document.getElementById('start-bench-btn');
    const stopBtn = document.getElementById('stop-bench-btn');
    btn.disabled = true;
    btn.textContent = 'Running...';
    stopBtn.style.display = 'inline-block';
    
    document.getElementById('benchmark-progress').style.display = 'block';
    document.getElementById('benchmark-live-charts').style.display = 'block';
    document.getElementById('benchmark-results').innerHTML = '';
    document.getElementById('bench-stop-reason').textContent = '';
    document.getElementById('iteration-counter').style.display = 'inline';
    document.getElementById('iteration-counter').textContent = 'Iteration #0';
    
    // Build URL with params
    let url = '/api/benchmark/start?benchmark_type=' + selectedBenchType;
    
    // Handle different modes
    if (selectedMode === 'quick') {
        url += '&mode=fixed&duration=15&auto_scale=false';
    } else if (selectedMode === 'standard') {
        url += '&mode=fixed&duration=60&auto_scale=false';
    } else if (selectedMode === 'stress-test') {
        url += '&mode=stress&duration=60&auto_scale=true';
    } else if (selectedMode === 'extended') {
        url += '&mode=fixed&duration=180&auto_scale=false';
    } else if (selectedMode === 'custom') {
        url += '&mode=custom&auto_scale=false';
        url += '&duration=' + document.getElementById('custom-duration-val').value;
        url += '&temp_limit=' + document.getElementById('custom-temp-val').value;
        url += '&memory_limit=' + document.getElementById('custom-memory-val').value;
        url += '&power_limit=' + document.getElementById('custom-power-val').value;
        if (selectedBenchType === 'gemm') {
            url += '&matrix_size=' + document.getElementById('custom-matrix-val').value;
        } else if (selectedBenchType === 'particle') {
            const particles = Math.round(parseFloat(document.getElementById('custom-particles-val').value) * 1000000);
            url += '&num_particles=' + particles;
        }
    }
    
    // Initialize live charts
    initLiveCharts();
    
    try {
        await fetch(url, { method: 'POST' });
        benchmarkPollInterval = setInterval(pollBenchmarkStatus, 500);
    } catch (error) {
        console.error('Error starting benchmark:', error);
        btn.disabled = false;
        btn.textContent = 'Start Benchmark';
        stopBtn.style.display = 'none';
    }
}

async function stopBenchmark() {
    try {
        await fetch('/api/benchmark/stop', { method: 'POST' });
    } catch (error) {
        console.error('Error stopping benchmark:', error);
    }
}

async function pollBenchmarkStatus() {
    try {
        const response = await fetch('/api/benchmark/status');
        const data = await response.json();
        
        if (data.status === 'idle') {
            clearInterval(benchmarkPollInterval);
            const btn = document.getElementById('start-bench-btn');
            const simBtn = document.getElementById('start-sim-btn');
            const stopBtn = document.getElementById('stop-bench-btn');
            btn.disabled = false;
            btn.textContent = 'Start Benchmark';
            simBtn.disabled = false;
            simBtn.textContent = 'Start Simulation';
            stopBtn.style.display = 'none';
            document.getElementById('benchmark-progress').style.display = 'none';
            
            if (data.stop_reason) {
                document.getElementById('bench-stop-reason').textContent = data.stop_reason;
            }
        } else if (data.status === 'running') {
            // Update progress percentage
            if (data.progress !== undefined) {
                document.getElementById('bench-progress-bar').style.width = data.progress + '%';
                document.getElementById('bench-percent').textContent = data.progress + '%';
            }
            
            // Update iteration counter
            if (data.current_iteration !== undefined) {
                const iterElement = document.getElementById('iteration-counter');
                if (iterElement) {
                    iterElement.style.display = 'inline';
                    iterElement.textContent = `Iteration #${data.current_iteration}`;
                }
            }
            
            // Update workload type
            if (data.workload_type) {
                const workloadElement = document.getElementById('workload-info');
                const benchWorkloadElement = document.getElementById('bench-workload');
                if (workloadElement) {
                    workloadElement.textContent = 'Workload: ' + data.workload_type;
                }
                if (benchWorkloadElement) {
                    benchWorkloadElement.textContent = data.workload_type;
                }
            }
            
            // Update live charts with latest metrics
            if (data.latest_metrics) {
                updateLiveCharts(data.latest_metrics);
            }
        }
    } catch (error) {
        console.error('Error polling benchmark status:', error);
    }
}

function displayBenchmarkResults(results) {
    const resultsDiv = document.getElementById('benchmark-results');
    resultsDiv.innerHTML = '<h3>Benchmark Results</h3>';
    
    // Build results HTML based on benchmark type
    let html = '<div class="results-grid">';
    
    if (results.benchmark_type === 'gemm') {
        html += `
            <div class="result-card">
                <div class="result-label">Average TFLOPS</div>
                <div class="result-value">${results.avg_tflops.toFixed(2)}</div>
            </div>
            <div class="result-card">
                <div class="result-label">Peak TFLOPS</div>
                <div class="result-value">${results.peak_tflops.toFixed(2)}</div>
            </div>
        `;
    } else if (results.benchmark_type === 'particle') {
        html += `
            <div class="result-card">
                <div class="result-label">Avg Steps/Sec</div>
                <div class="result-value">${results.avg_steps_per_sec ? results.avg_steps_per_sec.toFixed(2) : 'N/A'}</div>
            </div>
            <div class="result-card">
                <div class="result-label">Peak Steps/Sec</div>
                <div class="result-value">${results.peak_steps_per_sec ? results.peak_steps_per_sec.toFixed(2) : 'N/A'}</div>
            </div>
        `;
    }
    
    // Common metrics
    html += `
        <div class="result-card">
            <div class="result-label">Avg Temperature</div>
            <div class="result-value">${results.avg_temperature.toFixed(1)}°C</div>
        </div>
        <div class="result-card">
            <div class="result-label">Peak Temperature</div>
            <div class="result-value">${results.peak_temperature.toFixed(1)}°C</div>
        </div>
        <div class="result-card">
            <div class="result-label">Avg GPU Utilization</div>
            <div class="result-value">${results.avg_gpu_utilization.toFixed(1)}%</div>
        </div>
        <div class="result-card">
            <div class="result-label">Avg Memory Usage</div>
            <div class="result-value">${results.avg_memory_usage.toFixed(1)}%</div>
        </div>
        <div class="result-card">
            <div class="result-label">Avg Power Draw</div>
            <div class="result-value">${results.avg_power_draw.toFixed(1)}W</div>
        </div>
        <div class="result-card">
            <div class="result-label">Duration</div>
            <div class="result-value">${results.duration.toFixed(1)}s</div>
        </div>
        <div class="result-card">
            <div class="result-label">Iterations</div>
            <div class="result-value">${results.total_iterations}</div>
        </div>
    `;
    
    html += '</div>';
    resultsDiv.innerHTML += html;
}

function exportData(format) {
    if (format === 'json') {
        fetch('/api/metrics/export/json')
            .then(r => r.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'metrics.json';
                a.click();
            });
    } else if (format === 'csv') {
        fetch('/api/metrics/export/csv')
            .then(r => r.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'metrics.csv';
                a.click();
            });
    }
}

async function loadBaseline() {
    try {
        const response = await fetch('/api/benchmark/baseline?benchmark_type=' + selectedBenchType);
        const baseline = await response.json();
        if (baseline && baseline.status !== 'no_baseline') {
            document.getElementById('baseline-info').style.display = 'block';
            const benchTypeLabel = baseline.benchmark_type === 'gemm' ? 'GEMM' : 'Particle';
            const runModeLabel = baseline.run_mode === 'simulation' ? ' (Simulation)' : ' (Benchmark)';
            document.getElementById('baseline-details').innerHTML = `
                <div class="metric-row"><span class="metric-label">GPU</span><span class="metric-value">${baseline.gpu_name}</span></div>
                <div class="metric-row"><span class="metric-label">Type</span><span class="metric-value">${benchTypeLabel}${runModeLabel}</span></div>
                <div class="metric-row"><span class="metric-label">Iterations</span><span class="metric-value">${baseline.iterations_completed}</span></div>
                <div class="metric-row"><span class="metric-label">Avg Iteration</span><span class="metric-value">${baseline.avg_iteration_time_ms.toFixed(2)} ms</span></div>
                <div class="metric-row"><span class="metric-label">Avg Temp</span><span class="metric-value">${baseline.avg_temperature.toFixed(1)} C</span></div>
                <p style="font-size: 0.85em; color: var(--text-secondary); margin-top: 10px;">Saved: ${new Date(baseline.timestamp).toLocaleString()}</p>
            `;
        } else {
            document.getElementById('baseline-info').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading baseline:', error);
    }
}
