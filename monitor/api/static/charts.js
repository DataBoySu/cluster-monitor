// charts.js - Chart initialization and update functions

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

function updateLiveCharts(metrics) {
    if (!benchCharts.utilization) return;
    
    const currentTime = new Date().toLocaleTimeString();
    
    // Update each chart with new data point
    // Backend sends: utilization, temperature_c, memory_used_mb, power_w
    const charts = {
        utilization: metrics.utilization || 0,
        temperature: metrics.temperature_c || 0,
        memory: metrics.memory_used_mb || 0,
        power: metrics.power_w || 0
    };
    
    Object.entries(charts).forEach(([key, value]) => {
        const chart = benchCharts[key];
        if (chart) {
            chart.data.labels.push(currentTime);
            chart.data.datasets[0].data.push(value);
            
            // Keep only last 50 data points
            if (chart.data.labels.length > 50) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            
            chart.update('none');
        }
    });
}
