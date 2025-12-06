"""GPU workload implementations for benchmarking."""

import time
import subprocess
import math
from typing import Dict, Any, Optional

from .config import BenchmarkConfig


class GPUStressWorker:
    """GPU stress workload using cupy or torch libraries."""
    
    def __init__(self, benchmark_type: str = "gemm", config: Optional[BenchmarkConfig] = None):
        self.iterations = 0
        self.benchmark_type = benchmark_type
        self.config = config or BenchmarkConfig()
        self.workload_type = "Detecting..."
        self._method = None
        self._initialized = False
        self.total_flops = 0.0
        self.total_steps = 0
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
        except Exception:
            pass
        
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
        except Exception:
            pass
        
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
            
            vy = vy + 9.81 * dt
            x = x + vx * dt
            y = y + vy * dt
            
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
            
            vy = vy + 9.81 * dt
            x = x + vx * dt
            y = y + vy * dt
            
            x = torch.clamp(x, 0, 1000.0)
            y = torch.clamp(y, 0, 1000.0)
            
            vx[x <= 0] *= -0.8
            vx[x >= 1000.0] *= -0.8
            vy[y <= 0] *= -0.8
            vy[y >= 1000.0] *= -0.8
            
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
        """Scale workload size for auto-scaling stress test."""
        if not self._initialized or self._method == 'passive':
            return
        
        if self.benchmark_type == "gemm":
            old_size = self.config.matrix_size
            new_size = int(old_size * math.sqrt(scale_factor))
            self.config.matrix_size = new_size
            
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
            old_count = self.config.num_particles
            new_count = int(old_count * scale_factor)
            self.config.num_particles = new_count
            
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
