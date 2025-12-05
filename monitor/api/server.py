"""FastAPI server for REST API and web dashboard."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import json
import csv
import io
import asyncio
import threading

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse

from monitor.collectors.gpu import GPUCollector
from monitor.collectors.system import SystemCollector
from monitor.storage.sqlite import MetricsStorage
from monitor.alerting.rules import AlertEngine
from monitor.benchmark.gpu_bench import GPUBenchmark, BenchmarkConfig, get_benchmark_instance


def create_app(config: Dict[str, Any]) -> FastAPI:
    
    app = FastAPI(
        title="Cluster Health Monitor",
        description="Real-time GPU cluster monitoring",
        version="1.0.0"
    )
    
    storage = MetricsStorage(config['storage']['path'])
    alert_engine = AlertEngine(config.get('alerts', {}))
    
    @app.on_event("startup")
    async def startup():
        await storage.initialize()
    
    @app.on_event("shutdown")
    async def shutdown():
        storage.close()
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        return get_dashboard_html()
    
    @app.get("/api/status")
    async def get_status():
        gpu_collector = GPUCollector()
        sys_collector = SystemCollector()
        
        gpus = gpu_collector.collect()
        system = sys_collector.collect()
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'hostname': system.get('hostname', 'unknown'),
            'gpus': gpus,
            'system': system,
        }
        
        # Store metrics for history
        await storage.store(metrics)
        
        alerts = alert_engine.check(metrics)
        
        return {
            'status': 'healthy' if not alerts else 'warning',
            'metrics': metrics,
            'alerts': alerts,
        }
    
    @app.get("/api/gpus")
    async def get_gpus():
        collector = GPUCollector()
        return {'gpus': collector.collect()}
    
    @app.get("/api/processes")
    async def get_processes():
        collector = GPUCollector()
        return {'processes': collector.collect_processes()}
    
    @app.get("/api/system")
    async def get_system():
        collector = SystemCollector()
        return {'system': collector.collect()}
    
    @app.get("/api/alerts")
    async def get_alerts():
        return {'alerts': alert_engine.get_active_alerts()}
    
    @app.get("/api/history")
    async def get_history(hours: int = 1, metric: str = "gpu_0_utilization"):
        metrics = await storage.query(metric_name=metric, hours=hours)
        return {
            'metric': metric,
            'hours': hours,
            'data': [{'timestamp': m['timestamp'], 'value': m['metric_value']} for m in metrics]
        }
    
    @app.get("/api/history/available")
    async def get_available_metrics():
        return {
            'metrics': [
                'gpu_0_utilization', 'gpu_0_memory_used', 'gpu_0_temperature', 'gpu_0_power',
                'cpu_percent', 'memory_percent', 'disk_percent'
            ]
        }
    
    @app.get("/api/export/json")
    async def export_json(hours: int = 24):
        metrics = await storage.query(hours=hours)
        return StreamingResponse(
            io.BytesIO(json.dumps(metrics, indent=2).encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
        )
    
    @app.get("/api/export/csv")
    async def export_csv(hours: int = 24):
        metrics = await storage.query(hours=hours)
        
        output = io.StringIO()
        if metrics:
            writer = csv.DictWriter(output, fieldnames=metrics[0].keys())
            writer.writeheader()
            writer.writerows(metrics)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
    
    # Benchmark endpoints
    benchmark_instance = get_benchmark_instance()
    benchmark_thread = None
    
    @app.post("/api/benchmark/start")
    async def start_benchmark(
        mode: str = "standard",
        duration: int = 30,
        temp_limit: int = 85,
        memory_limit: int = 0,
        power_limit: int = 0
    ):
        nonlocal benchmark_thread
        
        if benchmark_instance.running:
            return {'status': 'already_running', 'progress': benchmark_instance.progress}
        
        # Create config based on mode
        if mode == 'custom':
            bench_config = BenchmarkConfig.custom(duration, temp_limit, memory_limit, power_limit)
        else:
            bench_config = BenchmarkConfig.from_mode(mode)
        
        def run_benchmark():
            benchmark_instance.start(bench_config)
        
        benchmark_thread = threading.Thread(target=run_benchmark)
        benchmark_thread.start()
        
        return {'status': 'started', 'message': 'Benchmark started', 'config': bench_config.__dict__}
    
    @app.get("/api/benchmark/status")
    async def get_benchmark_status():
        return benchmark_instance.get_status()
    
    @app.get("/api/benchmark/samples")
    async def get_benchmark_samples():
        return {'samples': benchmark_instance.get_samples()}
    
    @app.post("/api/benchmark/stop")
    async def stop_benchmark():
        benchmark_instance.stop()
        return {'status': 'stopping'}
    
    @app.get("/api/benchmark/results")
    async def get_benchmark_results():
        return benchmark_instance.get_results() if benchmark_instance.results else {'status': 'no_results'}
    
    @app.get("/api/benchmark/baseline")
    async def get_benchmark_baseline():
        baseline = benchmark_instance.get_baseline()
        return baseline if baseline else {'status': 'no_baseline'}
    
    return app


def get_dashboard_html() -> str:
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cluster Health Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
        
        :root {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2a2a2a;
            --bg-tertiary: #3a3a3a;
            --text-primary: #f0f0f0;
            --text-secondary: #a0a0a0;
            --accent-green: #76b900;
            --accent-blue: #00a0ff;
            --accent-yellow: #ffc107;
            --accent-red: #dc3545;
            --border-color: #4a4a4a;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Roboto', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        header {
            background: var(--accent-green);
            padding: 20px 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        header h1 { 
            font-size: 1.5em; 
            color: #000;
        }
        
        .status-badge {
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.85em;
            color: #000;
        }
        
        .status-healthy { background: var(--accent-blue); }
        .status-warning { background: var(--accent-yellow); }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 20px;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
        }
        
        .tab {
            padding: 10px 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            color: var(--text-secondary);
            transition: all 0.2s;
        }
        
        .tab:hover { background: var(--bg-tertiary); }
        .tab.active {
            background: var(--accent-green);
            color: #000;
            border-color: var(--accent-green);
        }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* Cards */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
        }
        
        .card h2 {
            color: var(--accent-green);
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        
        .gpu-card {
            background: var(--bg-tertiary);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
        }
        
        .gpu-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .gpu-name { font-weight: bold; }
        .gpu-temp { color: var(--accent-yellow); }
        .gpu-temp.hot { color: var(--accent-red); }
        
        .progress-bar {
            background: var(--bg-secondary);
            border-radius: 4px;
            height: 8px;
            margin: 8px 0;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: var(--accent-green);
            transition: width 0.3s ease;
        }
        
        .progress-fill.warn { background: var(--accent-yellow); }
        .progress-fill.crit { background: var(--accent-red); }
        
        .metric-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid var(--border-color);
        }
        
        .metric-label { color: var(--text-secondary); font-size: 0.9em; }
        .metric-value { font-weight: bold; }
        
        /* Process table */
        .process-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }
        
        .process-table th, .process-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        
        .process-table th {
            background: var(--bg-tertiary);
            color: var(--accent-green);
        }
        
        .process-table tr:hover { background: var(--bg-tertiary); }
        
        /* Chart */
        .chart-container {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .chart-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .chart-controls select, .chart-controls button {
            padding: 8px 15px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-primary);
            cursor: pointer;
        }
        
        .chart-controls button:hover { 
            background: var(--accent-green); 
            color: #000;
        }
        
        /* Export */
        .export-section {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .export-btn {
            padding: 12px 25px;
            background: var(--accent-green);
            border: none;
            border-radius: 8px;
            color: #000;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
        }
        
        .export-btn:hover { opacity: 0.9; }
        .export-btn.secondary { 
            background: var(--bg-tertiary); 
            border: 1px solid var(--border-color); 
            color: var(--text-primary);
        }
        
        footer {
            text-align: center;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }
        
        .alert-item {
            background: var(--bg-tertiary);
            border-left: 4px solid var(--accent-yellow);
            padding: 10px 15px;
            margin-bottom: 10px;
            border-radius: 0 8px 8px 0;
        }
        
        .mode-btn {
            padding: 10px 20px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-primary);
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .mode-btn:hover { background: var(--bg-secondary); border-color: var(--accent-green); }
        .mode-btn.active { background: var(--accent-green); color: #000; border-color: var(--accent-green); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Cluster Health Monitor</h1>
                <span style="font-size: 0.8em; opacity: 0.8;">Auto-refresh: <span id="countdown">5</span>s</span>
            </div>
            <div id="status-badge" class="status-badge status-healthy">HEALTHY</div>
        </header>
        
        <div class="tabs">
            <div class="tab active" data-tab="home">Home</div>
            <div class="tab" data-tab="history">History</div>
            <div class="tab" data-tab="processes">Processes</div>
            <div class="tab" data-tab="benchmark">Benchmark</div>
            <div class="tab" data-tab="export">Export</div>
        </div>
        
        <!-- HOME TAB -->
        <div id="home" class="tab-content active">
            <div class="grid">
                <div class="card">
                    <h2>GPU Status</h2>
                    <div id="gpu-list">Loading...</div>
                </div>
                <div class="card">
                    <h2>System</h2>
                    <div id="system-info">Loading...</div>
                </div>
            </div>
            <div class="card">
                <h2>Alerts</h2>
                <div id="alerts-list">No active alerts</div>
            </div>
        </div>
        
        <!-- HISTORY TAB -->
        <div id="history" class="tab-content">
            <div class="chart-container">
                <div class="chart-controls">
                    <select id="metric-select">
                        <option value="gpu_0_utilization">GPU Utilization (%)</option>
                        <option value="gpu_0_memory_used">GPU Memory (MB)</option>
                        <option value="gpu_0_temperature">GPU Temperature (°C)</option>
                        <option value="gpu_0_power">GPU Power (W)</option>
                        <option value="cpu_percent">CPU Usage (%)</option>
                        <option value="memory_percent">RAM Usage (%)</option>
                    </select>
                    <select id="hours-select">
                        <option value="1">Last 1 hour</option>
                        <option value="6">Last 6 hours</option>
                        <option value="24">Last 24 hours</option>
                        <option value="168">Last 7 days</option>
                    </select>
                    <button onclick="loadHistory()">Refresh</button>
                </div>
                <canvas id="historyChart" height="100"></canvas>
            </div>
        </div>
        
        <!-- PROCESSES TAB -->
        <div id="processes" class="tab-content">
            <div class="card">
                <h2>GPU Processes</h2>
                <button onclick="loadProcesses()" style="margin-bottom: 15px; padding: 8px 15px; background: var(--accent-blue); border: none; border-radius: 6px; color: white; cursor: pointer;">Refresh</button>
                <table class="process-table">
                    <thead>
                        <tr>
                            <th>PID</th>
                            <th>Process</th>
                            <th>GPU</th>
                            <th>GPU Memory</th>
                            <th>User</th>
                        </tr>
                    </thead>
                    <tbody id="process-list">
                        <tr><td colspan="5">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- EXPORT TAB -->
        <div id="export" class="tab-content">
            <div class="card">
                <h2>Export Data</h2>
                <p style="margin-bottom: 20px; color: var(--text-secondary);">Download collected metrics data for analysis.</p>
                <div class="chart-controls" style="margin-bottom: 20px;">
                    <select id="export-hours">
                        <option value="1">Last 1 hour</option>
                        <option value="6">Last 6 hours</option>
                        <option value="24" selected>Last 24 hours</option>
                        <option value="168">Last 7 days</option>
                    </select>
                </div>
                <div class="export-section">
                    <button class="export-btn" onclick="exportData('json')">Download JSON</button>
                    <button class="export-btn secondary" onclick="exportData('csv')">Download CSV</button>
                </div>
            </div>
        </div>
        
        <!-- BENCHMARK TAB -->
        <div id="benchmark" class="tab-content">
            <div class="card">
                <h2>GPU Benchmark</h2>
                <p style="margin-bottom: 10px; color: var(--text-secondary);">Stress test using matrix multiplication workload. Faster GPUs complete more iterations.</p>
                <p id="workload-info" style="margin-bottom: 20px; color: var(--accent-blue); font-size: 0.9em;"></p>
                
                <div id="baseline-info" style="display: none; background: var(--bg-tertiary); padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid var(--accent-green);">
                    <h4 style="color: var(--accent-green); margin-bottom: 10px;">Baseline Saved</h4>
                    <div id="baseline-details"></div>
                </div>
                
                <div id="benchmark-controls">
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 8px; color: var(--text-secondary);">Test Mode</label>
                        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                            <button class="mode-btn active" data-mode="quick" onclick="selectMode('quick')">Quick (15s)</button>
                            <button class="mode-btn" data-mode="standard" onclick="selectMode('standard')">Standard (60s)</button>
                            <button class="mode-btn" data-mode="stress" onclick="selectMode('stress')">Stress (180s)</button>
                            <button class="mode-btn" data-mode="custom" onclick="selectMode('custom')">Custom</button>
                        </div>
                    </div>
                    
                    <div id="custom-controls" style="display: none; background: var(--bg-tertiary); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                            <div>
                                <label style="display: block; margin-bottom: 5px; color: var(--text-secondary);">Duration (seconds)</label>
                                <input type="range" id="custom-duration" min="10" max="300" value="60" oninput="updateSliderValue('duration')">
                                <input type="number" id="custom-duration-val" value="60" min="10" max="300" style="width: 80px; padding: 5px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary);">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; color: var(--text-secondary);">Temp Limit (C) - 0 = no limit</label>
                                <input type="range" id="custom-temp" min="0" max="100" value="85" oninput="updateSliderValue('temp')">
                                <input type="number" id="custom-temp-val" value="85" min="0" max="100" style="width: 80px; padding: 5px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary);">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; color: var(--text-secondary);">Memory Limit (MB) - 0 = no limit</label>
                                <input type="range" id="custom-memory" min="0" max="48000" value="0" step="1000" oninput="updateSliderValue('memory')">
                                <input type="number" id="custom-memory-val" value="0" min="0" max="48000" style="width: 80px; padding: 5px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary);">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; color: var(--text-secondary);">Power Limit (W) - 0 = no limit</label>
                                <input type="range" id="custom-power" min="0" max="500" value="0" step="10" oninput="updateSliderValue('power')">
                                <input type="number" id="custom-power-val" value="0" min="0" max="500" style="width: 80px; padding: 5px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary);">
                            </div>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <button class="export-btn" onclick="startBenchmark()" id="start-bench-btn">Start Benchmark</button>
                        <button class="export-btn secondary" onclick="stopBenchmark()" id="stop-bench-btn" style="display: none;">Stop</button>
                        <span id="iteration-counter" style="display: none; font-size: 1.2em; color: var(--accent-green); font-weight: bold; margin-left: 20px;"></span>
                    </div>
                </div>
                
                <div id="benchmark-progress" style="display: none; margin: 20px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span id="bench-status">Running...</span>
                        <span id="bench-stop-reason" style="color: var(--accent-yellow);"></span>
                    </div>
                    <div class="progress-bar" style="height: 20px;">
                        <div class="progress-fill" id="bench-progress-bar" style="width: 0%;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <span id="bench-percent" style="font-size: 0.9em;">0%</span>
                        <span id="bench-workload" style="font-size: 0.9em; color: var(--text-secondary);"></span>
                    </div>
                </div>
                
                <div id="benchmark-live-charts" style="display: none; margin: 20px 0;">
                    <h3 style="color: var(--accent-green); margin-bottom: 15px;">Real-time Metrics</h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                        <div class="gpu-card">
                            <h4 style="color: var(--accent-green); margin-bottom: 10px; font-size: 0.9em;">GPU Utilization (%)</h4>
                            <canvas id="chartUtilization" height="60"></canvas>
                        </div>
                        <div class="gpu-card">
                            <h4 style="color: var(--accent-yellow); margin-bottom: 10px; font-size: 0.9em;">Temperature (C)</h4>
                            <canvas id="chartTemperature" height="60"></canvas>
                        </div>
                        <div class="gpu-card">
                            <h4 style="color: var(--accent-blue); margin-bottom: 10px; font-size: 0.9em;">Memory Used (MB)</h4>
                            <canvas id="chartMemory" height="60"></canvas>
                        </div>
                        <div class="gpu-card">
                            <h4 style="color: var(--accent-red); margin-bottom: 10px; font-size: 0.9em;">Power Draw (W)</h4>
                            <canvas id="chartPower" height="60"></canvas>
                        </div>
                    </div>
                </div>
                
                <div id="benchmark-results" style="margin-top: 20px;"></div>
            </div>
        </div>
        
        <footer>
            <p>Cluster Health Monitor v1.0.0 | <span id="last-update">-</span></p>
        </footer>
    </div>
    
    <script>
        let countdown = 5;
        let historyChart = null;
        
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
                const response = await fetch('/api/status');
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        function updateDashboard(data) {
            const badge = document.getElementById('status-badge');
            badge.className = 'status-badge status-' + data.status;
            badge.textContent = data.status.toUpperCase();
            
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
                const historyResponse = await fetch(`/api/history?metric=${metric}&hours=${hours}`);
                const historyData = await historyResponse.json();
                
                const ctx = document.getElementById('historyChart').getContext('2d');
                
                if (historyChart) historyChart.destroy();

                const getUnit = (metric) => {
                    if (metric.includes('utilization') || metric.includes('percent')) return '%';
                    if (metric.includes('memory_used')) return 'MB';
                    if (metric.includes('temperature')) return '°C';
                    if (metric.includes('power')) return 'W';
                    return '';
                }

                const unit = getUnit(metric);

                const yAxisOptions = {
                    ticks: { color: '#a0a0a0' },
                    grid: { color: '#4a4a4a' },
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: unit,
                        color: '#a0a0a0',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                };

                if (metric.includes('utilization') || metric.includes('percent')) {
                    yAxisOptions.suggestedMax = 100;
                }
                if (metric.includes('temperature')) {
                    yAxisOptions.suggestedMax = 100;
                }

                if (metric.startsWith('gpu_') && metric.includes('_memory_used')) {
                    const statusResponse = await fetch('/api/status');
                    const statusData = await statusResponse.json();
                    const gpuIndex = parseInt(metric.split('_')[1]);
                    const gpu = statusData.metrics.gpus[gpuIndex];
                    if (gpu && gpu.memory_total) {
                        yAxisOptions.max = gpu.memory_total;
                    }
                }
                
                historyChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: historyData.data.map(d => new Date(d.timestamp).toLocaleTimeString()),
                        datasets: [{
                            label: document.getElementById('metric-select').selectedOptions[0].text,
                            data: historyData.data.map(d => d.value),
                            borderColor: '#76b900',
                            backgroundColor: 'rgba(118, 185, 0, 0.1)',
                            fill: true,
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { 
                            legend: { 
                                display: true,
                                labels: { 
                                    color: '#f0f0f0',
                                    font: {
                                        size: 14
                                    }
                                } 
                            } 
                        },
                        scales: {
                            x: { 
                                ticks: { color: '#a0a0a0', maxTicksLimit: 10 }, 
                                grid: { color: '#4a4a4a' } 
                            },
                            y: yAxisOptions
                        }
                    }
                });
            } catch (error) {
                console.error('Error loading history:', error);
            }
        }
        
        async function loadProcesses() {
            try {
                const response = await fetch('/api/processes');
                const data = await response.json();
                
                const tbody = document.getElementById('process-list');
                if (data.processes.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" style="color: var(--text-secondary);">No GPU processes running</td></tr>';
                } else {
                    tbody.innerHTML = data.processes.map(p => `
                        <tr>
                            <td>${p.pid}</td>
                            <td>${p.name}</td>
                            <td>GPU ${p.gpu_index}</td>
                            <td>${p.gpu_memory_mb.toFixed(0)} MB</td>
                            <td>${p.username || 'N/A'}</td>
                        </tr>
                    `).join('');
                }
            } catch (error) {
                console.error('Error loading processes:', error);
            }
        }
        
        function exportData(format) {
            const hours = document.getElementById('export-hours').value;
            window.location.href = `/api/export/${format}?hours=${hours}`;
        }
        
        // Benchmark functions
        let benchmarkPollInterval = null;
        let benchCharts = {};
        let selectedMode = 'quick';
        
        // Load baseline on page load
        async function loadBaseline() {
            try {
                const response = await fetch('/api/benchmark/baseline');
                const baseline = await response.json();
                if (baseline && baseline.status !== 'no_baseline') {
                    document.getElementById('baseline-info').style.display = 'block';
                    document.getElementById('baseline-details').innerHTML = `
                        <div class="metric-row"><span class="metric-label">GPU</span><span class="metric-value">${baseline.gpu_name}</span></div>
                        <div class="metric-row"><span class="metric-label">Iterations</span><span class="metric-value">${baseline.iterations_completed}</span></div>
                        <div class="metric-row"><span class="metric-label">Avg Iteration</span><span class="metric-value">${baseline.avg_iteration_time_ms.toFixed(2)} ms</span></div>
                        <div class="metric-row"><span class="metric-label">Avg Temp</span><span class="metric-value">${baseline.avg_temperature.toFixed(1)} C</span></div>
                        <p style="font-size: 0.85em; color: var(--text-secondary); margin-top: 10px;">Saved: ${new Date(baseline.timestamp).toLocaleString()}</p>
                    `;
                }
            } catch (error) {
                console.error('Error loading baseline:', error);
            }
        }
        
        function selectMode(mode) {
            selectedMode = mode;
            document.querySelectorAll('.mode-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.mode === mode);
            });
            document.getElementById('custom-controls').style.display = mode === 'custom' ? 'block' : 'none';
        }
        
        function updateSliderValue(type) {
            const slider = document.getElementById('custom-' + type);
            const input = document.getElementById('custom-' + type + '-val');
            input.value = slider.value;
        }
        
        // Sync input to slider
        ['duration', 'temp', 'memory', 'power'].forEach(type => {
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
            let url = '/api/benchmark/start?mode=' + selectedMode;
            if (selectedMode === 'custom') {
                url += '&duration=' + document.getElementById('custom-duration-val').value;
                url += '&temp_limit=' + document.getElementById('custom-temp-val').value;
                url += '&memory_limit=' + document.getElementById('custom-memory-val').value;
                url += '&power_limit=' + document.getElementById('custom-power-val').value;
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
                
                document.getElementById('bench-progress-bar').style.width = status.progress + '%';
                document.getElementById('bench-percent').textContent = status.progress + '%';
                document.getElementById('iteration-counter').textContent = 'Iteration #' + (status.iterations || 0);
                document.getElementById('workload-info').textContent = 'Workload: ' + (status.workload_type || 'N/A');
                document.getElementById('bench-workload').textContent = status.workload_type || '';
                
                // Update live charts with samples
                if (samplesData.samples && benchCharts.utilization) {
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
                    document.getElementById('bench-status').textContent = 'Completed';
                    
                    const resultsResponse = await fetch('/api/benchmark/results');
                    const results = await resultsResponse.json();
                    displayBenchmarkResults(results);
                    
                    // Reload baseline if saved
                    loadBaseline();
                }
            } catch (error) {
                console.error('Error polling benchmark:', error);
            }
        }
        
        function displayBenchmarkResults(results) {
            if (!results || results.status === 'no_results') {
                document.getElementById('benchmark-results').innerHTML = '<p style="color: var(--text-secondary);">No results available</p>';
                return;
            }
            
            const gpuInfo = results.gpu_info || {};
            const config = results.config || {};
            const scores = results.scores || {};
            const baseline = results.baseline;
            
            // Show stop reason if benchmark was stopped early
            if (results.stop_reason && results.stop_reason !== 'Duration completed') {
                document.getElementById('bench-stop-reason').textContent = 'Stopped: ' + results.stop_reason;
            }
            
            // Baseline comparison
            let baselineComparison = '';
            if (baseline) {
                const iterDiff = results.iterations_completed - baseline.iterations_completed;
                const iterPct = ((iterDiff / baseline.iterations_completed) * 100).toFixed(1);
                const iterColor = iterDiff >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';
                baselineComparison = `
                    <div class="gpu-card" style="margin-bottom: 15px; border-left: 4px solid var(--accent-blue);">
                        <h3 style="color: var(--accent-blue); margin-bottom: 10px;">vs Baseline</h3>
                        <div class="metric-row">
                            <span class="metric-label">Iterations</span>
                            <span class="metric-value" style="color: ${iterColor};">${iterDiff >= 0 ? '+' : ''}${iterDiff} (${iterPct}%)</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Baseline Iterations</span>
                            <span class="metric-value">${baseline.iterations_completed}</span>
                        </div>
                    </div>
                `;
            }
            
            let html = `
                <div class="gpu-card" style="margin-bottom: 15px;">
                    <h3 style="color: var(--accent-green); margin-bottom: 10px;">GPU Info</h3>
                    <div class="metric-row"><span class="metric-label">Name</span><span class="metric-value">${gpuInfo.name || 'N/A'}</span></div>
                    <div class="metric-row"><span class="metric-label">Memory</span><span class="metric-value">${gpuInfo.memory_total_mb ? Math.round(gpuInfo.memory_total_mb) + ' MB' : 'N/A'}</span></div>
                    <div class="metric-row"><span class="metric-label">Driver</span><span class="metric-value">${gpuInfo.driver_version || 'N/A'}</span></div>
                </div>
                
                <div class="gpu-card" style="margin-bottom: 15px; background: var(--accent-green); color: #000;">
                    <h3 style="margin-bottom: 5px;">Performance Results</h3>
                    <div style="display: flex; gap: 30px; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span style="font-size: 2.5em; font-weight: bold;">${results.iterations_completed || 0}</span>
                            <span style="font-size: 1em;"> iterations</span>
                        </div>
                        <div>
                            <span style="font-size: 1.5em; font-weight: bold;">${results.avg_iteration_time_ms || 0}</span>
                            <span style="font-size: 0.9em;"> ms/iter</span>
                        </div>
                        <div>
                            <span style="font-size: 1.5em; font-weight: bold;">${results.iterations_per_second || 0}</span>
                            <span style="font-size: 0.9em;"> iter/sec</span>
                        </div>
                    </div>
                    ${results.saved_as_baseline ? '<p style="margin-top: 10px; font-size: 0.9em;">Saved as new baseline</p>' : ''}
                </div>
                
                ${baselineComparison}
                
                <div class="gpu-card" style="margin-bottom: 15px;">
                    <h3 style="color: var(--accent-blue); margin-bottom: 10px;">Test Config</h3>
                    <div class="metric-row"><span class="metric-label">Workload</span><span class="metric-value">${results.workload_type || 'N/A'}</span></div>
                    <div class="metric-row"><span class="metric-label">Mode</span><span class="metric-value">${config.mode || 'N/A'}</span></div>
                    <div class="metric-row"><span class="metric-label">Duration</span><span class="metric-value">${results.duration_actual_sec || 0}s / ${config.duration_seconds || 0}s</span></div>
                    <div class="metric-row"><span class="metric-label">Stop Reason</span><span class="metric-value">${results.stop_reason || 'N/A'}</span></div>
                </div>
                
                <div class="gpu-card" style="margin-bottom: 15px;">
                    <h3 style="color: var(--accent-yellow); margin-bottom: 10px;">Scores</h3>
                    <div class="metric-row"><span class="metric-label">Stability</span><span class="metric-value">${scores.stability || 0}/100</span></div>
                    <div class="metric-row"><span class="metric-label">Thermal</span><span class="metric-value">${scores.thermal || 0}/100</span></div>
                    <div class="metric-row"><span class="metric-label">Performance</span><span class="metric-value">${scores.performance || 0}/100</span></div>
                    <div class="metric-row"><span class="metric-label">Overall</span><span class="metric-value" style="color: var(--accent-green); font-weight: bold;">${scores.overall || 0}/100</span></div>
                </div>
                
                <h3 style="color: var(--accent-green); margin: 20px 0 10px;">Metrics Summary</h3>
            `;
            
            const metrics = [
                { key: 'utilization', label: 'Utilization', unit: '%' },
                { key: 'temperature_c', label: 'Temperature', unit: 'C' },
                { key: 'memory_used_mb', label: 'Memory Used', unit: 'MB' },
                { key: 'power_w', label: 'Power Draw', unit: 'W' }
            ];
            
            metrics.forEach(m => {
                const data = results[m.key];
                if (data) {
                    html += `
                        <div class="gpu-card" style="margin-bottom: 10px;">
                            <div class="gpu-header">
                                <span class="gpu-name">${m.label}</span>
                            </div>
                            <div class="metric-row"><span class="metric-label">Min</span><span class="metric-value">${data.min} ${m.unit}</span></div>
                            <div class="metric-row"><span class="metric-label">Avg</span><span class="metric-value">${data.avg} ${m.unit}</span></div>
                            <div class="metric-row"><span class="metric-label">Max</span><span class="metric-value">${data.max} ${m.unit}</span></div>
                        </div>
                    `;
                }
            });
            
            html += `<p style="color: var(--text-secondary); margin-top: 15px; font-size: 0.9em;">Benchmark completed at ${new Date(results.timestamp).toLocaleString()}</p>`;
            
            document.getElementById('benchmark-results').innerHTML = html;
        }
        
        function tick() {
            countdown--;
            document.getElementById('countdown').textContent = countdown;
            if (countdown <= 0) {
                countdown = 5;
                fetchStatus();
            }
        }
        
        fetchStatus();
        loadBaseline();
        setInterval(tick, 1000);
    </script>
</body>
</html>'''
