// main.js - Main initialization and tab handling
// All functions are now modularized across simulation.js, benchmark.js, charts.js, and utils.js

// Global variables
let countdown = 5;
let historyChart = null;
let benchmarkPollInterval = null;
let benchCharts = {};
let selectedMode = 'quick';
let selectedBenchType = 'gemm';
if (typeof selectedBackend === 'undefined') {
    var selectedBackend = 'auto';
}

// History chart state for zoom/highlight (mirrors main.js)
let historyOriginalLabels = [];
let historyOriginalData = [];
let historyVisibleStart = 0;
let historyVisibleEnd = 0;
let historyDayStarts = [];
let historySelectedDay = null;

function ensureZoomPlugin() {
    try {
        if (typeof Chart === 'undefined') return;
        const regs = (Chart && Chart.registry && Chart.registry.plugins && Chart.registry.plugins.items) ? Chart.registry.plugins.items : null;
        if (regs && regs.some(p => p && p.id === 'zoom')) return;
        const candidate = window['chartjsPluginZoom'] || window['ChartZoom'] || window['chartjs-plugin-zoom'];
        if (candidate) {
            Chart.register(candidate);
            console.debug('chartjs zoom plugin registered at runtime (main-new)');
        }
    } catch (e) { console.debug('ensureZoomPlugin error (main-new)', e); }
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
function highlightSelectedDay(val) { const idx = val === '' ? null : parseInt(val); historySelectedDay = isNaN(idx) ? null : idx; renderHistoryView(); }
function renderHistoryView(){ if (!historyChart) return; historyChart.update('none'); }

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
        
        // Clear benchmark results when leaving the benchmark tab to avoid stale/plain-text output
        if (tab.dataset.tab !== 'benchmark') {
            try { const br = document.getElementById('benchmark-results'); if (br) br.innerHTML = ''; } catch(e){}
        }
        if (tab.dataset.tab === 'history') loadHistory();
        if (tab.dataset.tab === 'processes') loadProcesses();
        if (tab.dataset.tab === 'benchmark') { loadBenchmarkResults(); loadBaseline(); }
    });
});

// History loader (mirrors improved behavior in main.js)
async function loadHistory() {
    const metric = document.getElementById('metric-select').value;
    const hours = document.getElementById('hours-select').value;
    try {
        const historyResponse = await fetch(`/api/history?metric=${metric}&hours=${hours}`);
        let historyData = await historyResponse.json();
        if (hours === 'lifetime' && (!historyData || !historyData.data || historyData.data.length === 0)) {
            try {
                const fallbackHours = 24 * 365 * 5;
                const r2 = await fetch(`/api/history?metric=${metric}&hours=${fallbackHours}`);
                if (r2.ok) historyData = await r2.json();
            } catch(e){}
        }
        const ctx = document.getElementById('historyChart').getContext('2d');
        if (historyChart) historyChart.destroy();
        ensureZoomPlugin();

        const unit = (metric.includes('utilization') || metric.includes('percent')) ? '%' : (metric.includes('memory_used') ? 'MB' : (metric.includes('temperature') ? '°C' : (metric.includes('power') ? 'W' : '')));

        const points = (historyData.data || []).map(d => ({ t: new Date(d.timestamp).getTime(), y: d.value }));
        const labels = (historyData.data || []).map(d => new Date(d.timestamp).getTime());
        const firstTs = points.length ? points[0].t : Date.now();
        const lastTs = points.length ? points[points.length-1].t : Date.now();
        const rangeHours = (lastTs - firstTs) / (1000*60*60);
        const multiDay = rangeHours >= 24;

        const yAxisOptions = { ticks: { color: '#a0a0a0' }, grid: { color: '#4a4a4a' }, beginAtZero: true, title: { display: true, text: unit, color: '#a0a0a0' } };

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
                    const xScale = chart.scales.x; const ctx = chart.ctx; const dataLen = historyOriginalLabels.length; if (dataLen === 0) return;
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
                    // store originals for zoom/highlight
                    historyOriginalLabels = labels.slice();
                    historyOriginalData = points.map(p => p.y).slice();
                    historyDayStarts = dayStarts.slice();
                    historyVisibleStart = 0; historyVisibleEnd = historyOriginalLabels.length-1;

                    const highlightPlugin = {
                        id: 'highlightDay',
                        beforeDatasetsDraw: function(chart) {
                            if (historySelectedDay === null) return;
                            try {
                                const xScale = chart.scales.x; const ctx = chart.ctx; const len = historyOriginalLabels.length; const sel = historySelectedDay; if (sel < 0 || sel >= historyDayStarts.length) return;
                                const globalStartIdx = historyDayStarts[sel];
                                const globalEndIdx = (sel+1 < historyDayStarts.length) ? historyDayStarts[sel+1]-1 : len-1;
                                const globalStartTs = historyOriginalLabels[globalStartIdx];
                                const globalEndTs = historyOriginalLabels[globalEndIdx];
                                const left = xScale.getPixelForValue(globalStartTs);
                                const right = xScale.getPixelForValue(globalEndTs + 1);
                                if (right < chart.chartArea.left || left > chart.chartArea.right) return;
                                ctx.save(); ctx.fillStyle = 'rgba(0,160,255,0.12)'; ctx.fillRect(left, chart.chartArea.top, Math.max(1, right-left), chart.chartArea.bottom - chart.chartArea.top); ctx.restore();
                            } catch(e) { console.debug('highlightPlugin error', e); }
                        }
                    };

                    historyChart = new Chart(ctx, {
            type: 'line',
            data: { datasets: [{ label: document.getElementById('metric-select').selectedOptions[0].text, data: points.map(p => ({ x: p.t, y: p.y })), borderColor: '#76b900', backgroundColor: 'rgba(118, 185, 0, 0.08)', fill: true, tension: 0.3, pointRadius: 2 }] },
                        options: { responsive: true, interaction: { mode: 'nearest', intersect: false }, plugins: { legend: { display: true, labels: { color: '#f0f0f0' } }, zoom: { pan: { enabled: true, mode: 'x' }, zoom: { wheel: { enabled: true }, pinch: { enabled: true }, drag: { enabled: false }, mode: 'x' } } }, scales: { x: { type: 'time', time: { tooltipFormat: 'MMM d, yyyy HH:mm' }, ticks: { color: '#a0a0a0' }, grid: { color: '#4a4a4a' } }, y: yAxisOptions }, plugins: [dayBandPlugin, highlightPlugin] }
        });
                    // add click handler to highlight the day/hour of the nearest datapoint
                    const canvas = document.getElementById('historyChart');
                    canvas.onclick = function(evt) {
                        try {
                            const pointsFound = historyChart.getElementsAtEventForMode(evt, 'nearest', { intersect: false }, true);
                            if (!pointsFound || pointsFound.length === 0) return;
                            const idx = pointsFound[0].index; // index into dataset.data
                            let sel = 0;
                            for (let j = 0; j < historyDayStarts.length; j++) {
                                if (historyDayStarts[j] <= idx) sel = j; else break;
                            }
                            historySelectedDay = sel;
                            historyChart.update('none');
                        } catch (e) { console.debug('click highlight failed', e); }
                    };
    } catch (e) { console.error('Error loading history:', e); }
}

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
            // try to extract server-provided error message
            let errText = `HTTP ${response.status}`;
            try {
                const txt = await response.text();
                if (txt) {
                    try { const j = JSON.parse(txt); errText = j.error || j.message || txt; }
                    catch(e){ errText = txt; }
