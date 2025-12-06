"""GPU workload implementations for benchmarking - REFACTORED."""

import time
import subprocess
import math
from typing import Dict, Any, Optional

from .config import BenchmarkConfig
from . import gpu_setup
from . import physics_cupy
from . import physics_torch
from . import particle_utils


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
        self._counters = {}
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
            self.workload_type = f"Bounce Simulation ({n:,} particles, cupy)"
            
            # Use modular GPU setup
            self._gpu_arrays, self._counters = gpu_setup.setup_cupy_arrays(n, cp)
            
            # Initialize instance variables from counters
            self._initial_particle_count = n
            self._active_count = self._counters['active_count']
            self._small_ball_count = self._counters['small_ball_count']
            self._drop_timer = self._counters['drop_timer']
            self._gravity_strength = self._counters['gravity_strength']
            self._small_ball_speed = self._counters['small_ball_speed']
            self._initial_balls = self._counters['initial_balls']
            self._max_balls_cap = self._counters['max_balls_cap']
            self._split_enabled = self._counters['split_enabled']
            self._drop_rate = 1
    
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
            self.workload_type = f"Bounce Simulation ({n:,} particles, torch)"
            
            # Use modular GPU setup
            self._gpu_arrays, self._counters = gpu_setup.setup_torch_arrays(n, torch)
            
            # Initialize instance variables from counters
            self._initial_particle_count = n
            self._active_count = self._counters['active_count']
            self._small_ball_count = self._counters['small_ball_count']
            self._drop_timer = self._counters['drop_timer']
            self._gravity_strength = self._counters['gravity_strength']
            self._small_ball_speed = self._counters['small_ball_speed']
            self._initial_balls = self._counters['initial_balls']
            self._max_balls_cap = self._counters['max_balls_cap']
            self._split_enabled = self._counters['split_enabled']
            self._drop_rate = 1
    
    def run_iteration(self) -> float:
        """Run one iteration of the workload and return elapsed time."""
        if not self._initialized or self._method == 'passive':
            return 0.0
        
        start = time.perf_counter()
        
        if self.benchmark_type == "gemm":
            self._run_gemm()
        elif self.benchmark_type == "particle":
            self._run_particle()
        
        elapsed = time.perf_counter() - start
        self.iterations += 1
        return elapsed
    
    def _run_gemm(self):
        """Run GEMM workload."""
        if self._method == 'cupy':
            cp = self._cp
            A = self._gpu_arrays['A']
            B = self._gpu_arrays['B']
            C = cp.matmul(A, B)
            cp.cuda.Stream.null.synchronize()
            self.total_flops += self._flops_per_iter
            
        elif self._method == 'torch':
            torch = self._torch
            A = self._gpu_arrays['A']
            B = self._gpu_arrays['B']
            C = torch.matmul(A, B)
            torch.cuda.synchronize()
            self.total_flops += self._flops_per_iter
    
    def _run_particle(self):
        """Run particle simulation workload - delegates to modular physics engines."""
        # Build params dictionary
        params = {
            'dt': 0.016,
            'gravity_strength': self._gravity_strength,
            'small_ball_speed': self._small_ball_speed,
            'initial_balls': self._initial_balls,
            'max_balls_cap': self._max_balls_cap,
            'split_enabled': self._split_enabled,
            'active_count': self._active_count,
            'small_ball_count': self._small_ball_count,
            'drop_timer': self._drop_timer
        }
        
        if self._method == 'cupy':
            # Use modular CuPy physics engine
            result = physics_cupy.run_particle_physics_cupy(
                self._gpu_arrays,
                params,
                self._cp
            )
            
            # Update counters from result
            self._active_count = result['active_count']
            self._small_ball_count = result['small_ball_count']
            self._drop_timer = result['drop_timer']
            self._split_enabled = result['split_enabled']
            
            self._cp.cuda.Stream.null.synchronize()
            self.total_steps += 1
            
        elif self._method == 'torch':
            # Use modular PyTorch physics engine
            result = physics_torch.run_particle_physics_torch(
                self._gpu_arrays,
                params,
                self._torch
            )
            
            # Update counters from result
            self._active_count = result['active_count']
            self._small_ball_count = result['small_ball_count']
            self._drop_timer = result['drop_timer']
            self._split_enabled = result['split_enabled']
            
            self._torch.cuda.synchronize()
            self.total_steps += 1
    
    def update_physics_params(self, gravity_strength: Optional[float] = None, 
                             small_ball_speed: Optional[float] = None,
                             initial_balls: Optional[int] = None,
                             max_balls_cap: Optional[int] = None):
        """Update physics parameters from UI sliders."""
        if gravity_strength is not None:
            self._gravity_strength = gravity_strength
        if small_ball_speed is not None:
            self._small_ball_speed = small_ball_speed
        if initial_balls is not None:
            self._initial_balls = initial_balls
        if max_balls_cap is not None:
            self._max_balls_cap = max_balls_cap
    
    def set_split_enabled(self, enabled: bool):
        """Enable or disable particle splitting."""
        self._split_enabled = enabled
    
    def get_particle_sample(self, max_samples: int = 2000):
        """
        Get a sampled subset of ACTIVE particle positions, masses, colors, and glow for visualization.
        
        Args:
            max_samples: Maximum number of particles to return
            
        Returns:
            tuple of (positions, masses, colors, glows) or (None, None, None, None) if not available
        """
        if not self._initialized or self.benchmark_type != "particle":
            return None, None, None, None
        
        return particle_utils.get_particle_sample(
            self._gpu_arrays,
            self._method,
            max_samples
        )
    
    def get_influence_boundaries(self, gravity_strength: float = 500.0):
        """
        Get positions of large bodies with gravity radius based on actual force strength.
        
        Args:
            gravity_strength: Current gravity constant
            
        Returns:
            list of (x, y, radius) tuples for large bodies, or empty list
        """
        if not self._initialized or self.benchmark_type != "particle":
            return []
        
        return particle_utils.get_influence_boundaries(
            self._gpu_arrays,
            self._method,
            gravity_strength
        )
    
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
                (self.total_steps * self._active_count) / elapsed_seconds, 2
            )
        
        return stats


class PyTorchStressWorker:
    """PyTorch-specific stress workload (CPU fallback)."""
    
    def __init__(self):
        import torch
        self.torch = torch
        self.iterations = 0
        self.workload_type = "PyTorch CPU Stress"
        
        # Create large tensors for stress test
        self.tensor_a = torch.randn(2000, 2000)
        self.tensor_b = torch.randn(2000, 2000)
    
    def run_iteration(self) -> float:
        """Run one iteration."""
        start = time.perf_counter()
        result = torch.matmul(self.tensor_a, self.tensor_b)
        elapsed = time.perf_counter() - start
        self.iterations += 1
        return elapsed
    
    def reset(self):
        """Reset iteration counter."""
        self.iterations = 0
    
    def cleanup(self):
        """Free memory."""
        del self.tensor_a
        del self.tensor_b
    
    def get_performance_stats(self, elapsed_seconds: float) -> Dict[str, Any]:
        """Get performance stats."""
        return {
            'iterations': self.iterations,
            'workload_type': self.workload_type,
        }


class SystemStressWorker:
    """Generic system stress worker using external tools."""
    
    def __init__(self):
        self.iterations = 0
        self.workload_type = "System Stress (stress-ng)"
        self.process = None
    
    def run_iteration(self) -> float:
        """Run stress iteration."""
        if self.process is None:
            try:
                self.process = subprocess.Popen(
                    ['stress-ng', '--cpu', '4', '--timeout', '60s'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except FileNotFoundError:
                self.workload_type = "System Stress (unavailable)"
                return 0.0
        
        self.iterations += 1
        return 0.01  # Nominal time
    
    def reset(self):
        """Reset counter."""
        self.iterations = 0
    
    def cleanup(self):
        """Stop stress process."""
        if self.process:
            self.process.terminate()
            self.process = None
    
    def get_performance_stats(self, elapsed_seconds: float) -> Dict[str, Any]:
        """Get stats."""
        return {
            'iterations': self.iterations,
            'workload_type': self.workload_type,
        }
