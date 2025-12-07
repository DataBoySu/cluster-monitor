"""GPU metrics sampling and monitoring."""

import time
import subprocess
import threading
from typing import Dict, Any, Optional, List


class GPUMetricsSampler:
    """Handles GPU metrics collection via nvidia-smi in a separate thread."""
    
    def __init__(self):
        """Initialize metrics sampler."""
        self.nvidia_smi_error_count = 0
        self.max_consecutive_errors = 5
        self._current_util = 0.0
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self.sample_interval = 0.1  # 100ms between samples for real-time feel
    
    def start(self):
        """Start the background metrics collection thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._sampling_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the background metrics collection thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def _sampling_loop(self):
        """Background thread that continuously samples GPU metrics."""
        while self._running:
            try:
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=utilization.gpu',
                     '--format=csv,noheader,nounits'],
                    capture_output=True, text=True, timeout=1
                )
                
                if result.returncode == 0:
                    util_str = result.stdout.strip()
                    if util_str and util_str != '[N/A]':
                        util_val = float(util_str)
                        with self._lock:
                            self._current_util = util_val
                        self.nvidia_smi_error_count = 0
                else:
                    self.nvidia_smi_error_count += 1
            except Exception:
                self.nvidia_smi_error_count += 1
            
            time.sleep(self.sample_interval)
    
    def get_current_util(self) -> float:
        """Get current GPU utilization (thread-safe)."""
        with self._lock:
            return self._current_util
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information via nvidia-smi."""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total,driver_version,pcie.link.gen.current,pcie.link.width.current',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return {'error': 'nvidia-smi failed'}
            
            parts = [p.strip() for p in result.stdout.strip().split(',')]
            return {
                'name': parts[0],
                'memory_total_mb': float(parts[1]),
                'driver_version': parts[2],
                'pcie_gen': parts[3],
                'pcie_width': parts[4],
            }
        except Exception as e:
            return {'error': str(e)}
    
    def sample_metrics(self) -> Dict[str, Any]:
        """Collect a single sample of GPU metrics via nvidia-smi (for logging/storage)."""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=1
            )
            
            if result.returncode != 0:
                return {'error': 'nvidia-smi failed', 'timestamp': time.time()}
            
            parts = [p.strip() for p in result.stdout.strip().split(',')]
            util_val = float(parts[0]) if parts[0] != '[N/A]' else 0
            
            return {
                'timestamp': time.time(),
                'utilization': util_val,
                'memory_used_mb': float(parts[1]) if parts[1] != '[N/A]' else 0,
                'memory_total_mb': float(parts[2]) if parts[2] != '[N/A]' else 0,
                'temperature_c': float(parts[3]) if parts[3] != '[N/A]' else 0,
                'power_w': float(parts[4]) if parts[4] != '[N/A]' else 0,
            }
        except Exception as e:
            return {'error': str(e), 'timestamp': time.time()}
    
    def should_sample(self, elapsed: float) -> bool:
        """Check if it's time to take a new sample (for logging)."""
        # For storage sampling, use a longer interval
        return True  # Let caller decide when to sample
    
    def check_stop_conditions(self, sample: Dict[str, Any], config) -> Optional[str]:
        """Check if any stop condition is met."""
        # Don't stop on nvidia-smi errors - simulation can run without metrics
        
        if config.temp_limit_c > 0 and sample.get('temperature_c', 0) >= config.temp_limit_c:
            return f"Temperature limit reached ({sample['temperature_c']}C >= {config.temp_limit_c}C)"
        
        if config.power_limit_w > 0 and sample.get('power_w', 0) >= config.power_limit_w:
            return f"Power limit reached ({sample['power_w']}W >= {config.power_limit_w}W)"
        
        if config.memory_limit_mb > 0 and sample.get('memory_used_mb', 0) >= config.memory_limit_mb:
            return f"Memory limit reached ({sample['memory_used_mb']}MB >= {config.memory_limit_mb}MB)"
        
        return None
