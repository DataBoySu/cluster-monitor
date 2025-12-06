"""GPU Benchmark with GEMM and Particle Simulation stress tests.

Uses standard GPU libraries (cupy/torch) for stable, production-ready stress testing.
No JIT compilation - simple vectorized operations for maximum GPU load.
"""

import time
import subprocess
import json
import sqlite3
import threading
import math
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BenchmarkConfig:
    mode: str = "fixed"  # fixed, stress, or adaptive
    benchmark_type: str = "gemm"  # "gemm" or "particle"
    duration_seconds: int = 30
    memory_limit_mb: int = 0  # 0 = no limit
    temp_limit_c: int = 85
    power_limit_w: int = 0  # 0 = no limit
    sample_interval_ms: int = 500
    # GEMM-specific settings
    matrix_size: int = 2048  # Reduced for stability
    # Particle-specific settings
    num_particles: int = 100000  # 100k particles default
    # Auto-scaling settings
    auto_scale: bool = False  # Automatically scale workload to reach target utilization
    target_gpu_util: int = 98  # Target GPU utilization %
    
    @classmethod
    def from_mode(cls, mode: str, benchmark_type: str = "gemm") -> 'BenchmarkConfig':
        presets = {
            'quick': cls(mode='quick', benchmark_type=benchmark_type, duration_seconds=15, temp_limit_c=85, sample_interval_ms=500),
            'standard': cls(mode='standard', benchmark_type=benchmark_type, duration_seconds=60, temp_limit_c=85, sample_interval_ms=500),
            'stress': cls(mode='stress', benchmark_type=benchmark_type, duration_seconds=180, temp_limit_c=92, sample_interval_ms=250),
        }
        return presets.get(mode, cls(mode='standard', benchmark_type=benchmark_type))
    
    @classmethod
    def custom(cls, duration: int, temp_limit: int, memory_limit: int = 0, power_limit: int = 0, 
               benchmark_type: str = "gemm", matrix_size: int = 2048, 
               num_particles: int = 100000) -> 'BenchmarkConfig':
        return cls(
            mode='custom',
            benchmark_type=benchmark_type,
            duration_seconds=duration,
            temp_limit_c=temp_limit,
            memory_limit_mb=memory_limit,
            power_limit_w=power_limit,
            sample_interval_ms=500,
            matrix_size=matrix_size,
            num_particles=num_particles
        )


class BaselineStorage:
    """Storage for benchmark baseline results."""
    
    def __init__(self, db_path: str = './metrics.db'):
        self.db_path = Path(db_path)
        self._ensure_table()
    
    def _ensure_table(self):
        conn = sqlite3.connect(str(self.db_path))
        
        # Check if table exists and has old schema
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_baseline'"
        )
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # Check if benchmark_type column exists
            cursor = conn.execute("PRAGMA table_info(benchmark_baseline)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'benchmark_type' not in columns:
                # Migrate old table - drop and recreate
                conn.execute('DROP TABLE IF EXISTS benchmark_baseline')
        
        # Create table with new schema
        conn.execute('''
            CREATE TABLE IF NOT EXISTS benchmark_baseline (
                gpu_name TEXT NOT NULL,
                benchmark_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                iterations_completed INTEGER,
                avg_iteration_time_ms REAL,
                avg_utilization REAL,
                avg_temperature REAL,
                avg_power REAL,
                avg_memory_used REAL,
                results_json TEXT,
                PRIMARY KEY (gpu_name, benchmark_type)
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_baseline(self, gpu_name: str, benchmark_type: str, results: Dict[str, Any]):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute('''
            INSERT OR REPLACE INTO benchmark_baseline 
            (gpu_name, benchmark_type, timestamp, iterations_completed, avg_iteration_time_ms, 
             avg_utilization, avg_temperature, avg_power, avg_memory_used, results_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            gpu_name,
            benchmark_type,
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
    
    def get_baseline(self, gpu_name: str, benchmark_type: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            'SELECT * FROM benchmark_baseline WHERE gpu_name = ? AND benchmark_type = ?', 
            (gpu_name, benchmark_type)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'gpu_name': row['gpu_name'],
                'benchmark_type': row['benchmark_type'],
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
    """GPU stress workload - uses standard GPU libraries (cupy/torch)."""
    
    def __init__(self, benchmark_type: str = "gemm", config: Optional[BenchmarkConfig] = None):
        self.iterations = 0
        self.benchmark_type = benchmark_type
        self.config = config or BenchmarkConfig()
        self.workload_type = "Detecting..."
        self._method = None  # 'cupy', 'torch', or 'passive'
        self._initialized = False
        
        # Performance tracking
        self.total_flops = 0.0
        self.total_steps = 0
        
        # GPU state
        self._gpu_arrays = {}
        
        self._detect_and_setup()
    
    def _detect_and_setup(self):
        """Detect available GPU libraries and setup workload."""
        # Try cupy first
        try:
            import cupy as cp
            self._method = 'cupy'
            self._cp = cp
            self._setup_cupy()
            self._initialized = True
            return
        except ImportError:
            pass
        except Exception as e:
            print(f"cupy failed: {e}")
        
        # Try torch
        try:
            import torch
            if torch.cuda.is_available():
                self._method = 'torch'
                self._torch = torch
                self._setup_torch()
                self._initialized = True
                return
        except ImportError:
            pass
        except Exception as e:
            print(f"torch failed: {e}")
        
        # Fallback: passive monitoring
        self._method = 'passive'
        self.workload_type = "Passive Monitoring (cupy/torch not available - run your own GPU workload)"
    
    def _setup_cupy(self):
        """Setup workload using cupy."""
        cp = self._cp
        n = self.config.matrix_size if self.benchmark_type == "gemm" else self.config.num_particles
        
        if self.benchmark_type == "gemm":
            self.workload_type = f"GEMM {n}x{n} (cupy)"
            self._gpu_arrays['A'] = cp.random.rand(n, n, dtype=cp.float32)
            self._gpu_arrays['B'] = cp.random.rand(n, n, dtype=cp.float32)
            self._flops_per_iter = 2.0 * (n ** 3)
        else:
            self.workload_type = f"Particle Sim ({n:,} particles, cupy)"
            self._gpu_arrays['x'] = cp.random.rand(n, dtype=cp.float32) * 1000.0
            self._gpu_arrays['y'] = cp.random.rand(n, dtype=cp.float32) * 1000.0
            self._gpu_arrays['vx'] = (cp.random.rand(n, dtype=cp.float32) - 0.5) * 10.0
            self._gpu_arrays['vy'] = (cp.random.rand(n, dtype=cp.float32) - 0.5) * 10.0
    
    def _setup_torch(self):
        """Setup workload using torch."""
        torch = self._torch
        device = torch.device('cuda')
        n = self.config.matrix_size if self.benchmark_type == "gemm" else self.config.num_particles
        
        if self.benchmark_type == "gemm":
            self.workload_type = f"GEMM {n}x{n} (torch)"
            self._gpu_arrays['A'] = torch.randn(n, n, device=device, dtype=torch.float32)
            self._gpu_arrays['B'] = torch.randn(n, n, device=device, dtype=torch.float32)
            self._flops_per_iter = 2.0 * (n ** 3)
        else:
            self.workload_type = f"Particle Sim ({n:,} particles, torch)"
            self._gpu_arrays['x'] = torch.rand(n, device=device, dtype=torch.float32) * 1000.0
            self._gpu_arrays['y'] = torch.rand(n, device=device, dtype=torch.float32) * 1000.0
            self._gpu_arrays['vx'] = (torch.rand(n, device=device, dtype=torch.float32) - 0.5) * 10.0
            self._gpu_arrays['vy'] = (torch.rand(n, device=device, dtype=torch.float32) - 0.5) * 10.0
    
    def run_iteration(self) -> float:
        """Run one iteration. Returns time in ms."""
        start = time.perf_counter()
        
        if not self._initialized or self._method == 'passive':
            # Passive mode - just sleep and count iterations
            try:
                subprocess.run(
                    ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader'],
                    capture_output=True, timeout=2
                )
            except Exception:
                pass
            time.sleep(0.05)
            self.iterations += 1
            return (time.perf_counter() - start) * 1000
        
        # Run GPU workload
        if self.benchmark_type == "gemm":
            self._run_gemm()
        elif self.benchmark_type == "particle":
            self._run_particle()
        
        self.iterations += 1
        return (time.perf_counter() - start) * 1000
    
    def _run_gemm(self):
        """Run GEMM (matrix multiply) workload."""
        if self._method == 'cupy':
            A = self._gpu_arrays['A']
            B = self._gpu_arrays['B']
            C = self._cp.matmul(A, B)
            self._cp.cuda.Stream.null.synchronize()
            self.total_flops += self._flops_per_iter
        elif self._method == 'torch':
            A = self._gpu_arrays['A']
            B = self._gpu_arrays['B']
            C = self._torch.matmul(A, B)
            self._torch.cuda.synchronize()
            self.total_flops += self._flops_per_iter
    
    def _run_particle(self):
        """Run particle simulation workload."""
        if self._method == 'cupy':
            cp = self._cp
            x = self._gpu_arrays['x']
            y = self._gpu_arrays['y']
            vx = self._gpu_arrays['vx']
            vy = self._gpu_arrays['vy']
            dt = 0.001
            
            # Simple particle update: gravity, velocity, position, wall bounce
            vy = vy + 9.81 * dt
            x = x + vx * dt
            y = y + vy * dt
            
            # Wall bouncing
            mask_x_min = x < 0
            mask_x_max = x > 1000.0
            mask_y_min = y < 0
            mask_y_max = y > 1000.0
            
            x[mask_x_min] = 0
            x[mask_x_max] = 1000.0
            vx[mask_x_min | mask_x_max] *= -0.8
            
            y[mask_y_min] = 0
            y[mask_y_max] = 1000.0
            vy[mask_y_min | mask_y_max] *= -0.8
            
            # Update arrays
            self._gpu_arrays['x'] = x
            self._gpu_arrays['y'] = y
            self._gpu_arrays['vx'] = vx
            self._gpu_arrays['vy'] = vy
            
            cp.cuda.Stream.null.synchronize()
            self.total_steps += 1
            
        elif self._method == 'torch':
            torch = self._torch
            x = self._gpu_arrays['x']
            y = self._gpu_arrays['y']
            vx = self._gpu_arrays['vx']
            vy = self._gpu_arrays['vy']
            dt = 0.001
            
            # Simple particle update
            vy = vy + 9.81 * dt
            x = x + vx * dt
            y = y + vy * dt
            
            # Wall bouncing
            x = torch.clamp(x, 0, 1000.0)
            y = torch.clamp(y, 0, 1000.0)
            
            vx[x <= 0] *= -0.8
            vx[x >= 1000.0] *= -0.8
            vy[y <= 0] *= -0.8
            vy[y >= 1000.0] *= -0.8
            
            # Update arrays
            self._gpu_arrays['x'] = x
            self._gpu_arrays['y'] = y
            self._gpu_arrays['vx'] = vx
            self._gpu_arrays['vy'] = vy
            
            torch.cuda.synchronize()
            self.total_steps += 1
    
    def reset(self):
        """Reset counters."""
        self.iterations = 0
        self.total_flops = 0.0
        self.total_steps = 0
    
    def cleanup(self):
        """Free GPU memory."""
        if self._method == 'cupy':
            for key in list(self._gpu_arrays.keys()):
                self._gpu_arrays[key] = None
        elif self._method == 'torch':
            for key in list(self._gpu_arrays.keys()):
                if self._gpu_arrays[key] is not None:
                    del self._gpu_arrays[key]
        self._gpu_arrays.clear()
    
    def scale_workload(self, scale_factor: float = 1.5):
        """Scale workload size up (for auto-scaling stress test)."""
        if not self._initialized or self._method == 'passive':
            return
        
        if self.benchmark_type == "gemm":
            # Increase matrix size
            old_size = self.config.matrix_size
            new_size = int(old_size * math.sqrt(scale_factor))
            self.config.matrix_size = new_size
            
            # Recreate arrays
            if self._method == 'cupy':
                cp = self._cp
                self._gpu_arrays['A'] = cp.random.rand(new_size, new_size, dtype=cp.float32)
                self._gpu_arrays['B'] = cp.random.rand(new_size, new_size, dtype=cp.float32)
                self._flops_per_iter = 2.0 * (new_size ** 3)
            elif self._method == 'torch':
                torch = self._torch
                device = torch.device('cuda')
                self._gpu_arrays['A'] = torch.randn(new_size, new_size, device=device, dtype=torch.float32)
                self._gpu_arrays['B'] = torch.randn(new_size, new_size, device=device, dtype=torch.float32)
                self._flops_per_iter = 2.0 * (new_size ** 3)
            
            self.workload_type = f"GEMM {new_size}x{new_size} ({self._method})"
            
        elif self.benchmark_type == "particle":
            # Increase particle count
            old_count = self.config.num_particles
            new_count = int(old_count * scale_factor)
            self.config.num_particles = new_count
            
            # Recreate arrays
            if self._method == 'cupy':
                cp = self._cp
                self._gpu_arrays['x'] = cp.random.rand(new_count, dtype=cp.float32) * 1000.0
                self._gpu_arrays['y'] = cp.random.rand(new_count, dtype=cp.float32) * 1000.0
                self._gpu_arrays['vx'] = (cp.random.rand(new_count, dtype=cp.float32) - 0.5) * 10.0
                self._gpu_arrays['vy'] = (cp.random.rand(new_count, dtype=cp.float32) - 0.5) * 10.0
            elif self._method == 'torch':
                torch = self._torch
                device = torch.device('cuda')
                self._gpu_arrays['x'] = torch.rand(new_count, device=device, dtype=torch.float32) * 1000.0
                self._gpu_arrays['y'] = torch.rand(new_count, device=device, dtype=torch.float32) * 1000.0
                self._gpu_arrays['vx'] = (torch.rand(new_count, device=device, dtype=torch.float32) - 0.5) * 10.0
                self._gpu_arrays['vy'] = (torch.rand(new_count, device=device, dtype=torch.float32) - 0.5) * 10.0
            
            self.workload_type = f"Particle Sim ({new_count:,} particles, {self._method})"
    
    def get_performance_stats(self, elapsed_seconds: float) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {
            'iterations': self.iterations,
            'workload_type': self.workload_type,
        }
        
        if self.benchmark_type == "gemm" and elapsed_seconds > 0:
            tflops = (self.total_flops / elapsed_seconds) / 1e12
            stats['total_flops'] = self.total_flops
            stats['tflops'] = round(tflops, 3)
            stats['gflops'] = round(tflops * 1000, 2)
        elif self.benchmark_type == "particle" and elapsed_seconds > 0:
            stats['total_steps'] = self.total_steps
            stats['steps_per_second'] = round(self.total_steps / elapsed_seconds, 2)
            stats['particles_updated_per_second'] = round(
                (self.total_steps * self.config.num_particles) / elapsed_seconds, 0
            )
        
        return stats


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
        self.stress_worker: Optional[GPUStressWorker] = None
        self.iteration_times: List[float] = []
        self.completed_full = False
        self.db_path = db_path
        
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
        last_scale_check = 0
        scale_interval = 2.0  # Check for scaling every 2 seconds
        scale_count = 0
        max_scales = 5  # Limit scaling attempts
        
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
                
                # Auto-scaling logic: check if we need to increase workload
                if self.config.auto_scale and elapsed - last_scale_check >= scale_interval:
                    gpu_util = sample.get('utilization', 0)
                    if gpu_util < 93 and scale_count < max_scales:
                        print(f"[Auto-Scale] GPU util {gpu_util}% < target, scaling up workload...")
                        self.stress_worker.scale_workload(1.5)
                        scale_count += 1
                        # Update workload type in current phase
                        self.current_phase = f"Auto-Scaling: {self.stress_worker.workload_type}"
                    last_scale_check = elapsed
                
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
        elapsed_sec = time.time() - self.start_time
        
        results = {
            'duration_actual_sec': round(elapsed_sec, 2),
            'samples_collected': len(valid_samples),
            'stop_reason': self.stop_reason,
            'completed_full': self.completed_full,
            'workload_type': self.stress_worker.workload_type,
            'benchmark_type': self.config.benchmark_type,
            'iterations_completed': self.stress_worker.iterations,
            'avg_iteration_time_ms': round(avg_iter_time, 2),
            'iterations_per_second': round(1000 / avg_iter_time, 2) if avg_iter_time > 0 else 0,
            'utilization': calc_stats('utilization'),
            'memory_used_mb': calc_stats('memory_used_mb'),
            'temperature_c': calc_stats('temperature_c'),
            'power_w': calc_stats('power_w'),
        }
        
        # Add performance stats from stress worker
        perf_stats = self.stress_worker.get_performance_stats(elapsed_sec)
        results['performance'] = perf_stats
        
        # Calculate scores based on performance
        temp_range = results['temperature_c']['max'] - results['temperature_c']['min']
        stability_score = max(0, 100 - int(temp_range * 5))
        thermal_score = max(0, min(100, int((90 - results['temperature_c']['max']) * 5)))
        
        # Performance score based on benchmark type
        if self.config.benchmark_type == 'gemm':
            # Score based on TFLOPS (scale: 1 TFLOPS = 10 points, max 100)
            tflops = perf_stats.get('tflops', 0)
            perf_score = min(100, int(tflops * 10))
        elif self.config.benchmark_type == 'particle':
            # Score based on steps per second (scale: 1M steps/sec = 10 points)
            sps = perf_stats.get('steps_per_second', 0)
            perf_score = min(100, int(sps / 100000))
        else:
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
        
        # Initialize stress worker with benchmark type from config
        self.stress_worker = GPUStressWorker(
            benchmark_type=config.benchmark_type,
            config=config
        )
        
        try:
            gpu_info = self.get_gpu_info()
            
            self.results = {
                'timestamp': datetime.now().isoformat(),
                'config': {
                    'mode': config.mode,
                    'benchmark_type': config.benchmark_type,
                    'duration_seconds': config.duration_seconds,
                    'temp_limit_c': config.temp_limit_c,
                    'power_limit_w': config.power_limit_w,
                    'memory_limit_mb': config.memory_limit_mb,
                    'matrix_size': config.matrix_size if config.benchmark_type == 'gemm' else None,
                    'num_particles': config.num_particles if config.benchmark_type == 'particle' else None,
                },
                'gpu_info': gpu_info,
                'status': 'running',
            }
            
            # Get baseline for comparison (benchmark-type specific)
            if 'name' in gpu_info:
                baseline = self.baseline_storage.get_baseline(gpu_info['name'], config.benchmark_type)
                if baseline:
                    self.results['baseline'] = baseline
            
            results = self.run_stress_benchmark()
            self.results.update(results)
            self.results['status'] = 'completed'
            
            # Save as baseline only if completed fully
            if self.completed_full and 'name' in gpu_info:
                self.baseline_storage.save_baseline(gpu_info['name'], config.benchmark_type, self.results)
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
    
    def get_baseline(self, benchmark_type: str = "gemm") -> Optional[Dict[str, Any]]:
        """Get stored baseline for current GPU and benchmark type."""
        gpu_info = self.get_gpu_info()
        if 'name' in gpu_info:
            return self.baseline_storage.get_baseline(gpu_info['name'], benchmark_type)
        return None


# Global instance
_benchmark: Optional[GPUBenchmark] = None

def get_benchmark_instance() -> GPUBenchmark:
    global _benchmark
    if _benchmark is None:
        _benchmark = GPUBenchmark()
    return _benchmark
