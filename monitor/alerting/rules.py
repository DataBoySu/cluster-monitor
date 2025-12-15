"""Alert rules engine for evaluating metrics against thresholds.

Maintenance:
- Purpose: encapsulate alert logic for GPU and system metrics.
- Debug: if alerts are not firing, verify metric keys (e.g., 'gpus', 'temperature')
    and the configuration passed to the engine. Alerts are returned as a list
    of dictionaries and not persisted by this module.
"""

from datetime import datetime
from typing import Dict, Any, List


class AlertEngine:
    """Evaluates metrics against alert thresholds."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_alerts = []
    
    def check(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts = []
        hostname = metrics.get('hostname', 'unknown')
        timestamp = datetime.now().isoformat()
        
        # Check GPU alerts
        for gpu in metrics.get('gpus', []):
            if 'error' in gpu:
                continue
            
            gpu_index = gpu.get('index', 0)
            
            # Temperature alerts
            temp = gpu.get('temperature', 0)
            temp_critical = self.config.get('gpu_temperature_critical', 90)
            temp_warn = self.config.get('gpu_temperature_warn', 80)
            
            if temp >= temp_critical:
                alerts.append({
                    'timestamp': timestamp,
                    'hostname': hostname,
                    'name': f'gpu_{gpu_index}_temp_critical',
                    'severity': 'critical',
                    'message': f'GPU {gpu_index} temperature critical: {temp}°C',
                })
            elif temp >= temp_warn:
                alerts.append({
                    'timestamp': timestamp,
                    'hostname': hostname,
                    'name': f'gpu_{gpu_index}_temp_warn',
                    'severity': 'warning',
                    'message': f'GPU {gpu_index} temperature warning: {temp}°C',
                })
            
            # Memory usage alerts
            mem_used = gpu.get('memory_used', 0)
            mem_total = gpu.get('memory_total', 1)
            mem_pct = (mem_used / mem_total * 100) if mem_total > 0 else 0
            mem_warn = self.config.get('gpu_memory_usage_warn', 90)
            
            if mem_pct >= mem_warn:
                alerts.append({
                    'timestamp': timestamp,
                    'hostname': hostname,
                    'name': f'gpu_{gpu_index}_memory_high',
                    'severity': 'warning',
                    'message': f'GPU {gpu_index} memory usage high: {mem_pct:.0f}%',
                })
            
            # Low utilization alert (possibly idle GPU)
            util = gpu.get('utilization', 0)
            util_low = self.config.get('gpu_utilization_low', 10)
            
            if util < util_low:
                alerts.append({
                    'timestamp': timestamp,
                    'hostname': hostname,
                    'name': f'gpu_{gpu_index}_idle',
                    'severity': 'info',
                    'message': f'GPU {gpu_index} appears idle: {util}% utilization',
                })
        
        # Check system alerts
        sys_metrics = metrics.get('system', {})
        
        # High CPU usage
        cpu_pct = sys_metrics.get('cpu_percent', 0)
        if cpu_pct >= 95:
            alerts.append({
                'timestamp': timestamp,
                'hostname': hostname,
                'name': 'cpu_high',
                'severity': 'warning',
                'message': f'CPU usage very high: {cpu_pct:.0f}%',
            })
        
        # Low memory
        mem_pct = sys_metrics.get('memory_percent', 0)
        if mem_pct >= 95:
            alerts.append({
                'timestamp': timestamp,
                'hostname': hostname,
                'name': 'memory_high',
                'severity': 'critical',
                'message': f'System memory nearly exhausted: {mem_pct:.0f}%',
            })
        
        # Low disk space
        disk_pct = sys_metrics.get('disk_percent', 0)
        if disk_pct >= 90:
            alerts.append({
                'timestamp': timestamp,
                'hostname': hostname,
                'name': 'disk_high',
                'severity': 'warning',
                'message': f'Disk space running low: {disk_pct:.0f}%',
            })
        
        self.active_alerts = alerts
        return alerts
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        return self.active_alerts
