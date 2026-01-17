import subprocess
import os
import csv
import io
from typing import List, Dict, Any
import importlib
import importlib.util
import warnings

_pynvml_mod = None

for _name in ('nvidia_ml_py.pynvml', 'nvidia_ml_py'):
    try:
        _pynvml_mod = importlib.import_module(_name)
        break
    except ModuleNotFoundError:
        # Not installed, try next candidate
        continue
    except Exception:
        # Any other import error (e.g. runtime error inside module) should not crash import path
        _pynvml_mod = None
        break

PYNVML_AVAILABLE = _pynvml_mod is not None
if PYNVML_AVAILABLE:
    pynvml = _pynvml_mod

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class GPUCollector:
    """Collects GPU metrics via NVML or nvidia-smi fallback."""
    
    def __init__(self):
        self.nvml_initialized = False
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.nvml_initialized = True
            except Exception:
                pass
    
    def __del__(self):
        if self.nvml_initialized:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass
    
    def collect(self) -> List[Dict[str, Any]]:
        if self.nvml_initialized:
            return self._collect_nvml()
        else:
            return self._collect_nvidia_smi()
    
    def collect_processes(self) -> List[Dict[str, Any]]:
        """Get detailed process info for all GPUs with utilization."""
        # Try to get utilization data from nvidia-smi accounting mode
        utilization_map = self._get_process_utilization()
        
        if not self.nvml_initialized:
            return self._collect_processes_nvidia_smi(utilization_map)
        
        processes = []
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                gpu_name = pynvml.nvmlDeviceGetName(handle)
                
                try:
                    procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
                    for proc in procs:
                        proc_info = {
                            'gpu_index': i,
                            'gpu_name': gpu_name,
                            'pid': proc.pid,
                            'gpu_memory_mb': proc.usedGpuMemory / (1024**2) if proc.usedGpuMemory else 0,
                            'gpu_utilization': utilization_map.get(proc.pid, {}).get('gpu_util', None),
                            'name': 'Unknown',
                            'username': 'Unknown',
                        }
                        
                        if PSUTIL_AVAILABLE:
                            try:
                                p = psutil.Process(proc.pid)
                                proc_info['name'] = p.name()
                                proc_info['username'] = p.username()
                                proc_info['cpu_percent'] = p.cpu_percent()
                                proc_info['memory_mb'] = p.memory_info().rss / (1024**2)
                                proc_info['cmdline'] = ' '.join(p.cmdline()[:3])
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                        else:
                            try:
                                uname = self._resolve_username(proc.pid)
                                if uname:
                                    proc_info['username'] = uname
                            except Exception:
                                pass
                        
                        processes.append(proc_info)
                except Exception:
                    pass
        except Exception:
            pass
        
        return processes
    
    def _get_process_utilization(self) -> Dict[int, Dict[str, Any]]:
        """Get per-process GPU utilization using nvidia-smi accounting mode.
        
        Note: This only works for CUDA/compute workloads, not graphics processes.
        Requires accounting mode to be enabled: nvidia-smi --accounting-mode=1
        """
        utilization_map = {}
        
        try:
            # Try to query accounted apps (requires accounting mode enabled)
            result = subprocess.run(
                ['nvidia-smi', '--query-accounted-apps=pid,gpu_util,mem_util',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                reader = csv.reader(io.StringIO(result.stdout))
                for row in reader:
                    if len(row) >= 2:
                        try:
                            pid = int(row[0].strip())
                            gpu_util = float(row[1].strip()) if row[1].strip() != '[N/A]' else None
                            utilization_map[pid] = {
                                'gpu_util': gpu_util,
                            }
                        except (ValueError, IndexError):
                            continue
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            # Accounting mode not available or nvidia-smi failed
            # This is expected for graphics workloads or when accounting is disabled
            pass
        
        return utilization_map
    
    def _collect_processes_nvidia_smi(self, utilization_map: Dict[int, Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fallback process collection via nvidia-smi."""
        if utilization_map is None:
            utilization_map = {}
        
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-compute-apps=gpu_uuid,pid,used_memory,process_name',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            processes = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 4:
                    pid = int(parts[1])
                    proc_info = {
                        'gpu_index': 0,
                        'pid': pid,
                        'gpu_memory_mb': float(parts[2]) if parts[2] != '[N/A]' else 0,
                        'name': parts[3],
                        'gpu_utilization': utilization_map.get(pid, {}).get('gpu_util', None),
                    }
                    try:
                        if PSUTIL_AVAILABLE:
                            p = psutil.Process(pid)
                            proc_info['username'] = p.username()
                        else:
                            uname = self._resolve_username(pid)
                            if uname:
                                proc_info['username'] = uname
                            else:
                                proc_info['username'] = 'Unknown'
                    except Exception:
                        proc_info['username'] = 'Unknown'

                    processes.append(proc_info)
            return processes
        except Exception:
            return []
    
    def _collect_nvml(self) -> List[Dict[str, Any]]:
        gpus = []
        device_count = pynvml.nvmlDeviceGetCount()
        
        for i in range(device_count):
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                try:
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    gpu_util = util.gpu
                except Exception:
                    gpu_util = 0
                
                try:
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except Exception:
                    temp = 0
                
                try:
                    power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000  # mW to W
                except Exception:
                    power = 0
                
                try:
                    procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
                    num_procs = len(procs)
                except Exception:
                    num_procs = 0
                
                gpus.append({
                    'index': i,
                    'name': pynvml.nvmlDeviceGetName(handle),
                    'utilization': gpu_util,
                    'memory_used': mem.used / (1024**2),  # MB
                    'memory_total': mem.total / (1024**2),
                    'memory_free': mem.free / (1024**2),
                    'temperature': temp,
                    'power': power,
                    'processes': num_procs,
                })
                
            except Exception as e:
                gpus.append({'index': i, 'error': str(e)})
        
        return gpus
    
    def _collect_nvidia_smi(self) -> List[Dict[str, Any]]:
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,utilization.gpu,memory.used,memory.total,'
                 'temperature.gpu,power.draw',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return [{'error': 'nvidia-smi failed'}]
            
            gpus = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 7:
                    mem_used = float(parts[3]) if parts[3] != '[N/A]' else 0
                    mem_total = float(parts[4]) if parts[4] != '[N/A]' else 0
                    gpus.append({
                        'index': int(parts[0]),
                        'name': parts[1],
                        'utilization': int(parts[2]) if parts[2] != '[N/A]' else 0,
                        'memory_used': mem_used,
                        'memory_total': mem_total,
                        'memory_free': mem_total - mem_used,
                        'temperature': int(parts[5]) if parts[5] != '[N/A]' else 0,
                        'power': float(parts[6]) if parts[6] != '[N/A]' else 0,
                    })
            
            return gpus
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def _resolve_username(self, pid: int) -> str:
        """Attempt to resolve the username owning a PID using OS utilities.

        Uses `ps` on POSIX and PowerShell/WMI on Windows as a fallback when
        psutil is not available or cannot access the process.
        Returns empty string if resolution fails.
        """
        try:
            import platform
            import subprocess
            system = platform.system()
            if system == 'Windows':
                # Use WMI via PowerShell to get the process owner
                # This is a fallback when psutil is not available
                cmd = [
                    'powershell', '-NoProfile', '-NonInteractive',
                    '-Command',
                    f"(Get-WmiObject -Class Win32_Process -Filter \"ProcessId={pid}\").GetOwner().User"
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
                out = (proc.stdout or '').strip()
                return out if out else ''
            elif system == 'Darwin':
                # macOS: use ps -o user= -p PID
                cmd = ['ps', '-o', 'user=', '-p', str(pid)]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                return (proc.stdout or '').strip()
            else:
                # Linux/POSIX: use ps -o user= -p PID
                cmd = ['ps', '-o', 'user=', '-p', str(pid)]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                return (proc.stdout or '').strip()
        except Exception:
            pass
        return ''
