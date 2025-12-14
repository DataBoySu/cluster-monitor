// benchmark.js - (disabled) Benchmark control functions
// The original benchmark UI/logic is intentionally disabled. Functions remain defined as no-ops
// so the rest of the application doesn't throw errors when referencing them.

let benchUserChangeTs = 0;
const BENCH_PREVIEW_GUARD_MS = 4000;

function selectBenchType(type) {
    // disabled: original implementation commented out
    console.debug('selectBenchType called but benchmark UI is disabled');
    selectedBenchType = type;
}

function selectMode(mode) {
    console.debug('selectMode called but benchmark UI is disabled');
    selectedMode = mode;
}

function updateWorkloadPreview(){
    // no-op while benchmark UI is disabled
    try {
        const el = document.getElementById('workload-info');
        if (el) el.textContent = 'Benchmark UI disabled';
    } catch(e){}
}

function initBackendDropdown(){
    try { window.selectedBackend = window.selectedBackend || 'auto'; } catch(e){}
}

function updateSliderValue(type) { /* placeholder kept for compatibility */ }

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
        const msg = error && error.message ? error.message : String(error);
        if (typeof window !== 'undefined' && window.showError) {
            window.showError('Error loading baseline: ' + msg);
        } else {
            console.error('Error loading baseline:', error);
        }
    }
}
