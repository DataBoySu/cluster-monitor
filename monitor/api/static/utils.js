// utils.js - Dashboard update and utility functions

function updateDashboard(data) {
    console.log('Updating dashboard with:', data);
    const badge = document.getElementById('status-badge');
    badge.className = 'status-badge status-' + data.status;
    badge.textContent = data.status.toUpperCase();
    
    // Add tooltip with alert count
    const alertCount = data.alerts ? data.alerts.length : 0;
    if (data.status === 'warning' && alertCount > 0) {
        badge.setAttribute('data-tooltip', `${alertCount} active alert${alertCount > 1 ? 's' : ''}`);
    } else if (data.status === 'info') {
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
        
        const tbody = document.getElementById('process-list');
        if (!data.processes || data.processes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="color: var(--text-secondary);">No GPU processes running</td></tr>';
        } else {
            // Check if any process has utilization data
            const hasUtilData = data.processes.some(p => p.gpu_utilization !== null && p.gpu_utilization !== undefined);
            
            // Sort by GPU memory usage (descending)
            const sorted = data.processes.sort((a, b) => (b.gpu_memory_mb || 0) - (a.gpu_memory_mb || 0));
            
            tbody.innerHTML = sorted.map(p => {
                let utilDisplay;
                if (p.gpu_utilization !== null && p.gpu_utilization !== undefined) {
                    utilDisplay = `${p.gpu_utilization.toFixed(1)}%`;
                } else if (hasUtilData) {
                    // Some processes have data, this one doesn't
                    utilDisplay = '<span style="opacity: 0.5;">N/A</span>';
                } else {
                    // No processes have data - show helpful message on first row only
                    if (sorted.indexOf(p) === 0) {
                        utilDisplay = '<span style="opacity: 0.5;" title="Per-process GPU utilization requires:\n1. CUDA/compute workloads (not graphics)\n2. Accounting mode enabled\n3. Supported GPU hardware">Not available</span>';
                    } else {
                        utilDisplay = '<span style="opacity: 0.5;">—</span>';
                    }
                }
                
                return `
                    <tr>
                        <td>${p.pid}</td>
                        <td>${p.name || 'N/A'}</td>
                        <td>GPU ${p.gpu_index}</td>
                        <td>${utilDisplay}</td>
                        <td>${p.username || 'N/A'}</td>
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
