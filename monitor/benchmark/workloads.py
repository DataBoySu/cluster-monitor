import time
import subprocess
import math
from typing import Dict, Any, Optional

from .config import BenchmarkConfig
from . import gpu_setup
from . import physics_cupy
from . import physics_torch
from . import particle_utils
from .backend_stress import BackendStressManager


class GPUStressWorker:
    """GPU stress workload using cupy or torch libraries."""
    
    def __init__(self, benchmark_type: str = "gemm", config: Optional[BenchmarkConfig] = None, visualize: bool = False):
        self.iterations = 0
        self.benchmark_type = benchmark_type
        self.config = config or BenchmarkConfig()
        self.visualize = visualize
        self.workload_type = "Detecting..."
        self._method = None
        self._initialized = False
        self.total_flops = 0.0
        self.total_steps = 0
        self._gpu_arrays = {}
        self._counters = {}
        self._backend_stress = BackendStressManager()  # Use dedicated backend manager
        # Track per-iteration TFLOPS for GEMM to report avg/peak
        self._tflops_history = []
        # Estimated FLOPs per particle update (used to approximate TFLOPS in particle simulation mode)
        self._flops_per_particle_step = getattr(self.config, 'particle_flops_per_step', 50)
        self._detect_and_setup()
    
    def _detect_and_setup(self):
        """Detect available GPU libraries and setup workload."""
        # Honor preferred backend if provided in config
        preferred = getattr(self.config, 'preferred_backend', 'auto')

        def try_cupy():
            try:
                import cupy as cp
                self._method = 'cupy'
                self._cp = cp
                self._setup_cupy()
                self._initialized = True
                return True
            except Exception as e:
                print(f"[DEBUG] CuPy setup failed: {e}")
                return False

        def try_torch():
            try:
                import torch
                if torch.cuda.is_available():
                    self._method = 'torch'
                    self._torch = torch
                    self._setup_torch()
                    self._initialized = True
                    return True
            except Exception as e:
                print(f"[DEBUG] PyTorch setup failed: {e}")
            return False

        # If user requested a specific backend, try it first
        if preferred == 'cupy':
            if try_cupy():
                return
            if try_torch():
                return
        elif preferred == 'torch':
            if try_torch():
                return
            if try_cupy():
                return
        elif preferred == 'cpu':
            self._method = 'passive'
            self.workload_type = "Passive CPU mode selected"
            return

        # Default auto-detect: try cupy, then torch
        if try_cupy():
            return
        if try_torch():
            return

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
            backend_mult = self.config.backend_multiplier
            
            self._gpu_arrays, self._counters = gpu_setup.setup_cupy_arrays(n, cp)
            
            # Initialize backend stress manager only if backend_multiplier > 1
            if backend_mult > 1:
                self._backend_stress.initialize('cupy', cp, n, backend_mult)
                total_backend = n * backend_mult
                if self.visualize:
                    self.workload_type = f"Bounce Simulation ({n:,} visible, {total_backend:,} backend, cupy)"
                else:
                    self.workload_type = f"Bounce Simulation ({total_backend:,} particles, cupy)"
            else:
                # No backend stress - just show visible particles
                if self.visualize:
                    self.workload_type = f"Bounce Simulation ({n:,} particles, cupy)"
                else:
                    self.workload_type = f"Bounce Simulation ({n:,} particles, cupy)"
            
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
            backend_mult = self.config.backend_multiplier
            
            self._gpu_arrays, self._counters = gpu_setup.setup_torch_arrays(n, torch)
            
            # Initialize backend stress manager only if backend_multiplier > 1
            if backend_mult > 1:
                self._backend_stress.initialize('torch', torch, n, backend_mult)
                total_backend = n * backend_mult
                if self.visualize:
                    self.workload_type = f"Bounce Simulation ({n:,} visible, {total_backend:,} backend, torch)"
                else:
                    self.workload_type = f"Bounce Simulation ({total_backend:,} particles, torch)"
            else:
                # No backend stress - just show visible particles
                if self.visualize:
                    self.workload_type = f"Bounce Simulation ({n:,} particles, torch)"
                else:
                    self.workload_type = f"Bounce Simulation ({n:,} particles, torch)"
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
        # Record per-iteration TFLOPS for GEMM workloads (if elapsed > 0)
        if self.benchmark_type == 'gemm' and elapsed > 0 and getattr(self, '_flops_per_iter', 0) > 0:
            tflops_iter = (self._flops_per_iter / elapsed) / 1e12
            self._tflops_history.append(tflops_iter)
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
            # Use modular CuPy physics engine on main (visual) arrays
            result = physics_cupy.run_particle_physics_cupy(
                self._gpu_arrays,
                params,
                self._cp
            )
            
            self._active_count = result['active_count']
            self._small_ball_count = result['small_ball_count']
            self._drop_timer = result['drop_timer']
            self._split_enabled = result['split_enabled']
            
            # Run physics on backend (offscreen) arrays using backend stress manager
            if self._backend_stress.is_initialized():
                self._backend_stress.run_physics(physics_cupy, params, self._cp)
            
            self._cp.cuda.Stream.null.synchronize()
            try:
                particles = int(self._active_count)
            except Exception:
                particles = 0
            self.total_flops += (particles * float(self._flops_per_particle_step))
            self.total_steps += 1
            
        elif self._method == 'torch':
            # Use modular PyTorch physics engine on main (visual) arrays
            result = physics_torch.run_particle_physics_torch(
                self._gpu_arrays,
                params,
                self._torch
            )
            
            self._active_count = result['active_count']
            self._small_ball_count = result['small_ball_count']
            self._drop_timer = result['drop_timer']
            self._split_enabled = result['split_enabled']
            
            # Run physics on backend (offscreen) arrays using backend stress manager
            if self._backend_stress.is_initialized():
                self._backend_stress.run_physics(physics_torch, params, self._torch)
            
            self._torch.cuda.synchronize()
            try:
                particles = int(self._active_count)
            except Exception:
                particles = 0
            self.total_flops += (particles * float(self._flops_per_particle_step))
            self.total_steps += 1
    
    def update_physics_params(self, gravity_strength: Optional[float] = None, 
                             small_ball_speed: Optional[float] = None,
                             initial_balls: Optional[int] = None,
                             max_balls_cap: Optional[int] = None,
                             big_ball_count: Optional[int] = None,
                             backend_multiplier: Optional[int] = None):
        """Update physics parameters from UI sliders."""
        if gravity_strength is not None:
            self._gravity_strength = gravity_strength
        if small_ball_speed is not None:
            self._small_ball_speed = small_ball_speed
        if initial_balls is not None:
            self._initial_balls = initial_balls
        if max_balls_cap is not None:
            self._max_balls_cap = max_balls_cap
        if big_ball_count is not None:
            self._update_big_ball_count(big_ball_count)
        if backend_multiplier is not None and hasattr(self, '_initial_particle_count'):
            # Use backend stress manager to update multiplier (only for particle mode with backend stress)
            if self._backend_stress.is_initialized():
                self._backend_stress.update_multiplier(backend_multiplier, self._initial_particle_count)
    
    def update_split_enabled(self, enabled: bool):
        """Enable or disable particle splitting."""
        self._split_enabled = enabled
    
    def spawn_big_balls(self, x: float, y: float, count: int):
        """Spawn big ball(s) at specified position."""
        if not self._initialized or self.benchmark_type != "particle":
            return
        
        self._active_count = particle_utils.spawn_big_balls(
            self._gpu_arrays,
            self._method,
            x, y, count,
            self._active_count
        )
    
    def _update_big_ball_count(self, target_count: int):
        """Dynamically adjust the number of big balls."""
        if not self._initialized or self.benchmark_type != "particle":
            return
        
        self._active_count = particle_utils.update_big_ball_count(
            self._gpu_arrays,
            self._method,
            target_count,
            self._active_count
        )
    
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
        self._tflops_history = []  # clear recorded per-iteration TFLOPS
    
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
            elif self._method == 'torch':
                torch = self._torch
                device = torch.device('cuda')
                self._gpu_arrays['A'] = torch.randn(new_size, new_size, device=device, dtype=torch.float32)
                self._gpu_arrays['B'] = torch.randn(new_size, new_size, device=device, dtype=torch.float32)
            
            self._flops_per_iter = 2.0 * (new_size ** 3)
            self.workload_type = f"GEMM {new_size}x{new_size} ({self._method})"
        else:
            # For particle simulation, scale the backend stress if it's enabled
            if self._backend_stress.is_initialized():
                current_backend_count = self._backend_stress.get_particle_count()
                new_backend_count = int(current_backend_count * scale_factor)
                print(f"[SCALING] Current: {current_backend_count:,}, Factor: {scale_factor}, New: {new_backend_count:,}")
                self._backend_stress.scale_particles(new_backend_count)
                
                # Update workload type to show new backend count
                if self.visualize:
                    visible_count = self._initial_particle_count
                    self.workload_type = f"Bounce Simulation ({visible_count:,} visible, {new_backend_count:,} backend, {self._method})"
                else:
                    self.workload_type = f"Bounce Simulation ({new_backend_count:,} particles, {self._method})"
            else:
                # No backend stress - workload type stays the same (no scaling happens for visible particles)
                print("[SCALING] Backend stress not initialized - skipping scaling")
                pass
    
    def update_workload_display(self, visible_count: int):
        """Update workload type display with actual visible particle count (for visualization mode)."""
        if self.visualize and self.benchmark_type == "particle":
            if self._backend_stress.is_initialized():
                backend_count = self._backend_stress.get_particle_count()
                self.workload_type = f"Bounce Simulation ({visible_count:,} visible, {backend_count:,} backend, {self._method})"
            else:
                self.workload_type = f"Bounce Simulation ({visible_count:,} particles, {self._method})"
    
    def get_performance_stats(self, elapsed_seconds: float) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {
            'iterations': self.iterations,
            'workload_type': self.workload_type,
        }
        
        if self.benchmark_type == "gemm" and elapsed_seconds > 0:
            tflops = (self.total_flops / elapsed_seconds) / 1e12
            stats['total_flops'] = self.total_flops
            # Prefer history-based stats for avg/peak if available
            if self._tflops_history:
                avg_tflops = sum(self._tflops_history) / len(self._tflops_history)
                peak_tflops = max(self._tflops_history)
                stats['avg_tflops'] = round(avg_tflops, 3)
                stats['peak_tflops'] = round(peak_tflops, 3)
            else:
                stats['avg_tflops'] = round(tflops, 3)
                stats['peak_tflops'] = round(tflops, 3)
            stats['tflops'] = round(tflops, 3)
            stats['gflops'] = round(tflops * 1000, 2)
        elif self.benchmark_type == "particle" and elapsed_seconds > 0:
            stats['total_steps'] = self.total_steps
            stats['steps_per_second'] = round(self.total_steps / elapsed_seconds, 2)
            stats['particles_updated_per_second'] = round(
                (self.total_steps * self._active_count) / elapsed_seconds, 2
            )
            # If we have accumulated flops (from particle updates or backend stress), report TFLOPS
            if getattr(self, 'total_flops', 0) > 0:
                tflops = (self.total_flops / elapsed_seconds) / 1e12
                stats['tflops'] = round(tflops, 3)
                stats['avg_tflops'] = round(tflops, 3)
                stats['peak_tflops'] = round(tflops, 3)
        
        return stats

