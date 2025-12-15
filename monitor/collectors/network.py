"""Network metrics collector for interfaces and connectivity.

Maintenance:
- Purpose: gather interface, IP and I/O stats via psutil when available.
- Debug: `ping_host` uses OS ping—results and parsing differ between platforms.
"""

import subprocess
import socket
import platform
from typing import Dict, Any, List, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class NetworkCollector:
    """Collects network metrics via psutil."""
    
    def collect(self) -> Dict[str, Any]:
        metrics = {
            'interfaces': [],
            'hostname': socket.gethostname(),
        }
        
        if PSUTIL_AVAILABLE:
            metrics['interfaces'] = self._collect_interfaces()
        
        return metrics
    
    def _collect_interfaces(self) -> List[Dict[str, Any]]:
        interfaces = []
        
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io = psutil.net_io_counters(pernic=True)
            
            for name, addr_list in addrs.items():
                if name in stats and stats[name].isup:
                    iface = {
                        'name': name,
                        'speed_mbps': stats[name].speed,
                        'mtu': stats[name].mtu,
                        'is_up': stats[name].isup,
                    }
                    
                    # Get IPv4 address
                    for addr in addr_list:
                        if addr.family == socket.AF_INET:
                            iface['ipv4'] = addr.address
                            break
                    
                    # Get I/O stats
                    if name in io:
                        iface['bytes_sent'] = io[name].bytes_sent
                        iface['bytes_recv'] = io[name].bytes_recv
                    
                    interfaces.append(iface)
                    
        except Exception:
            pass
        
        return interfaces
    
    def ping_host(self, host: str, count: int = 3) -> Dict[str, Any]:
        result = {
            'host': host,
            'reachable': False,
            'latency_ms': None,
        }
        
        try:
            if platform.system() == 'Windows':
                cmd = ['ping', '-n', str(count), '-w', '1000', host]
            else:
                cmd = ['ping', '-c', str(count), '-W', '1', host]
            
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if proc.returncode == 0:
                result['reachable'] = True
                
                # Parse latency
                import re
                # Linux: rtt min/avg/max/mdev = 0.1/0.2/0.3/0.1 ms
                match = re.search(r'avg[^=]*=\s*[\d.]+/([\d.]+)/', proc.stdout)
                if match:
                    result['latency_ms'] = float(match.group(1))
                else:
                    # Windows: Average = 1ms
                    match = re.search(r'Average\s*=\s*(\d+)ms', proc.stdout)
                    if match:
                        result['latency_ms'] = float(match.group(1))
                        
        except Exception as e:
            result['error'] = str(e)
        
        return result
