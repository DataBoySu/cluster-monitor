// Canonical dashboard script: keep this file as `main.js`.
// (Any legacy or duplicate files such as `main-new.js` were removed.)
// Canonical dashboard script: keep this file as `main.js`.
// (Any legacy or duplicate files such as `main-new.js` were removed.)
let countdown = 5;
let refreshInterval = null; // handle for the main auto-refresh interval
let historyChart = null;
// History chart state for zoom/highlight
let historyOriginalLabels = [];
let historyOriginalData = [];
let historyVisibleStart = 0;
let historyVisibleEnd = 0;
let historyDayStarts = []; // indices where each day starts
let historySelectedDay = null; // index into historyDayStarts

function ensureZoomPlugin() {
    try {
        if (typeof Chart === 'undefined') return;
        // check registry for a plugin with id 'zoom'
        const regs = (Chart && Chart.registry && Chart.registry.plugins && Chart.registry.plugins.items) ? Chart.registry.plugins.items : null;
        if (regs && regs.some(p => p && p.id === 'zoom')) return;
        const candidate = window['chartjsPluginZoom'] || window['ChartZoom'] || window['chartjs-plugin-zoom'];
        if (candidate) {
            Chart.register(candidate);
            console.debug('chartjs zoom plugin registered at runtime');
        }
    } catch (e) { console.debug('ensureZoomPlugin error', e); }
}

// Notifications are provided by /static/toast.js (loaded before main.js)

function showRestartSuccessPage() {
    try {
        // stop intervals
        try { if (refreshInterval) clearInterval(refreshInterval); } catch (e) {}
        try { if (benchmarkPollInterval) clearInterval(benchmarkPollInterval); } catch (e) {}

        document.documentElement.style.height = '100%';
        document.body.style.margin = '0';
        document.body.innerHTML = `
            <div style="display:flex;align-items:center;justify-content:center;height:100vh;background:#062b00;color:#d1fae5;font-family:Roboto,Segoe UI,Arial,sans-serif;">
                <div style="text-align:center;max-width:720px;padding:24px;">
                    <h1 style="font-size:38px;margin-bottom:12px;color:#bbf7d0;">Server restarted successfully</h1>
                    <p style="color:#bbf7d0;margin-bottom:18px;">The server restart was initiated with elevated privileges. If the UI does not reconnect automatically, refresh this page after a few seconds.</p>
                    <div style="display:flex;gap:8px;justify-content:center;">
                        <button onclick="location.reload()" style="padding:10px 16px;border-radius:6px;border:none;background:#0b6623;color:#fff;cursor:pointer;">Refresh</button>
                        <button onclick="window.close()" style="padding:10px 16px;border-radius:6px;border:1px solid rgba(255,255,255,0.1);background:transparent;color:#d1fae5;cursor:pointer;">Close Window</button>
                    </div>
                </div>
            </div>
        `;
    } catch (e) { console.debug('showRestartSuccessPage error', e); }
}

// Shutdown helper called by the Exit button in the header
async function shutdownServer() {
    try {
        const ok = await showConfirmShutdownDialog();
        if (!ok) return;
        const btn = document.getElementById('shutdown-btn');
        if (btn) { btn.disabled = true; btn.textContent = 'Shutting down...'; }

        // Show a transient modal while we send the shutdown request
        const modal = createShutdownModal('Sending shutdown request...');
        // Attempt to POST shutdown. If the POST fails (server killed before responding)
        // fall back to polling to detect that the server has gone away.
        try {
            const res = await fetch('/api/shutdown', { method: 'POST' });
            if (!res.ok) {
                const txt = await res.text().catch(() => res.statusText || 'Error');
                modal.setText('Shutdown failed: ' + txt);
                if (typeof showError === 'function') showError('Shutdown failed: ' + txt);
                if (btn) { btn.disabled = false; btn.textContent = 'Exit'; }
                setTimeout(() => modal.remove(), 4000);
                return;
            }

            // Server accepted shutdown request — update modal then proceed
            modal.setText('Server is shutting down...');
            try { await waitMs(600); } catch (e) {}
            try { modal.remove(); } catch (e) {}

            try { showServerShutdownPage(); } catch (e) { console.debug('showServerShutdownPage error', e); }
            const stopped = await waitForServerStop(60, 1000);
            if (stopped) {
                showServerStoppedPage(true);
            } else {
                showServerStoppedPage(false);
            }
            return;
        } catch (postErr) {
            // Network error when posting — server may have terminated before sending a response.
            // Immediately proceed to the final page rather than showing an intermediate "waiting" message.
            try { modal.remove(); } catch (e) {}
            // Show final stopped page (assume server is stopping/has stopped)
            try { showServerStoppedPage(true); } catch (e) { console.debug('showServerStoppedPage error', e); }
            return;
        }
    } catch (e) {
        // Final note: ensure Exit button uses server shutdown flow. (index.html already wired to shutdownServer())
        if (typeof showError === 'function') showError('Error sending shutdown: ' + (e && e.message ? e.message : e));
        const btn = document.getElementById('shutdown-btn');
        if (btn) { btn.disabled = false; btn.textContent = 'Exit'; }
    }
}

// Modal helper used for shutdown flow
function createShutdownModal(initialText) {
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.left = '0';
    overlay.style.top = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    overlay.style.background = 'rgba(0,0,0,0.45)';
    overlay.style.zIndex = '10000';

    const card = document.createElement('div');
    card.style.background = 'var(--bg-secondary)';
    card.style.color = 'var(--text-primary)';
    card.style.padding = '18px 22px';
    card.style.borderRadius = '10px';
    card.style.boxShadow = '0 8px 24px rgba(0,0,0,0.4)';
    card.style.minWidth = '280px';
    card.style.textAlign = 'center';

    const msg = document.createElement('div');
    msg.textContent = initialText || '';
    msg.style.marginBottom = '10px';

    const spinner = document.createElement('div');
    spinner.style.width = '28px';
    spinner.style.height = '28px';
    spinner.style.border = '4px solid rgba(255,255,255,0.15)';
    spinner.style.borderTopColor = 'var(--accent-blue)';
    spinner.style.borderRadius = '50%';
    spinner.style.margin = '0 auto';
    spinner.style.animation = 'spin 1s linear infinite';

    card.appendChild(msg);
    card.appendChild(spinner);
    overlay.appendChild(card);
    document.body.appendChild(overlay);

    // Add simple keyframes if not present
    if (!document.getElementById('shutdown-spin-style')) {
        const style = document.createElement('style');
        style.id = 'shutdown-spin-style';
        style.textContent = '@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}';
        document.head.appendChild(style);
    }

    return {
        setText: (t) => { msg.textContent = t; },
        remove: () => { try { if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay); } catch (e) {} }
    };
}

// Custom confirmation dialog for shutdown (returns Promise<boolean>)
function showConfirmShutdownDialog() {
    return new Promise(resolve => {
        const overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.left = '0';
        overlay.style.top = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.background = 'rgba(0,0,0,0.45)';
        overlay.style.zIndex = '10000';

        const card = document.createElement('div');
        card.style.background = 'var(--bg-secondary)';
        card.style.color = 'var(--text-primary)';
        card.style.padding = '18px 22px';
        card.style.borderRadius = '10px';
        card.style.boxShadow = '0 8px 24px rgba(0,0,0,0.4)';
        card.style.minWidth = '320px';
        card.style.textAlign = 'center';

        const title = document.createElement('div');
        title.textContent = 'Confirm Shutdown';
        title.style.fontWeight = '700';
        title.style.marginBottom = '8px';

        const msg = document.createElement('div');
        msg.textContent = 'Are you sure you want to shutdown the server? This will stop the process.';
        msg.style.marginBottom = '14px';
        msg.style.color = 'var(--text-secondary)';

        const actions = document.createElement('div');
        actions.style.display = 'flex';
        actions.style.justifyContent = 'center';
        actions.style.gap = '10px';

        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = 'Cancel';
        cancelBtn.style.padding = '8px 12px';
        cancelBtn.style.borderRadius = '6px';
        cancelBtn.style.border = '1px solid var(--border-color)';
        cancelBtn.style.background = 'transparent';
        cancelBtn.style.color = 'var(--text-primary)';
        cancelBtn.onclick = () => { try { overlay.remove(); } catch (e){}; resolve(false); };

        const shutdownBtn = document.createElement('button');
        shutdownBtn.textContent = 'Shutdown Server';
        shutdownBtn.style.padding = '8px 12px';
        shutdownBtn.style.borderRadius = '6px';
        shutdownBtn.style.border = 'none';
        shutdownBtn.style.background = 'var(--accent-red)';
        shutdownBtn.style.color = '#fff';
        shutdownBtn.onclick = () => { try { overlay.remove(); } catch (e){}; resolve(true); };

        actions.appendChild(cancelBtn);
        actions.appendChild(shutdownBtn);

        card.appendChild(title);
        card.appendChild(msg);
        card.appendChild(actions);
        overlay.appendChild(card);
        document.body.appendChild(overlay);
    });
}

// Show a full-page server shutdown message (used after server accepts the shutdown)
function showServerShutdownPage() {
    // Stop periodic refresh and benchmark polling
    try { if (refreshInterval) clearInterval(refreshInterval); } catch (e) {}
    try { if (benchmarkPollInterval) clearInterval(benchmarkPollInterval); } catch (e) {}
    try { if (typeof stopBenchmark === 'function') stopBenchmark(); } catch (e) {}

    document.documentElement.style.height = '100%';
    document.body.style.margin = '0';
    document.body.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;height:100vh;background:var(--bg-primary);color:var(--text-primary);font-family:Roboto,Segoe UI,Arial,sans-serif;">
            <div style="text-align:center;max-width:720px;padding:24px;">
                <h1 style="font-size:34px;margin-bottom:12px;">Server Shutting Down</h1>
                <p style="color:var(--text-secondary);margin-bottom:18px;">The server has accepted the shutdown request and is terminating. You can close this window or keep it open to see when the server stops responding.</p>
                <p style="color:var(--text-secondary);margin-bottom:24px;">If you started this server in a terminal, it will stop shortly.</p>
                <div style="display:flex;gap:8px;justify-content:center;">
                    <button onclick="location.reload()" style="padding:8px 14px;border-radius:6px;border:none;background:var(--accent-blue);color:#fff;cursor:pointer;">Refresh</button>
                    <button onclick="window.close()" style="padding:8px 14px;border-radius:6px;border:1px solid var(--border-color);background:transparent;color:var(--text-primary);cursor:pointer;">Close Window</button>
                </div>
            </div>
        </div>
    `;
}

// Wait until the server stops responding to /api/status or until timeout.
// timeoutSeconds: total seconds to wait; intervalMs: poll interval in ms.
async function waitForServerStop(timeoutSeconds = 60, intervalMs = 1000) {
    const attempts = Math.max(1, Math.ceil((timeoutSeconds * 1000) / intervalMs));
    for (let i = 0; i < attempts; i++) {
        try {
            // short fetch with small timeout via AbortController
            const controller = new AbortController();
            const to = setTimeout(() => controller.abort(), Math.min(intervalMs, 2000));
            const resp = await fetch('/api/status', { signal: controller.signal });
            clearTimeout(to);
            // If we got a valid response, server still up — wait and retry
            if (!resp.ok) {
                // treat non-ok as server error; continue polling because shutdown may return 5xx then stop
            }
        } catch (e) {
            // fetch threw — likely network error / server went away
            return true;
        }
        // wait before next attempt
        await waitMs(intervalMs);
    }
    return false;
}

// Show final page when server is confirmed stopped (or timed out waiting)
function showServerStoppedPage(serverStopped = true) {
    try {
        try { if (refreshInterval) clearInterval(refreshInterval); } catch (e) {}
        try { if (benchmarkPollInterval) clearInterval(benchmarkPollInterval); } catch (e) {}
        try { if (typeof stopBenchmark === 'function') stopBenchmark(); } catch (e) {}

        document.documentElement.style.height = '100%';
        document.body.style.margin = '0';
        document.body.innerHTML = `
            <div style="display:flex;align-items:center;justify-content:center;height:100vh;background:var(--bg-primary);color:var(--text-primary);font-family:Roboto,Segoe UI,Arial,sans-serif;">
                <div style="text-align:center;max-width:720px;padding:24px;">
                    <h1 style="font-size:48px;margin-bottom:12px;">Server Shut down</h1>
                    <p style="color:var(--text-secondary);font-size:18px;margin-bottom:18px;">${serverStopped ? 'It is now safe to close this window.' : 'Server appears unreachable. You can close this window or try refreshing later.'}</p>
                    <div style="display:flex;gap:8px;justify-content:center;">
                        <button onclick="location.reload()" style="padding:10px 16px;border-radius:6px;border:none;background:var(--accent-blue);color:#fff;cursor:pointer;">Refresh</button>
                        <button onclick="window.close()" style="padding:10px 16px;border-radius:6px;border:1px solid var(--border-color);background:transparent;color:var(--text-primary);cursor:pointer;">Close Window</button>
                    </div>
                </div>
            </div>
        `;
    } catch (e) { console.debug('showServerStoppedPage error', e); }
}

// Show client-side shutdown sequence (do NOT kill the server process).
function showShutdownSequence() {
    try {
        // Stop periodic refresh and benchmark polling
        try { if (refreshInterval) clearInterval(refreshInterval); } catch (e) {}
        try { if (benchmarkPollInterval) clearInterval(benchmarkPollInterval); } catch (e) {}

        // Attempt to stop any running benchmark gracefully via existing handler
        try { if (typeof stopBenchmark === 'function') stopBenchmark(); } catch (e) {}

        // Replace entire body with shutdown message (client-only)
        document.documentElement.style.height = '100%';
        document.body.style.margin = '0';
        document.body.innerHTML = `
            <div style="display:flex;align-items:center;justify-content:center;height:100vh;background:var(--bg-primary);color:var(--text-primary);font-family:Roboto,Segoe UI,Arial,sans-serif;">
                <div style="text-align:center;max-width:720px;padding:24px;">
                    <h1 style="font-size:32px;margin-bottom:12px;">Dashboard Closed</h1>
                    <p style="color:var(--text-secondary);margin-bottom:18px;">The web dashboard has been closed in this browser tab. You can safely close this tab or navigate away.</p>
                    <div style="display:flex;gap:8px;justify-content:center;">
                        <button onclick="location.reload()" style="padding:8px 14px;border-radius:6px;border:none;background:var(--accent-blue);color:#fff;cursor:pointer;">Reopen Dashboard</button>
                        <button onclick="window.close()" style="padding:8px 14px;border-radius:6px;border:1px solid var(--border-color);background:transparent;color:var(--text-primary);cursor:pointer;">Close Window</button>
                    </div>
                </div>
            </div>
        `;
    } catch (e) {
        console.debug('showShutdownSequence failed', e);
    }
}

function zoomIn() { adjustZoom(1.5); }
function zoomOut() { adjustZoom(1/1.5); }
function resetZoom() { historyVisibleStart = 0; historyVisibleEnd = historyOriginalLabels.length-1; renderHistoryView(); }

function adjustZoom(factor) {
    const len = historyOriginalLabels.length;
    if (!len) return;
    const curLen = historyVisibleEnd - historyVisibleStart + 1;
    let newLen = Math.max(10, Math.round(curLen / factor));
    if (newLen >= len) { resetZoom(); return; }
    const center = Math.floor((historyVisibleStart + historyVisibleEnd)/2);
    let start = Math.max(0, center - Math.floor(newLen/2));
    let end = Math.min(len-1, start + newLen -1);
    if (end - start + 1 < newLen) start = Math.max(0, end - newLen +1);
    historyVisibleStart = start; historyVisibleEnd = end; renderHistoryView();
}

function highlightSelectedDay(val) {
    const idx = val === '' ? null : parseInt(val);
    historySelectedDay = isNaN(idx) ? null : idx;
    renderHistoryView();
}

function renderHistoryView(){
    if (!historyChart) return;
    // With time-scale charts we keep the full dataset on the chart and let
    // the zoom/pan plugin control the visible window. For highlight changes
    // simply update the chart to redraw overlays.
    historyChart.update('none');
}

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

function updateDashboard(data) {
    console.log('Updating dashboard with:', data);
    const badge = document.getElementById('status-badge');
    // Display 'warning' state from server as 'idle' in UI while leaving alerts untouched
    const displayStatus = (data.status === 'warning') ? 'idle' : (data.status || 'unknown');
    badge.className = 'status-badge status-' + displayStatus;
    badge.textContent = displayStatus.toUpperCase();

    // Add tooltip with alert count (keep original alert logic based on server status)
    const alertCount = data.alerts ? data.alerts.length : 0;
    if (data.status === 'warning' && alertCount > 0) {
        badge.setAttribute('data-tooltip', `${alertCount} active alert${alertCount > 1 ? 's' : ''}`);
    } else if (displayStatus === 'info') {
        badge.setAttribute('data-tooltip', 'System information available');
    } else {
        badge.setAttribute('data-tooltip', 'All systems operational');
    }
    
    const gpuList = document.getElementById('gpu-list');
    gpuList.innerHTML = data.metrics.gpus.map(gpu => {
        if (gpu.error) return `<div class="gpu-card">Error: ${gpu.error}</div>`;
        
        const util = gpu.utilization || 0;
        const memPct = gpu.memory_total > 0 ? (gpu.memory_used / gpu.memory_total * 100) : 0;
        const temp = gpu.temperature || 0;
        
        return `
            <div class="gpu-card">
                <div class="gpu-header">
                    <span class="gpu-name">GPU ${gpu.index}: ${gpu.name}</span>
                    <span class="gpu-temp ${temp > 80 ? 'hot' : ''}">${temp}C</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Utilization</span>
                    <span class="metric-value">${util}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${util > 90 ? 'crit' : util > 70 ? 'warn' : ''}" style="width: ${util}%"></div>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Memory</span>
                    <span class="metric-value">${(gpu.memory_used/1024).toFixed(1)}/${(gpu.memory_total/1024).toFixed(1)} GB</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${memPct > 90 ? 'crit' : memPct > 70 ? 'warn' : ''}" style="width: ${memPct}%"></div>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Power</span>
                    <span class="metric-value">${(gpu.power || 0).toFixed(0)}W</span>
                </div>
            </div>
        `;
    }).join('');
    
    const sys = data.metrics.system;
    document.getElementById('system-info').innerHTML = `
        <div class="metric-row"><span class="metric-label">Hostname</span><span class="metric-value">${sys.hostname || 'N/A'}</span></div>
        <div class="metric-row"><span class="metric-label">CPU</span><span class="metric-value">${(sys.cpu_percent || 0).toFixed(1)}%</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width: ${sys.cpu_percent || 0}%"></div></div>
        <div class="metric-row"><span class="metric-label">Memory</span><span class="metric-value">${(sys.memory_used_gb || 0).toFixed(1)}/${(sys.memory_total_gb || 0).toFixed(1)} GB</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width: ${sys.memory_percent || 0}%"></div></div>
        <div class="metric-row"><span class="metric-label">Disk</span><span class="metric-value">${(sys.disk_used_gb || 0).toFixed(1)}/${(sys.disk_total_gb || 0).toFixed(1)} GB</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width: ${sys.disk_percent || 0}%"></div></div>
    `;
    
    const alertsList = document.getElementById('alerts-list');
    if (data.alerts && data.alerts.length > 0) {
        alertsList.innerHTML = data.alerts.map(a => `<div class="alert-item"><strong>${a.severity.toUpperCase()}</strong>: ${a.message}</div>`).join('');
    } else {
        alertsList.innerHTML = '<div style="color: var(--accent-green);">No active alerts</div>';
    }
    
    document.getElementById('last-update').textContent = 'Last update: ' + new Date().toLocaleTimeString();
}

async function loadHistory() {
    const metric = document.getElementById('metric-select').value;
    const hours = document.getElementById('hours-select').value;

    try {
        // allow 'lifetime' to be requested; server may handle it
        const historyResponse = await fetch(`/api/history?metric=${metric}&hours=${hours}`);
        let historyData = await historyResponse.json();
        // If user requested 'lifetime' but server returned empty, try a large numeric fallback
        if (hours === 'lifetime' && (!historyData || !historyData.data || historyData.data.length === 0)) {
            try {
                const fallbackHours = 24 * 365 * 5; // 5 years
                const resp2 = await fetch(`/api/history?metric=${metric}&hours=${fallbackHours}`);
                if (resp2.ok) historyData = await resp2.json();
            } catch (e) { /* ignore fallback errors */ }
        }

        const ctx = document.getElementById('historyChart').getContext('2d');
        ensureZoomPlugin();
        if (historyChart) historyChart.destroy();

        const getUnit = (metric) => {
            if (metric.includes('utilization') || metric.includes('percent')) return '%';
            if (metric.includes('memory_used')) return 'MB';
            if (metric.includes('temperature')) return '°C';
            if (metric.includes('power')) return 'W';
            return '';
        }
        const unit = getUnit(metric);

        // Prepare labels (timestamps) and datapoints
        const points = (historyData.data || []).map(d => ({ t: new Date(d.timestamp).getTime(), y: d.value }));
        const labels = (historyData.data || []).map(d => new Date(d.timestamp).getTime());

        // Determine if multi-day range
        const firstTs = points.length ? points[0].t : Date.now();
        const lastTs = points.length ? points[points.length-1].t : Date.now();
        const rangeHours = (lastTs - firstTs) / (1000*60*60);
        const multiDay = rangeHours >= 24;

        // y axis options
        const yAxisOptions = {
            ticks: { color: '#a0a0a0' },
            grid: { color: '#4a4a4a' },
            beginAtZero: true,
            title: { display: true, text: unit, color: '#a0a0a0', font: { size: 14, weight: 'bold' } }
        };
        if (metric.includes('utilization') || metric.includes('percent')) yAxisOptions.suggestedMax = 100;
        if (metric.includes('temperature')) yAxisOptions.suggestedMax = 100;

        // Build plugin to draw alternating day bands for multi-day ranges
        // compute day boundaries once so click/highlight can map to days
        const dayStarts = [];
        let prevDay = null;
        for (let i = 0; i < labels.length; i++) {
            const d = new Date(labels[i]);
            const day = d.getFullYear() + '-' + d.getMonth() + '-' + d.getDate();
            if (day !== prevDay) { dayStarts.push(i); prevDay = day; }
        }

        const dayBandPlugin = {
            id: 'dayBands',
            beforeDatasetsDraw: function(chart) {
                if (!multiDay) return;
                try {
                    const xScale = chart.scales.x;
                    const ctx = chart.ctx;
                    const dataLen = historyOriginalLabels.length;
                    if (dataLen === 0) return;
                    for (let j = 0; j < dayStarts.length; j++) {
                        const startIdx = dayStarts[j];
                        const endIdx = (j+1 < dayStarts.length) ? dayStarts[j+1]-1 : dataLen-1;
                        const startTs = historyOriginalLabels[startIdx];
                        const endTs = historyOriginalLabels[endIdx];
                        const left = xScale.getPixelForValue(startTs);
                        const right = xScale.getPixelForValue(endTs + 1);
                        const bandColor = (j % 2 === 0) ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.03)';
                        ctx.save(); ctx.fillStyle = bandColor; ctx.fillRect(left, chart.chartArea.top, Math.max(1, right-left), chart.chartArea.bottom - chart.chartArea.top); ctx.restore();
                    }
                } catch(e) { console.debug('dayBandPlugin error', e); }
            }
        };

        // store originals for zooming / highlighting
        historyOriginalLabels = labels.slice();
        historyOriginalData = points.map(p => p.y).slice();
        historyDayStarts = dayStarts.slice();
        historyVisibleStart = 0;
        historyVisibleEnd = historyOriginalLabels.length - 1;

        // plugin: highlight selected day (uses historySelectedDay and historyDayStarts)
        const highlightPlugin = {
            id: 'highlightDay',
            beforeDatasetsDraw: function(chart) {
                if (historySelectedDay === null) return;
                try {
                    const xScale = chart.scales.x;
                    const ctx = chart.ctx;
                    const len = historyOriginalLabels.length;
                    const sel = historySelectedDay;
                    if (sel < 0 || sel >= historyDayStarts.length) return;
                    const globalStartIdx = historyDayStarts[sel];
                    const globalEndIdx = (sel+1 < historyDayStarts.length) ? historyDayStarts[sel+1]-1 : len-1;
                    const globalStartTs = historyOriginalLabels[globalStartIdx];
                    const globalEndTs = historyOriginalLabels[globalEndIdx];
                    const left = xScale.getPixelForValue(globalStartTs);
                    const right = xScale.getPixelForValue(globalEndTs + 1);
                    // check overlap with chart area
                    if (right < chart.chartArea.left || left > chart.chartArea.right) return;
                    ctx.save(); ctx.fillStyle = 'rgba(0,160,255,0.12)'; ctx.fillRect(left, chart.chartArea.top, Math.max(1, right-left), chart.chartArea.bottom - chart.chartArea.top); ctx.restore();
                } catch(e) { console.debug('highlightPlugin error', e); }
            }
        };

        historyChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: document.getElementById('metric-select').selectedOptions[0].text,
                    data: points.map(p => ({ x: p.t, y: p.y })),
                    borderColor: '#76b900',
                    backgroundColor: 'rgba(118, 185, 0, 0.08)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 2
                }]
            },
            options: {
                responsive: true,
                interaction: { mode: 'nearest', intersect: false },
                plugins: {
                    legend: { display: true, labels: { color: '#f0f0f0', font: { size: 14 } } },
                    zoom: { pan: { enabled: true, mode: 'x' }, zoom: { wheel: { enabled: true }, pinch: { enabled: true }, drag: { enabled: false }, mode: 'x' } }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: { tooltipFormat: 'MMM d, yyyy HH:mm' },
                        ticks: { color: '#a0a0a0', maxRotation: 0, autoSkip: true },
                        grid: { color: '#4a4a4a' }
                    },
                    y: yAxisOptions
                },
                plugins: [dayBandPlugin, highlightPlugin]
            }
        });
        // add click handler to highlight the day/hour of the nearest datapoint
        const canvas = document.getElementById('historyChart');
        canvas.onclick = function(evt) {
            try {
                const pointsFound = historyChart.getElementsAtEventForMode(evt, 'nearest', { intersect: false }, true);
                if (!pointsFound || pointsFound.length === 0) return;
                const idx = pointsFound[0].index; // index into dataset.data
                // find day index for idx
                let sel = 0;
                for (let j = 0; j < historyDayStarts.length; j++) {
                    if (historyDayStarts[j] <= idx) sel = j; else break;
                }
                historySelectedDay = sel;
                historyChart.update('none');
            } catch (e) { console.debug('click highlight failed', e); }
        };
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

async function loadProcesses() {
    try {
        const tbody = document.getElementById('process-list');
        // show loading state while we fetch latest processes
        tbody.innerHTML = '<tr><td colspan="5" style="color: var(--text-secondary);">Loading processes…</td></tr>';

        const response = await fetch('/api/processes');
        const data = await response.json();
        
        // Update VRAM bar if we have GPU memory stats
        if (data.gpu_memory && Object.keys(data.gpu_memory).length > 0) {
            const gpuKeys = Object.keys(data.gpu_memory);
            const gpu0 = data.gpu_memory[gpuKeys[0]];
            
            if (gpu0 && gpu0.total > 0) {
                const usedGB = (gpu0.used / 1024).toFixed(1);
                const totalGB = (gpu0.total / 1024).toFixed(1);
                const freeGB = (gpu0.free / 1024).toFixed(1);
                const usedPct = ((gpu0.total - gpu0.free) / gpu0.total) * 100;
                
                document.getElementById('vram-bar-container').style.display = 'block';
                document.getElementById('vram-used-bar').style.width = usedPct + '%';
                document.getElementById('vram-free').textContent = `${usedGB} / ${totalGB} GB (${freeGB} GB Free)`;
                
                // Change color based on usage - solid colors only
                const bar = document.getElementById('vram-used-bar');
                if (usedPct > 90) {
                    bar.style.background = 'var(--accent-red)';
                } else if (usedPct > 70) {
                    bar.style.background = 'var(--accent-yellow)';
                } else {
                    bar.style.background = 'var(--accent-green)';
                }
            }
        }
        
        if (!data.processes || data.processes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="color: var(--text-secondary);">No GPU processes running</td></tr>';
        } else {
            // Sort by GPU utilization (descending). Fall back to gpu_utilization_percent or 0.
            const sorted = (data.processes || []).slice().sort((a, b) => {
                const au = Number(a.gpu_utilization ?? a.gpu_utilization_percent ?? 0) || 0;
                const bu = Number(b.gpu_utilization ?? b.gpu_utilization_percent ?? 0) || 0;
                return bu - au;
            });

            tbody.innerHTML = sorted.map(p => {
                const userDisplay = p.username || p.user || 'N/A';
                const pid = p.pid;
                // Disable terminate button and add tooltip when the server is not running elevated
                const disabledAttr = (window.isAdmin ? '' : 'disabled');
                const tooltipAttr = (window.isAdmin ? '' : ' data-tooltip="Run as admin"');
                const baseStyle = 'padding:6px 10px;border-radius:6px;border:none;background:var(--accent-red);color:#fff;';
                const disabledStyle = window.isAdmin ? '' : 'opacity:0.55;cursor:not-allowed;';
                const combinedStyle = `style="${baseStyle}${disabledStyle}"`;
                return `
                    <tr>
                        <td>${pid}</td>
                        <td>${p.name || 'N/A'}</td>
                        <td>GPU ${p.gpu_index}</td>
                        <td>${userDisplay}</td>
                        <td><button id="terminate-${pid}" onclick="terminateProcess(${pid})" ${disabledAttr}${tooltipAttr} ${combinedStyle}>Terminate</button></td>
                    </tr>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading processes:', error);
        document.getElementById('process-list').innerHTML = 
            '<tr><td colspan="5" style="color: var(--accent-red);">Error loading processes</td></tr>';
    }
}

function exportData(format) {
    const hours = document.getElementById('export-hours').value;
    window.location.href = `/api/export/${format}?hours=${hours}`;
}

// Terminate a process by PID via server endpoint
async function terminateProcess(pid) {
    try {
        // Safety: prevent UI-initiated terminate when not running elevated
        if (typeof window !== 'undefined' && window.isAdmin === false) {
            if (typeof showToast === 'function') showToast('Run as admin', { level: 'yellow', duration: 4000 });
            return;
        }
        // Directly send terminate request (no confirm). Disable button while in-flight.
        const btn = document.getElementById(`terminate-${pid}`);
        if (btn) { btn.disabled = true; btn.textContent = 'Terminating...'; }

        const resp = await fetch('/api/processes/terminate', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pid })
        });
        const data = await resp.json().catch(() => ({}));
        if (resp.ok && (data.status === 'terminated' || data.status === 'killed')) {
            if (typeof showSuccess === 'function') showSuccess('Process terminated');
            if (btn) { btn.textContent = 'Terminated'; }
            try { const row = document.getElementById(`terminate-${pid}`).closest('tr'); if (row) { row.style.opacity = '0.6'; } } catch(e){}
        } else if (data.status === 'not_found') {
            if (typeof showError === 'function') showError('Process not found');
            if (btn) { btn.disabled = false; btn.textContent = 'Terminate'; }
        } else {
            const msg = data.error || data.status || 'Error';
            if (typeof showError === 'function') showError('Terminate failed: ' + msg);
            if (btn) { btn.disabled = false; btn.textContent = 'Terminate'; }
        }
    } catch (e) {
        if (typeof showError === 'function') showError('Terminate error: ' + (e && e.message ? e.message : e));
        const btn = document.getElementById(`terminate-${pid}`);
        if (btn) { btn.disabled = false; btn.textContent = 'Terminate'; }
    }
}

// Benchmark functions
let benchmarkPollInterval = null;
let benchCharts = {};
let selectedMode = 'quick';
let selectedBenchType = 'gemm';

// Load baseline on page load
async function loadBaseline() {
    try {
        const response = await fetch('/api/benchmark/baseline?benchmark_type=' + selectedBenchType);
        const baseline = await response.json();
        if (baseline && baseline.status !== 'no_baseline') {
            document.getElementById('baseline-info').style.display = 'block';
            const benchTypeLabel = baseline.benchmark_type === 'gemm' ? 'GEMM' : 'Particle';
            document.getElementById('baseline-details').innerHTML = `
                <div class="metric-row"><span class="metric-label">GPU</span><span class="metric-value">${baseline.gpu_name}</span></div>
                <div class="metric-row"><span class="metric-label">Type</span><span class="metric-value">${benchTypeLabel}</span></div>
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
    
    // Update simulation button enabled state depending on mode
    const startSimBtn = document.getElementById('start-sim-btn');
    if (startSimBtn) {
        if (selectedMode === 'stress-test' || selectedMode === 'custom') {
            startSimBtn.disabled = true;
            startSimBtn.title = 'Simulation disabled for stress-test and custom modes';
            startSimBtn.style.opacity = '0.5';
            startSimBtn.style.cursor = 'not-allowed';
        } else {
            startSimBtn.disabled = false;
            startSimBtn.title = '';
            startSimBtn.style.opacity = '';
            startSimBtn.style.cursor = '';
        }
    }
}

function selectMode(mode) {
    selectedMode = mode;
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    document.getElementById('custom-controls').style.display = mode === 'custom' ? 'block' : 'none';
    
    // Update mode description
    const descriptions = {
        'quick': 'Quick baseline test - 15 seconds with fixed workload size',
        'standard': 'Standard benchmark - 60 seconds with fixed workload size',
        'extended': 'Extended burn-in test - 180 seconds with fixed workload size for thorough validation',
        'stress-test': 'Stress test - 60 seconds with AUTO-SCALING workload that dynamically increases to push GPU to 98% utilization',
        'custom': 'Custom configuration - set your own duration, limits, and workload parameters'
    };
    document.getElementById('mode-description').textContent = descriptions[mode] || '';

    // When in stress-test or custom modes the Simulation view is not supported
    const simBtn = document.getElementById('start-sim-btn');
    if (simBtn) {
        if (mode === 'stress-test' || mode === 'custom') {
            simBtn.disabled = true;
            simBtn.title = 'Simulation disabled for stress-test and custom modes';
            simBtn.style.opacity = '0.5';
            simBtn.style.cursor = 'not-allowed';
        } else {
            simBtn.disabled = false;
            simBtn.title = '';
            simBtn.style.opacity = '';
            simBtn.style.cursor = '';
        }
    }
}

function updateSliderValue(type) {
    const slider = document.getElementById('custom-' + type);
    const input = document.getElementById('custom-' + type + '-val');
    input.value = slider.value;
}

// Sync input to slider
['duration', 'temp', 'memory', 'power', 'matrix', 'particles'].forEach(type => {
    const input = document.getElementById('custom-' + type + '-val');
    if (input) {
        input.addEventListener('change', () => {
            document.getElementById('custom-' + type).value = input.value;
        });
    }
});

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

async function startSimulation() {
    console.log('Start Simulation clicked');
    console.log('Current benchmark type:', selectedBenchType);
    console.log('Current mode:', selectedMode);
    
    // Check current benchmark type
    const currentType = selectedBenchType;
    let modeToUse;
    
    // If not on particle type, switch to it and use 'quick' mode
    if (currentType !== 'particle') {
        selectBenchType('particle');
        modeToUse = 'quick';
        selectMode('quick');
    } else {
        // Use the currently selected mode
        modeToUse = selectedMode;
    }
    
    const btn = document.getElementById('start-sim-btn');
    const stopBtn = document.getElementById('stop-bench-btn');
    btn.disabled = true;
    btn.textContent = 'Opening Simulation...';
    stopBtn.style.display = 'inline-block';
    
    document.getElementById('benchmark-progress').style.display = 'block';
    document.getElementById('benchmark-live-charts').style.display = 'block';
    document.getElementById('benchmark-results').innerHTML = '';
    document.getElementById('bench-stop-reason').textContent = '';
    document.getElementById('iteration-counter').style.display = 'inline';
    document.getElementById('iteration-counter').textContent = 'Iteration #0';
    
    // Get duration and particles based on selected mode
    let duration = 60;
    let particles = 100000;
    
    if (modeToUse === 'quick') {
        duration = 15;
        particles = 50000;
    } else if (modeToUse === 'standard') {
        duration = 60;
        particles = 100000;
    } else if (modeToUse === 'extended') {
        duration = 180;
        particles = 100000;
    } else if (modeToUse === 'stress-test') {
        duration = 60;
        particles = 200000;
    } else if (modeToUse === 'custom') {
        duration = parseInt(document.getElementById('custom-duration-val').value);
        particles = Math.round(parseFloat(document.getElementById('custom-particles-val').value) * 1000000);
    }
    
    // Build URL with params
    let url = `/api/benchmark/start?benchmark_type=particle&visualize=true&duration=${duration}&num_particles=${particles}`;
    
    // Initialize live charts
    initLiveCharts();
    
    try {
        await fetch(url, { method: 'POST' });
        btn.textContent = 'Simulation Running';
        benchmarkPollInterval = setInterval(pollBenchmarkStatus, 500);
    } catch (error) {
        console.error('Error starting simulation:', error);
        btn.disabled = false;
        btn.textContent = 'Start Simulation';
        stopBtn.style.display = 'none';
    }
}

function createSmallChart(canvasId, color, maxY = null) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ data: [], borderColor: color, backgroundColor: color + '20', fill: true, tension: 0.3, pointRadius: 0 }] },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false },
                y: { min: 0, max: maxY, ticks: { color: '#a0a0a0' }, grid: { color: '#4a4a4a' } }
            }
        }
    });
}

function initLiveCharts() {
    Object.values(benchCharts).forEach(c => c.destroy());
    benchCharts = {
        utilization: createSmallChart('chartUtilization', '#76b900', 100),
        temperature: createSmallChart('chartTemperature', '#ffc107', 100),
        memory: createSmallChart('chartMemory', '#00a0ff'),
        power: createSmallChart('chartPower', '#dc3545')
    };
}

async function pollBenchmarkStatus() {
    try {
        const [statusRes, samplesRes] = await Promise.all([
            fetch('/api/benchmark/status'),
            fetch('/api/benchmark/samples')
        ]);
        const status = await statusRes.json();
        const samplesData = await samplesRes.json();

        document.getElementById('bench-progress-bar').style.width = (status.progress || 0) + '%';
        document.getElementById('bench-percent').textContent = (status.progress || 0) + '%';
        document.getElementById('iteration-counter').textContent = 'Iteration #' + (status.iterations || 0);
        document.getElementById('workload-info').textContent = 'Workload: ' + (status.workload_type || 'N/A');
        document.getElementById('bench-workload').textContent = status.workload_type || '';

        // Update live charts with samples
        if (samplesData && samplesData.samples && benchCharts.utilization) {
            const samples = samplesData.samples;
            const labels = samples.map(s => s.elapsed_sec + 's');

            benchCharts.utilization.data.labels = labels;
            benchCharts.utilization.data.datasets[0].data = samples.map(s => s.utilization || 0);
            benchCharts.utilization.update('none');

            benchCharts.temperature.data.labels = labels;
            benchCharts.temperature.data.datasets[0].data = samples.map(s => s.temperature_c || 0);
            benchCharts.temperature.update('none');

            benchCharts.memory.data.labels = labels;
            benchCharts.memory.data.datasets[0].data = samples.map(s => s.memory_used_mb || 0);
            benchCharts.memory.update('none');

            benchCharts.power.data.labels = labels;
            benchCharts.power.data.datasets[0].data = samples.map(s => s.power_w || 0);
            benchCharts.power.update('none');
        }

        if (!status.running) {
            clearInterval(benchmarkPollInterval);
            document.getElementById('start-bench-btn').disabled = false;
            document.getElementById('start-bench-btn').textContent = 'Start Benchmark';
            document.getElementById('stop-bench-btn').style.display = 'none';

            // fetch results and render
            try {
                const res = await fetch('/api/benchmark/results');
                if (res.ok) {
                    const results = await res.json();
                    if (typeof window !== 'undefined' && typeof window.renderFancyBenchmarkResults === 'function') {
                        try { window.renderFancyBenchmarkResults(results); return; } catch (e) { console.debug('renderFancyBenchmarkResults failed', e); }
                    }

                    // fallback rendering
                    const r = results || {};
                    const html = `
                        <div class="gpu-card"><h3 style="color: var(--accent-green);">Benchmark Results</h3>
                            <div class="metric-row"><span class="metric-label">Average TFLOPS</span><span class="metric-value">${(r.backend === 'cupy' || r.backend === 'torch') && Number.isFinite(r.avg_tflops) ? r.avg_tflops.toFixed(2) : 'N/A'}</span></div>
                            <div class="metric-row"><span class="metric-label">Peak TFLOPS</span><span class="metric-value">${(r.backend === 'cupy' || r.backend === 'torch') && Number.isFinite(r.peak_tflops) ? r.peak_tflops.toFixed(2) : 'N/A'}</span></div>
                            <div class="metric-row"><span class="metric-label">Avg Temperature</span><span class="metric-value">${(r.avg_temperature || 0).toFixed(1)}°C</span></div>
                            <div class="metric-row"><span class="metric-label">Avg GPU Utilization</span><span class="metric-value">${(r.avg_gpu_utilization || 0).toFixed(1)}%</span></div>
                            <div class="metric-row"><span class="metric-label">Avg Memory Usage</span><span class="metric-value">${(r.avg_memory_usage || 0).toFixed(1)}%</span></div>
                            <div class="metric-row"><span class="metric-label">Avg Power Draw</span><span class="metric-value">${(r.avg_power_draw || 0).toFixed(1)}W</span></div>
                            <div class="metric-row"><span class="metric-label">Duration</span><span class="metric-value">${(r.duration || 0).toFixed(1)}s</span></div>
                            <div class="metric-row"><span class="metric-label">Iterations</span><span class="metric-value">${r.total_iterations || r.iterations_completed || 0}</span></div>
                        </div>
                    `;
                    document.getElementById('benchmark-results').innerHTML = html;
                } else {
                    document.getElementById('benchmark-results').innerHTML = '<p style="color: var(--text-secondary);">Failed to load results</p>';
                }
            } catch (e) {
                console.error('Error fetching benchmark results:', e);
            }
        }
    } catch (error) {
        console.error('Error polling benchmark status:', error);
        try { clearInterval(benchmarkPollInterval); } catch(e){}
    }
}

async function checkForUpdates() {
    const btn = document.getElementById('update-btn');
    btn.disabled = true;
    btn.textContent = 'Checking...';
    btn.removeAttribute('data-tooltip');
    const GITHUB_REPO = 'DataBoySu/cluster-monitor';

    function parseVersion(text) {
        if (!text) return '0.0.0';
        const m = /v?(\d+\.\d+\.\d+)/.exec(text);
        return m ? m[1] : text.trim();
    }

    function compareVer(a, b) {
        const pa = a.split('.').map(n => parseInt(n)||0);
        const pb = b.split('.').map(n => parseInt(n)||0);
        for (let i=0;i<3;i++){
            if ((pa[i]||0) > (pb[i]||0)) return 1;
            if ((pa[i]||0) < (pb[i]||0)) return -1;
        }
        return 0;
    }

    try {
        // Read current version from footer (rendered server-side as {{VERSION}})
        let currentText = '';
        try { currentText = document.querySelector('footer').textContent || ''; } catch(e){}
        const currentVersion = parseVersion(currentText);

        const apiUrl = `https://api.github.com/repos/${GITHUB_REPO}/releases/latest`;
        const resp = await fetch(apiUrl, { headers: { Accept: 'application/vnd.github.v3+json' } });
        if (!resp.ok) throw new Error('GitHub API error: ' + resp.status);
        const json = await resp.json();
        const latestTag = parseVersion(json.tag_name || json.name || '0.0.0');

        const cmp = compareVer(latestTag, currentVersion);
        if (cmp > 0) {
            btn.textContent = `Update: ${latestTag}`;
            btn.classList.remove('success', 'error');
            btn.disabled = false;
            btn.setAttribute('data-tooltip', `Current: ${currentVersion} → Latest: ${latestTag}`);

            btn.onclick = async () => {
                btn.textContent = 'Installing...';
                btn.disabled = true;
                try {
                    const install = await fetch('/api/update/install', { method: 'POST' });
                    const result = await install.json();
                    if (result.status === 'success') {
                        btn.textContent = 'Restart App';
                        btn.classList.add('success');
                        btn.setAttribute('data-tooltip', 'Update installed - restart application');
                    } else {
                        btn.textContent = 'Update Failed';
                        btn.classList.add('error');
                        btn.setAttribute('data-tooltip', result.message || 'Failed to install');
                        btn.disabled = false;
                    }
                } catch (e) {
                    btn.textContent = 'Install Error';
                    btn.classList.add('error');
                    btn.setAttribute('data-tooltip', e && e.message ? e.message : 'Install failed');
                    btn.disabled = false;
                }
            };
        } else {
            btn.textContent = 'Latest Version';
            btn.classList.add('success');
            btn.setAttribute('data-tooltip', `Version ${currentVersion}`);
            setTimeout(() => {
                btn.textContent = 'Check for Updates';
                btn.classList.remove('success');
                btn.disabled = false;
                btn.removeAttribute('data-tooltip');
            }, 3000);
        }
    } catch (error) {
        btn.textContent = 'Network Error';
        btn.classList.add('error');
        btn.setAttribute('data-tooltip', 'Could not check GitHub releases');
        btn.disabled = false;
    }
}

function tick() {
    countdown--;
    document.getElementById('countdown').textContent = countdown;
    if (countdown <= 0) {
        countdown = 5;
        fetchStatus();
        
        // Auto-refresh active tab content
        const activeTab = document.querySelector('.tab-content.active');
        if (activeTab) {
            const tabId = activeTab.id;
            if (tabId === 'processes-tab') {
                loadProcesses();
            } else if (tabId === 'history-tab') {
                const activeChart = document.querySelector('.chart-tab.active');
                if (activeChart) {
                    loadHistory();
                }
            }
        }
    }
}

async function loadFeatures() {
    try {
        const response = await fetch('/api/features');
        const features = await response.json();
        // Detect whether the server process is elevated so the UI can enable/disable admin actions
        try {
            const elevResp = await fetch('/api/is_elevated');
            const elevJson = await elevResp.json().catch(() => ({}));
            window.isAdmin = Boolean(elevJson && (elevJson.elevated || elevJson.started_with_flag));
        } catch (e) {
            window.isAdmin = false;
        }
        
        const benchTab = document.querySelector('[data-tab="benchmark"]');
        const startBtn = document.getElementById('start-bench-btn');
        const startSimBtn = document.getElementById('start-sim-btn');
        const typeButtons = document.querySelectorAll('.type-btn');
        const modeButtons = document.querySelectorAll('.mode-btn');
        
        // Disable benchmark controls if GPU benchmark not available
        if (!features.gpu_benchmark) {
            if (benchTab) {
                benchTab.classList.add('disabled');
                benchTab.setAttribute('data-tooltip', 'Install CuPy or PyTorch for GPU benchmarking');
                benchTab.style.pointerEvents = 'auto';
            }
            
            if (startBtn) {
                startBtn.disabled = true;
                startBtn.style.opacity = '0.5';
                startBtn.style.cursor = 'not-allowed';
                startBtn.title = 'GPU benchmark libraries not installed';
            }
            
            if (startSimBtn) {
                startSimBtn.disabled = true;
                startSimBtn.style.opacity = '0.5';
                startSimBtn.style.cursor = 'not-allowed';
                startSimBtn.title = 'Install CuPy or PyTorch for simulation';
            }
            
            typeButtons.forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = '0.5';
                btn.style.cursor = 'not-allowed';
            });
            
            modeButtons.forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = '0.5';
                btn.style.cursor = 'not-allowed';
            });
        } else {
            // ENABLE controls when GPU benchmark IS available
            if (benchTab) {
                benchTab.classList.remove('disabled');
                benchTab.removeAttribute('data-tooltip');
                benchTab.style.pointerEvents = '';
            }
            
            if (startBtn) {
                startBtn.disabled = false;
                startBtn.style.opacity = '1';
                startBtn.style.cursor = 'pointer';
                startBtn.title = 'Start GPU benchmark';
            }
            
            if (startSimBtn) {
                startSimBtn.disabled = false;
                startSimBtn.style.opacity = '1';
                startSimBtn.style.cursor = 'pointer';
                startSimBtn.title = 'Start particle simulation with visualization';
            }
            
            typeButtons.forEach(btn => {
                btn.disabled = false;
                btn.style.opacity = '1';
                btn.style.cursor = 'pointer';
            });
            
            modeButtons.forEach(btn => {
                btn.disabled = false;
                btn.style.opacity = '1';
                btn.style.cursor = 'pointer';
            });
        }
    } catch (error) {
        console.error('Error loading features:', error);
    }
}

fetchStatus();
loadBaseline();
loadFeatures();
refreshInterval = setInterval(tick, 1000);

// Initialize benchmark type on load
selectBenchType('gemm');

// Inject Restart as Admin button next to the Update button (no confirmation required)
try {
    const updateBtn = document.getElementById('update-btn');
    if (updateBtn && !document.getElementById('restart-elevated-btn')) {
        const btn = document.createElement('button');
        btn.id = 'restart-elevated-btn';
        btn.textContent = 'ADMIN';
        btn.style.padding = '8px 12px';
        btn.style.borderRadius = '6px';
        btn.style.border = '2px solid #76b900';
        btn.style.background = '#0b0b0b';
        btn.style.color = '#76b900';
        btn.style.cursor = 'pointer';
        btn.style.marginRight = '8px';
        btn.title = 'Restart the server with elevated privileges (UAC prompt)';

        btn.onclick = async function() {
            try {
                // Detection-only: query server for elevation status and show minimal toast
                const resp = await fetch('/api/is_elevated');
                if (!resp.ok) { window.showToast('', { level: 'red' }); return; }
                const json = await resp.json().catch(() => ({}));
                const elevated = Boolean(json && (json.elevated || json.started_with_flag));
                if (elevated) {
                    window.showSuccess('Running with admin');
                } else {
                    // Give the user concise instruction to start server with admin
                    const cmd = "python health_monitor.py web --admin";
                    window.showToast(`Run with admin: ${cmd}`, { level: 'yellow', duration: 12000 });
                }
            } catch (e) {
                window.showToast('', { level: 'red' });
            }
        };

        // insert to the left of updateBtn
        updateBtn.parentNode.insertBefore(btn, updateBtn);
    }
} catch (e) { console.debug('inject restart button error', e); }
