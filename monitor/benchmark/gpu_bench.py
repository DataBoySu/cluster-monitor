"""GPU Benchmark with real-time monitoring and configurable tests."""

import time
import subprocess
import json
import sqlite3
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BenchmarkConfig:
    mode: str = "standard"
    duration_seconds: int = 30
    memory_limit_mb: int = 0  # 0 = no limit
    temp_limit_c: int = 85
    power_limit_w: int = 0  # 0 = no limit
    sample_interval_ms: int = 500
    
    @classmethod
    def from_mode(cls, mode: str) -> 'BenchmarkConfig':
        presets = {
            'quick': cls(mode='quick', duration_seconds=15, temp_limit_c=85, sample_interval_ms=500),
            'standard': cls(mode='standard', duration_seconds=60, temp_limit_c=85, sample_interval_ms=500),
            'stress': cls(mode='stress', duration_seconds=180, temp_limit_c=92, sample_interval_ms=250),
        }
        return presets.get(mode, cls(mode='standard'))
    
    @classmethod
    def custom(cls, duration: int, temp_limit: int, memory_limit: int = 0, power_limit: int = 0) -> 'BenchmarkConfig':
        return cls(
            mode='custom',
            duration_seconds=duration,
            temp_limit_c=temp_limit,
            memory_limit_mb=memory_limit,
            power_limit_w=power_limit,
            sample_interval_ms=500
        )


class BaselineStorage:
    """Storage for benchmark baseline results."""
    
    def __init__(self, db_path: str = './metrics.db'):
        self.db_path = Path(db_path)
        self._ensure_table()
    
    def _ensure_table(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute('''
            CREATE TABLE IF NOT EXISTS benchmark_baseline (
                id INTEGER PRIMARY KEY,
                gpu_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                iterations_completed INTEGER,
                avg_iteration_time_ms REAL,
                avg_utilization REAL,
                avg_temperature REAL,
                avg_power REAL,
                avg_memory_used REAL,
                results_json TEXT,
                UNIQUE(gpu_name)
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_baseline(self, gpu_name: str, results: Dict[str, Any]):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute('''
            INSERT OR REPLACE INTO benchmark_baseline 
            (gpu_name, timestamp, iterations_completed, avg_iteration_time_ms, 
             avg_utilization, avg_temperature, avg_power, avg_memory_used, results_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            gpu_name,
            results.get('timestamp', datetime.now().isoformat()),
            results.get('iterations_completed', 0),
            results.get('avg_iteration_time_ms', 0),
            results.get('utilization', {}).get('avg', 0),
            results.get('temperature_c', {}).get('avg', 0),
            results.get('power_w', {}).get('avg', 0),
            results.get('memory_used_mb', {}).get('avg', 0),
            json.dumps(results)
        ))
        conn.commit()
        conn.close()
    
    def get_baseline(self, gpu_name: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            'SELECT * FROM benchmark_baseline WHERE gpu_name = ?', (gpu_name,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'gpu_name': row['gpu_name'],
                'timestamp': row['timestamp'],
                'iterations_completed': row['iterations_completed'],
                'avg_iteration_time_ms': row['avg_iteration_time_ms'],
                'avg_utilization': row['avg_utilization'],
                'avg_temperature': row['avg_temperature'],
                'avg_power': row['avg_power'],
                'avg_memory_used': row['avg_memory_used'],
                'full_results': json.loads(row['results_json']) if row['results_json'] else None
            }
        return None


class GPUStressWorker:
    """
    GPU stress workload - auto-detects best available method.
    Priority: cupy > torch > passive monitoring (user runs own workload).
    Each iteration = 1 complete stress cycle.
    """
    
    def __init__(self):
        self.iterations = 0
        self.running = False
        self.workload_type = "Detecting..."
        self.method = None
        self._detect_method()
    
    def _detect_method(self):
        """Detect best available stress method without requiring extra installs."""
        # Try cupy first
        try:
            import cupy as cp
            cp.cuda.Device(0).compute_capability
            self.method = 'cupy'
            self.workload_type = "CUDA Matrix Multiply (cupy)"
            return
        except:
            pass
        
        # Try torch
        try:
            import torch
            if torch.cuda.is_available():
                self.method = 'torch'
                self.workload_type = "CUDA Matrix Multiply (torch)"
                return
        except:
            pass
        
        # Fallback: passive monitoring mode
        self.method = 'passive'
        self.workload_type = "Passive Monitoring (run your own GPU workload)"
    
    def run_iteration(self) -> float:
        """Run one iteration. Returns time in ms."""
        start = time.perf_counter()
        
        if self.method == 'cupy':
            try:
                import cupy as cp
                size = 2048
                a = cp.random.rand(size, size).astype(cp.float32)
                b = cp.random.rand(size, size).astype(cp.float32)
                c = cp.matmul(a, b)
                cp.cuda.Stream.null.synchronize()
                del a, b, c
            except Exception:
                pass
        elif self.method == 'torch':
            try:
                import torch
                device = torch.device('cuda')
                size = 2048
                a = torch.rand(size, size, device=device)
                b = torch.rand(size, size, device=device)
                c = torch.matmul(a, b)
                torch.cuda.synchronize()
                del a, b, c
            except Exception:
                pass
        else:
            # Passive mode - just poll nvidia-smi to track iterations
            try:
                subprocess.run(
                    ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader'],
                    capture_output=True, timeout=2
                )
            except Exception:
                pass
            time.sleep(0.05)  # Small delay in passive mode
        
        self.iterations += 1
        return (time.perf_counter() - start) * 1000
    
    def reset(self):
        self.iterations = 0


class GPUBenchmark:
    """GPU Benchmark with real-time monitoring and stress workload."""
    
    def __init__(self, db_path: str = './metrics.db'):
        self.running = False
        self.should_stop = False
        self.config: Optional[BenchmarkConfig] = None
        self.samples: List[Dict[str, Any]] = []
        self.stop_reason: Optional[str] = None
        self.start_time: Optional[float] = None
        self.progress = 0
        self.current_phase = ""
        self.results: Dict[str, Any] = {}
        self.baseline_storage = BaselineStorage(db_path)
        self.stress_worker = GPUStressWorker()
        self.iteration_times: List[float] = []
        self.completed_full = False
        
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information."""
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
        """Collect a single sample of GPU metrics."""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode != 0:
                return {'error': 'nvidia-smi failed'}
            
            parts = [p.strip() for p in result.stdout.strip().split(',')]
            
            return {
                'timestamp': time.time(),
                'utilization': float(parts[0]) if parts[0] != '[N/A]' else 0,
                'memory_used_mb': float(parts[1]) if parts[1] != '[N/A]' else 0,
                'memory_total_mb': float(parts[2]) if parts[2] != '[N/A]' else 0,
                'temperature_c': float(parts[3]) if parts[3] != '[N/A]' else 0,
                'power_w': float(parts[4]) if parts[4] != '[N/A]' else 0,
            }
        except Exception as e:
            return {'error': str(e), 'timestamp': time.time()}
    
    def check_stop_conditions(self, sample: Dict[str, Any]) -> Optional[str]:
        """Check if any stop condition is met."""
        if self.should_stop:
            return "User stopped"
        
        if 'error' in sample:
            return f"GPU error: {sample['error']}"
        
        if self.config.temp_limit_c > 0 and sample.get('temperature_c', 0) >= self.config.temp_limit_c:
            return f"Temperature limit reached ({sample['temperature_c']}C >= {self.config.temp_limit_c}C)"
        
        if self.config.power_limit_w > 0 and sample.get('power_w', 0) >= self.config.power_limit_w:
            return f"Power limit reached ({sample['power_w']}W >= {self.config.power_limit_w}W)"
        
        if self.config.memory_limit_mb > 0 and sample.get('memory_used_mb', 0) >= self.config.memory_limit_mb:
            return f"Memory limit reached ({sample['memory_used_mb']}MB >= {self.config.memory_limit_mb}MB)"
        
        return None
    
    def run_stress_benchmark(self) -> Dict[str, Any]:
        """Run the stress benchmark with real GPU workload."""
        self.current_phase = "Running GPU Stress Test"
        self.samples = []
        self.iteration_times = []
        self.stress_worker.reset()
        self.start_time = time.time()
        self.completed_full = False
        
        sample_interval = self.config.sample_interval_ms / 1000.0
        last_sample_time = 0
        
        while True:
            elapsed = time.time() - self.start_time
            
            # Check duration
            if elapsed >= self.config.duration_seconds:
                self.stop_reason = "Duration completed"
                self.completed_full = True
                break
            
            # Run one iteration of stress work
            iter_time = self.stress_worker.run_iteration()
            self.iteration_times.append(iter_time)
            
            # Sample metrics periodically
            if elapsed - last_sample_time >= sample_interval:
                sample = self.sample_metrics()
                sample['elapsed_sec'] = round(elapsed, 2)
                sample['iterations'] = self.stress_worker.iterations
                sample['last_iter_ms'] = round(iter_time, 2)
                self.samples.append(sample)
                last_sample_time = elapsed
                
                # Check stop conditions
                stop = self.check_stop_conditions(sample)
                if stop:
                    self.stop_reason = stop
                    break
            
            # Update progress
            self.progress = int((elapsed / self.config.duration_seconds) * 100)
        
        return self._calculate_results()
    
    def _calculate_results(self) -> Dict[str, Any]:
        """Calculate benchmark results from samples."""
        if not self.samples:
            return {'error': 'No samples collected'}
        
        valid_samples = [s for s in self.samples if 'error' not in s]
        
        if not valid_samples:
            return {'error': 'All samples had errors'}
        
        def calc_stats(key: str) -> Dict[str, float]:
            values = [s.get(key, 0) for s in valid_samples]
            return {
                'min': round(min(values), 2),
                'max': round(max(values), 2),
                'avg': round(sum(values) / len(values), 2),
            }
        
        avg_iter_time = sum(self.iteration_times) / len(self.iteration_times) if self.iteration_times else 0
        
        results = {
            'duration_actual_sec': round(time.time() - self.start_time, 2),
            'samples_collected': len(valid_samples),
            'stop_reason': self.stop_reason,
            'completed_full': self.completed_full,
            'workload_type': self.stress_worker.workload_type,
            'iterations_completed': self.stress_worker.iterations,
            'avg_iteration_time_ms': round(avg_iter_time, 2),
            'iterations_per_second': round(1000 / avg_iter_time, 2) if avg_iter_time > 0 else 0,
            'utilization': calc_stats('utilization'),
            'memory_used_mb': calc_stats('memory_used_mb'),
            'temperature_c': calc_stats('temperature_c'),
            'power_w': calc_stats('power_w'),
        }
        
        # Calculate scores based on performance
        temp_range = results['temperature_c']['max'] - results['temperature_c']['min']
        stability_score = max(0, 100 - int(temp_range * 5))
        thermal_score = max(0, min(100, int((90 - results['temperature_c']['max']) * 5)))
        
        # Performance score based on iterations
        perf_score = min(100, int(results['iterations_completed'] / 10))
        
        results['scores'] = {
            'stability': stability_score,
            'thermal': thermal_score,
            'performance': perf_score,
            'overall': (stability_score + thermal_score + perf_score) // 3
        }
        
        return results
    
    def start(self, config: BenchmarkConfig) -> None:
        """Start benchmark with given configuration."""
        self.config = config
        self.running = True
        self.should_stop = False
        self.stop_reason = None
        self.progress = 0
        self.samples = []
        self.completed_full = False
        
        try:
            gpu_info = self.get_gpu_info()
            
            self.results = {
                'timestamp': datetime.now().isoformat(),
                'config': {
                    'mode': config.mode,
                    'duration_seconds': config.duration_seconds,
                    'temp_limit_c': config.temp_limit_c,
                    'power_limit_w': config.power_limit_w,
                    'memory_limit_mb': config.memory_limit_mb,
                },
                'gpu_info': gpu_info,
                'status': 'running',
            }
            
            # Get baseline for comparison
            if 'name' in gpu_info:
                baseline = self.baseline_storage.get_baseline(gpu_info['name'])
                if baseline:
                    self.results['baseline'] = baseline
            
            results = self.run_stress_benchmark()
            self.results.update(results)
            self.results['status'] = 'completed'
            
            # Save as baseline only if completed fully
            if self.completed_full and 'name' in gpu_info:
                self.baseline_storage.save_baseline(gpu_info['name'], self.results)
                self.results['saved_as_baseline'] = True
            
        except Exception as e:
            self.results['status'] = 'failed'
            self.results['error'] = str(e)
        finally:
            self.running = False
            self.progress = 100
    
    def stop(self) -> None:
        """Stop the benchmark."""
        self.should_stop = True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current benchmark status."""
        return {
            'running': self.running,
            'progress': self.progress,
            'phase': self.current_phase,
            'samples_count': len(self.samples),
            'iterations': self.stress_worker.iterations if self.stress_worker else 0,
            'workload_type': self.stress_worker.workload_type if self.stress_worker else 'N/A',
            'latest_sample': self.samples[-1] if self.samples else None,
        }
    
    def get_samples(self) -> List[Dict[str, Any]]:
        """Get all collected samples for real-time graphing."""
        return self.samples.copy()
    
    def get_results(self) -> Dict[str, Any]:
        """Get benchmark results."""
        return self.results
    
    def get_baseline(self) -> Optional[Dict[str, Any]]:
        """Get stored baseline for current GPU."""
        gpu_info = self.get_gpu_info()
        if 'name' in gpu_info:
            return self.baseline_storage.get_baseline(gpu_info['name'])
        return None


# Global instance
_benchmark: Optional[GPUBenchmark] = None

def get_benchmark_instance() -> GPUBenchmark:
    global _benchmark
    if _benchmark is None:
        _benchmark = GPUBenchmark()
    return _benchmark
