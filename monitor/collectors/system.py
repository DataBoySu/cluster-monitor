"""System metrics collector for CPU, memory, disk.

Maintenance:
- Purpose: expose system-level metrics via psutil when available.
- Debug: if `psutil` is unavailable, the collector will provide best-effort values
    and include a warning in the returned metrics. For Windows, some fields may be
    less accurate.
"""

import os
import platform
import socket
from typing import Dict, Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class SystemCollector:
    """Collects system metrics via psutil."""
    
    def collect(self) -> Dict[str, Any]:
        metrics = {
            'hostname': socket.gethostname(),
            'platform': platform.system(),
        }
        
        if PSUTIL_AVAILABLE:
            metrics.update(self._collect_psutil())
        else:
            metrics['warning'] = 'Install psutil for detailed system metrics'
        
        return metrics
    
    def _collect_psutil(self) -> Dict[str, Any]:
        metrics = {}
        
        # CPU
        try:
            metrics['cpu_percent'] = psutil.cpu_percent(interval=0.1)
            metrics['cpu_count'] = psutil.cpu_count()
            metrics['cpu_freq'] = psutil.cpu_freq().current if psutil.cpu_freq() else 0
        except Exception as e:
            metrics['cpu_error'] = str(e)
        
        # Memory
        try:
            mem = psutil.virtual_memory()
            metrics['memory_total_gb'] = mem.total / (1024**3)
            metrics['memory_used_gb'] = mem.used / (1024**3)
            metrics['memory_available_gb'] = mem.available / (1024**3)
            metrics['memory_percent'] = mem.percent
        except Exception as e:
            metrics['memory_error'] = str(e)
        
        # Disk
        try:
            disk = psutil.disk_usage('/')
            metrics['disk_total_gb'] = disk.total / (1024**3)
            metrics['disk_used_gb'] = disk.used / (1024**3)
            metrics['disk_free_gb'] = disk.free / (1024**3)
            metrics['disk_percent'] = disk.percent
        except Exception as e:
            metrics['disk_error'] = str(e)
        
        # Load average (Unix only)
        try:
            if hasattr(os, 'getloadavg'):
                metrics['load_avg'] = list(os.getloadavg())
            else:
                metrics['load_avg'] = [0, 0, 0]
        except Exception:
            metrics['load_avg'] = [0, 0, 0]
        
        # Network I/O
        try:
            net = psutil.net_io_counters()
            metrics['net_bytes_sent'] = net.bytes_sent
            metrics['net_bytes_recv'] = net.bytes_recv
        except Exception:
            pass
        
        # Boot time
        try:
            metrics['uptime_seconds'] = (psutil.time.time() - psutil.boot_time())
        except Exception:
            pass
        
        return metrics
