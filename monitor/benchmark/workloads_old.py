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
            self.workload_type = f"Bounce Simulation ({n:,} particles, cupy)"
            
            # Initialize ALL arrays for target size
            self._gpu_arrays['x'] = cp.zeros(n, dtype=cp.float32)
            self._gpu_arrays['y'] = cp.zeros(n, dtype=cp.float32)
            self._gpu_arrays['vx'] = cp.zeros(n, dtype=cp.float32)
            self._gpu_arrays['vy'] = cp.zeros(n, dtype=cp.float32)
            self._gpu_arrays['mass'] = cp.zeros(n, dtype=cp.float32)
            self._gpu_arrays['radius'] = cp.zeros(n, dtype=cp.float32)
            self._gpu_arrays['active'] = cp.zeros(n, dtype=cp.bool_)
            self._gpu_arrays['bounce_cooldown'] = cp.zeros(n, dtype=cp.float32)
            self._gpu_arrays['color_state'] = cp.zeros(n, dtype=cp.float32)  # 0=default, >0=hit (fades)
            self._gpu_arrays['glow_intensity'] = cp.zeros(n, dtype=cp.float32)  # GPU-computed glow
            self._gpu_arrays['should_split'] = cp.zeros(n, dtype=cp.bool_)  # Mark for splitting
            self._gpu_arrays['split_cooldown'] = cp.zeros(n, dtype=cp.float32)  # 5-second cooldown after split
            self._gpu_arrays['ball_color'] = cp.zeros((n, 3), dtype=cp.float32)  # RGB color for each ball
            
            # Define distinct colors for the 4 big balls (R, G, B)
            big_ball_colors = cp.array([
                [1.0, 0.2, 0.2],  # Red
                [0.2, 1.0, 0.2],  # Green
                [0.2, 0.4, 1.0],  # Blue
                [1.0, 0.8, 0.2],  # Yellow
            ], dtype=cp.float32)
            
            # Create 4 BIG balls positioned close together (overlapping influence zones)
            big_positions = [(450, 350), (550, 350), (450, 450), (550, 450)]
            
            for i in range(4):
                self._gpu_arrays['x'][i] = big_positions[i][0]
                self._gpu_arrays['y'][i] = big_positions[i][1]
                self._gpu_arrays['vx'][i] = 0.0  # Stationary
                self._gpu_arrays['vy'][i] = 0.0
                self._gpu_arrays['mass'][i] = 1000.0  # Big mass
                self._gpu_arrays['radius'][i] = 36.0  # Big radius
                self._gpu_arrays['active'][i] = True
                self._gpu_arrays['ball_color'][i] = big_ball_colors[i]  # Assign unique color
            
            self._initial_particle_count = n
            self._active_count = 4  # Start with 4 big balls
            self._drop_timer = 0.0
            self._gravity_strength = 500.0  # Much stronger gravity for big balls (from slider)
            self._drop_rate = 1
            self._small_ball_speed = 300.0  # Faster constant speed for small balls
            self._initial_balls = 1  # Target number to spawn from slider
            self._max_balls_cap = 100000  # Hard limit from text input
            self._small_ball_count = 0  # Track small ball count separately
            self._split_enabled = False  # Controlled by UI toggle
    
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
            device = torch.device('cuda')
            
            self._gpu_arrays['x'] = torch.zeros(n, device=device, dtype=torch.float32)
            self._gpu_arrays['y'] = torch.zeros(n, device=device, dtype=torch.float32)
            self._gpu_arrays['vx'] = torch.zeros(n, device=device, dtype=torch.float32)
            self._gpu_arrays['vy'] = torch.zeros(n, device=device, dtype=torch.float32)
            self._gpu_arrays['mass'] = torch.zeros(n, device=device, dtype=torch.float32)
            self._gpu_arrays['radius'] = torch.zeros(n, device=device, dtype=torch.float32)
            self._gpu_arrays['active'] = torch.zeros(n, device=device, dtype=torch.bool)
            self._gpu_arrays['bounce_cooldown'] = torch.zeros(n, device=device, dtype=torch.float32)
            self._gpu_arrays['color_state'] = torch.zeros(n, device=device, dtype=torch.float32)
            self._gpu_arrays['glow_intensity'] = torch.zeros(n, device=device, dtype=torch.float32)
            self._gpu_arrays['should_split'] = torch.zeros(n, device=device, dtype=torch.bool)
            self._gpu_arrays['split_cooldown'] = torch.zeros(n, device=device, dtype=torch.float32)
            self._gpu_arrays['ball_color'] = torch.zeros((n, 3), device=device, dtype=torch.float32)  # RGB color
            
            # Define distinct colors for the 4 big balls
            big_ball_colors = torch.tensor([
                [1.0, 0.2, 0.2],  # Red
                [0.2, 1.0, 0.2],  # Green
                [0.2, 0.4, 1.0],  # Blue
                [1.0, 0.8, 0.2],  # Yellow
            ], device=device, dtype=torch.float32)
            
            # Create 4 BIG balls positioned close together
            big_positions = [(450, 350), (550, 350), (450, 450), (550, 450)]
            
            for i in range(4):
                self._gpu_arrays['x'][i] = big_positions[i][0]
                self._gpu_arrays['y'][i] = big_positions[i][1]
                self._gpu_arrays['vx'][i] = 0.0
                self._gpu_arrays['vy'][i] = 0.0
                self._gpu_arrays['mass'][i] = 1000.0
                self._gpu_arrays['radius'][i] = 36.0
                self._gpu_arrays['active'][i] = True
                self._gpu_arrays['ball_color'][i] = big_ball_colors[i]  # Assign unique color
            
            self._initial_particle_count = n
            self._active_count = 4
            self._drop_timer = 0.0
            self._gravity_strength = 500.0
            self._drop_rate = 1
            self._small_ball_speed = 300.0
            self._initial_balls = 1  # Target number to spawn from slider
            self._max_balls_cap = 100000  # Hard limit from text input
            self._small_ball_count = 0
            self._split_enabled = False  # Controlled by UI toggle
    
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
    
    def update_physics_params(self, gravity_strength=None, small_ball_speed=None, initial_balls=None, max_balls_cap=None):
        """Update physics parameters in real-time from UI sliders."""
        if gravity_strength is not None:
            self._gravity_strength = gravity_strength
        if small_ball_speed is not None:
            self._small_ball_speed = small_ball_speed
        if initial_balls is not None:
            self._initial_balls = initial_balls
        if max_balls_cap is not None:
            # If lowering cap, instantly remove excess small balls
            if max_balls_cap < self._small_ball_count:
                self._remove_excess_balls(int(max_balls_cap))
            self._max_balls_cap = max_balls_cap
    
    def update_split_enabled(self, split_enabled: bool):
        """Update ball splitting toggle."""
        self._split_enabled = split_enabled
    
    def _remove_excess_balls(self, target_count: int):
        """Remove excess small balls when slider is lowered."""
        if self._method == 'cupy':
            cp = self._cp
            active = self._gpu_arrays['active']
            mass = self._gpu_arrays['mass']
            # Find small balls (mass < 100)
            small_balls = (mass < 100.0) & active
            small_indices = cp.where(small_balls)[0]
            current_count = len(small_indices)
            
            if current_count > target_count:
                # Deactivate excess balls (from the end)
                excess_count = current_count - target_count
                remove_indices = small_indices[-excess_count:]
                active[remove_indices] = False
                self._active_count -= excess_count
                self._small_ball_count = target_count
                self._gpu_arrays['active'] = active
        elif self._method == 'torch':
            torch = self._torch
            active = self._gpu_arrays['active']
            mass = self._gpu_arrays['mass']
            small_balls = (mass < 100.0) & active
            small_indices = torch.where(small_balls)[0]
            current_count = len(small_indices)
            
            if current_count > target_count:
                excess_count = current_count - target_count
                remove_indices = small_indices[-excess_count:]
                active[remove_indices] = False
                self._active_count -= excess_count
                self._small_ball_count = target_count
                self._gpu_arrays['active'] = active
    
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
        """
        NEW SIMPLE PHYSICS:
        - 4 big balls with gravity (mass 1000), start stationary
        - Small balls have NO gravity (mass 1), constant velocity bouncing
        - Big balls bounce off each other temporarily (disables gravity during bounce)
        - Small balls bounce off walls and big balls
        """
        if self._method == 'cupy':
            cp = self._cp
            x = self._gpu_arrays['x']
            y = self._gpu_arrays['y']
            vx = self._gpu_arrays['vx']
            vy = self._gpu_arrays['vy']
            mass = self._gpu_arrays['mass']
            radius = self._gpu_arrays['radius']
            active = self._gpu_arrays['active']
            bounce_cooldown = self._gpu_arrays['bounce_cooldown']
            color_state = self._gpu_arrays['color_state']
            glow_intensity = self._gpu_arrays['glow_intensity']
            should_split = self._gpu_arrays['should_split']
            split_cooldown = self._gpu_arrays['split_cooldown']
            ball_color = self._gpu_arrays['ball_color']
            
            dt = 0.016
            G = self._gravity_strength  # Use slider value
            small_ball_speed = self._small_ball_speed  # Use slider value
            initial_balls = int(self._initial_balls)  # Target for spawning
            max_balls_cap = int(self._max_balls_cap)  # Hard limit
            
            # Drop small balls continuously until we reach initial_balls count
            if self._small_ball_count < initial_balls:
                if self._drop_timer <= 0:
                    inactive_indices = cp.where(~active)[0]
                    if len(inactive_indices) > 0:
                        idx = int(inactive_indices[0])
                        x[idx] = 500.0  # Center top (water spout)
                        y[idx] = 50.0
                        vx[idx] = (cp.random.rand() - 0.5) * small_ball_speed * 0.2  # Slight random horizontal
                        vy[idx] = small_ball_speed
                        mass[idx] = 1.0
                        radius[idx] = 8.0
                        active[idx] = True
                        ball_color[idx] = cp.array([1.0, 1.0, 1.0], dtype=cp.float32)  # White initially
                        self._active_count += 1
                        self._small_ball_count += 1
                        self._drop_timer = 0.3  # Faster drops
                else:
                    self._drop_timer -= dt
            
            # Get active particles
            active_mask = active
            n_active = int(cp.sum(active_mask))
            
            if n_active > 0:
                x_act = x[active_mask]
                y_act = y[active_mask]
                vx_act = vx[active_mask]
                vy_act = vy[active_mask]
                mass_act = mass[active_mask]
                radius_act = radius[active_mask]
                cooldown_act = bounce_cooldown[active_mask]
                split_cooldown_act = split_cooldown[active_mask]
                
                # Identify big balls (mass >= 100)
                big_balls = mass_act >= 100.0
                
                # Initialize accelerations
                ax = cp.zeros_like(vx_act)
                ay = cp.zeros_like(vy_act)
                
                # Gravity between big balls - ALWAYS ACTIVE (permanent)
                # Use N×N pairwise computation for all big balls simultaneously
                if cp.any(big_balls):
                    # Get indices of big balls
                    big_indices = cp.where(big_balls)[0]
                    n_big = len(big_indices)
                    
                    if n_big > 1:
                        # Extract big ball positions and masses
                        x_big = x_act[big_indices]
                        y_big = y_act[big_indices]
                        mass_big = mass_act[big_indices]
                        
                        # Compute ALL pairwise distances (N×N matrix)
                        dx_matrix = x_big[:, cp.newaxis] - x_big[cp.newaxis, :]  # [N, N]
                        dy_matrix = y_big[:, cp.newaxis] - y_big[cp.newaxis, :]  # [N, N]
                        
                        # Distance squared matrix
                        r2_matrix = dx_matrix**2 + dy_matrix**2 + 10.0  # Prevent singularity
                        r_matrix = cp.sqrt(r2_matrix)
                        
                        # Gravitational force matrix: F = G * m_j / r^2
                        # Shape: [N, N] where force_matrix[i, j] = force on i from j
                        force_matrix = G * mass_big[cp.newaxis, :] / (r2_matrix + 1.0)
                        
                        # Set diagonal to zero (ball doesn't attract itself)
                        cp.fill_diagonal(force_matrix, 0.0)
                        
                        # Compute acceleration components
                        # a_x[i] = sum_j(F[i,j] * dx[i,j] / r[i,j])
                        ax_big = cp.sum(force_matrix * dx_matrix / (r_matrix + 1e-10), axis=1)
                        ay_big = cp.sum(force_matrix * dy_matrix / (r_matrix + 1e-10), axis=1)
                        
                        # Apply to the big ball indices
                        ax[big_indices] = ax_big
                        ay[big_indices] = ay_big
                
                # Update velocities - but NOT for small balls (they keep constant speed)
                # Only apply acceleration to big balls
                vx_act = cp.where(big_balls, vx_act + ax * dt, vx_act)
                vy_act = cp.where(big_balls, vy_act + ay * dt, vy_act)
                
                # Normalize small ball velocities to maintain constant speed
                small_balls_mask = ~big_balls
                if cp.any(small_balls_mask):
                    speed = cp.sqrt(vx_act**2 + vy_act**2)
                    vx_act = cp.where(small_balls_mask & (speed > 0), vx_act / speed * small_ball_speed, vx_act)
                    vy_act = cp.where(small_balls_mask & (speed > 0), vy_act / speed * small_ball_speed, vy_act)
                x_act = x_act + vx_act * dt
                y_act = y_act + vy_act * dt
                
                # Decrease bounce cooldown
                cooldown_act = cp.maximum(0.0, cooldown_act - dt)
                
                # Wall collisions (bounce)
                # Left/right walls
                hit_left = x_act - radius_act < 0
                hit_right = x_act + radius_act > 1000
                vx_act = cp.where(hit_left | hit_right, -vx_act * 0.8, vx_act)
                x_act = cp.where(hit_left, radius_act, x_act)
                x_act = cp.where(hit_right, 1000 - radius_act, x_act)
                
                # Top/bottom walls
                hit_top = y_act - radius_act < 0
                hit_bottom = y_act + radius_act > 800
                vy_act = cp.where(hit_top | hit_bottom, -vy_act * 0.8, vy_act)
                y_act = cp.where(hit_top, radius_act, y_act)
                y_act = cp.where(hit_bottom, 800 - radius_act, y_act)
                
                # GPU-ACCELERATED Ball-to-ball collisions with proper momentum conservation
                # Build pairwise distance matrices [N×N]
                dx_matrix = x_act[:, cp.newaxis] - x_act[cp.newaxis, :]
                dy_matrix = y_act[:, cp.newaxis] - y_act[cp.newaxis, :]
                dist_matrix = cp.sqrt(dx_matrix**2 + dy_matrix**2 + 1e-10)
                
                # Sum of radii matrix [N×N]
                radius_sum = radius_act[:, cp.newaxis] + radius_act[cp.newaxis, :]
                
                # Collision mask: distance < sum of radii (with small tolerance)
                collision_mask = (dist_matrix < radius_sum + 2.0) & (dist_matrix > 1e-5)
                
                # Upper triangular only (avoid double-processing)
                collision_mask = cp.triu(collision_mask, k=1)
                
                # Get collision pairs
                collision_i, collision_j = cp.where(collision_mask)
                
                # Process all collisions in parallel on GPU
                if len(collision_i) > 0:
                    # Extract collision pair data
                    xi, yi = x_act[collision_i], y_act[collision_i]
                    xj, yj = x_act[collision_j], y_act[collision_j]
                    vxi, vyi = vx_act[collision_i], vy_act[collision_i]
                    vxj, vyj = vx_act[collision_j], vy_act[collision_j]
                    mi, mj = mass_act[collision_i], mass_act[collision_j]
                    ri, rj = radius_act[collision_i], radius_act[collision_j]
                    
                    # Collision normal vectors
                    dx_col = xj - xi
                    dy_col = yj - yi
                    dist_col = cp.sqrt(dx_col**2 + dy_col**2 + 1e-10)
                    nx = dx_col / dist_col
                    ny = dy_col / dist_col
                    
                    # Relative velocity
                    dvx = vxj - vxi
                    dvy = vyj - vyi
                    dot = dvx * nx + dvy * ny
                    
                    # Only process if moving towards each other
                    approaching = dot < 0
                    
                    # PROPER ELASTIC COLLISION with momentum conservation
                    # For elastic collision: v'_i = v_i + (2*m_j / (m_i + m_j)) * dot * n
                    #                        v'_j = v_j - (2*m_i / (m_i + m_j)) * dot * n
                    total_mass = mi + mj
                    
                    # Big balls are slightly less rigid (0.95 coefficient of restitution)
                    big_i = mass_act[collision_i] >= 100.0
                    big_j = mass_act[collision_j] >= 100.0
                    restitution = cp.where(big_i | big_j, 0.95, 1.0)
                    
                    impulse_factor_i = 2.0 * mj / (total_mass + 1e-10) * restitution
                    impulse_factor_j = 2.0 * mi / (total_mass + 1e-10) * restitution
                    
                    # Apply impulse (only where approaching)
                    impulse_i_x = cp.where(approaching, impulse_factor_i * dot * nx, 0.0)
                    impulse_i_y = cp.where(approaching, impulse_factor_i * dot * ny, 0.0)
                    impulse_j_x = cp.where(approaching, -impulse_factor_j * dot * nx, 0.0)
                    impulse_j_y = cp.where(approaching, -impulse_factor_j * dot * ny, 0.0)
                    
                    # Accumulate velocity changes (handle multiple collisions per particle)
                    cp.add.at(vx_act, collision_i, impulse_i_x)
                    cp.add.at(vy_act, collision_i, impulse_i_y)
                    cp.add.at(vx_act, collision_j, impulse_j_x)
                    cp.add.at(vy_act, collision_j, impulse_j_y)
                    
                    # Mark small balls that collided with big balls (color change)
                    big_balls_array = mass_act >= 100.0
                    small_i = ~big_balls_array[collision_i] & big_balls_array[collision_j]
                    small_j = ~big_balls_array[collision_j] & big_balls_array[collision_i]
                    
                    # Copy big ball color to small ball permanently
                    ball_color_act = ball_color[active_mask]
                    for idx in range(len(collision_i)):
                        if small_i[idx]:  # Small ball i hit big ball j
                            ball_color_act[collision_i[idx]] = ball_color_act[collision_j[idx]]
                        if small_j[idx]:  # Small ball j hit big ball i
                            ball_color_act[collision_j[idx]] = ball_color_act[collision_i[idx]]
                    ball_color[active_mask] = ball_color_act
                    
                    # Set color state to 1.0 for small balls that hit big balls
                    color_state_act = color_state[active_mask]
                    color_state_act[collision_i] = cp.where(small_i, 1.0, color_state_act[collision_i])
                    color_state_act[collision_j] = cp.where(small_j, 1.0, color_state_act[collision_j])
                    color_state[active_mask] = color_state_act
                    
                    # Mark ALL colliding small balls for splitting (controlled by toggle)
                    # Small balls split on ANY collision (small-big OR small-small)
                    # Only if they're not on cooldown (5 seconds after previous split)
                    if self._split_enabled:
                        should_split_act = should_split[active_mask]
                        is_small_i = mass_act[collision_i] < 100.0
                        is_small_j = mass_act[collision_j] < 100.0
                        can_split_i = split_cooldown_act[collision_i] <= 0.0
                        can_split_j = split_cooldown_act[collision_j] <= 0.0
                        # Split if: small ball + off cooldown (regardless of what it hit)
                        should_split_act[collision_i] = cp.where(is_small_i & can_split_i, True, should_split_act[collision_i])
                        should_split_act[collision_j] = cp.where(is_small_j & can_split_j, True, should_split_act[collision_j])
                        should_split[active_mask] = should_split_act
                        
                        # Debug: print when we mark balls for splitting
                        marked_count = int(cp.sum(should_split_act[collision_i] | should_split_act[collision_j]))
                        if marked_count > 0:
                            print(f"[DEBUG] Marked {marked_count} balls for splitting")
                    
                    # Separate overlapping balls
                    overlap = ri + rj - dist_col
                    separation = overlap * 0.6
                    cp.add.at(x_act, collision_i, -nx * separation)
                    cp.add.at(y_act, collision_i, -ny * separation)
                    cp.add.at(x_act, collision_j, nx * separation)
                    cp.add.at(y_act, collision_j, ny * separation)
                
                # Write back
                x[active_mask] = x_act
                y[active_mask] = y_act
                vx[active_mask] = vx_act
                vy[active_mask] = vy_act
                bounce_cooldown[active_mask] = cooldown_act
                
                # GPU-compute glow intensity based on speed (shader effect)
                speed = cp.sqrt(vx_act**2 + vy_act**2)
                glow_act = cp.minimum(1.0, speed / 500.0)  # Normalize to [0, 1]
                glow_intensity[active_mask] = glow_act
                
                # Fade color state over time
                color_state_act = cp.maximum(0.0, color_state[active_mask] - dt * 2.0)
                color_state[active_mask] = color_state_act
                
                # Decay split cooldown timer
                split_cooldown_act = cp.maximum(0.0, split_cooldown_act - dt)
                split_cooldown[active_mask] = split_cooldown_act
            
            # Spawn child particles from collisions (2 per parent) - with safety limit
            if self._split_enabled and self._active_count < 50000:  # Safety: max 50k particles
                split_indices = cp.where(should_split & active)[0]
                if len(split_indices) > 0:
                    print(f"[DEBUG] Found {len(split_indices)} balls ready to split, active_count={self._active_count}")
                    inactive_indices = cp.where(~active)[0]
                    spawn_count = min(len(split_indices) * 2, len(inactive_indices), 1000)  # Max 1000 per frame
                    
                    if spawn_count > 0:
                        for idx, parent_idx in enumerate(split_indices[:spawn_count // 2]):
                            if idx * 2 + 1 < len(inactive_indices):
                                # Spawn 2 children near parent
                                child1_idx = inactive_indices[idx * 2]
                                child2_idx = inactive_indices[idx * 2 + 1]
                                
                                # Child 1
                                x[child1_idx] = x[parent_idx] + cp.random.uniform(-10, 10)
                                y[child1_idx] = y[parent_idx] + cp.random.uniform(-10, 10)
                                angle1 = cp.random.uniform(0, 2 * cp.pi)
                                vx[child1_idx] = cp.cos(angle1) * small_ball_speed
                                vy[child1_idx] = cp.sin(angle1) * small_ball_speed
                                mass[child1_idx] = 1.0
                                radius[child1_idx] = 8.0
                                active[child1_idx] = True
                                split_cooldown[child1_idx] = 5.0  # 5-second cooldown
                                ball_color[child1_idx] = ball_color[parent_idx]  # Inherit parent color
                                
                                # Child 2
                                x[child2_idx] = x[parent_idx] + cp.random.uniform(-10, 10)
                                y[child2_idx] = y[parent_idx] + cp.random.uniform(-10, 10)
                                angle2 = cp.random.uniform(0, 2 * cp.pi)
                                vx[child2_idx] = cp.cos(angle2) * small_ball_speed
                                vy[child2_idx] = cp.sin(angle2) * small_ball_speed
                                mass[child2_idx] = 1.0
                                radius[child2_idx] = 8.0
                                active[child2_idx] = True
                                split_cooldown[child2_idx] = 5.0  # 5-second cooldown
                                ball_color[child2_idx] = ball_color[parent_idx]  # Inherit parent color
                                
                                # Set parent cooldown
                                split_cooldown[parent_idx] = 5.0
                                
                                self._active_count += 2
                                self._small_ball_count += 2
                    
                    # Clear split flags
                    should_split[split_indices] = False
            
            # Enforce max_balls_cap by removing excess balls
            if self._small_ball_count > max_balls_cap:
                excess = self._small_ball_count - max_balls_cap
                small_balls = (mass < 100.0) & active
                small_indices = cp.where(small_balls)[0]
                if len(small_indices) > max_balls_cap:
                    remove_indices = small_indices[max_balls_cap:]
                    active[remove_indices] = False
                    self._active_count -= len(remove_indices)
                    self._small_ball_count = max_balls_cap
            
            elif self._active_count >= 50000:
                # Safety shutdown
                print(f"\n[SAFETY] Particle count reached {self._active_count} - disabling splitting")
                self._split_enabled = False
            
            self._gpu_arrays['x'] = x
            self._gpu_arrays['y'] = y
            self._gpu_arrays['vx'] = vx
            self._gpu_arrays['vy'] = vy
            self._gpu_arrays['bounce_cooldown'] = bounce_cooldown
            self._gpu_arrays['color_state'] = color_state
            self._gpu_arrays['glow_intensity'] = glow_intensity
            self._gpu_arrays['should_split'] = should_split
            self._gpu_arrays['split_cooldown'] = split_cooldown
            self._gpu_arrays['ball_color'] = ball_color
            
            cp.cuda.Stream.null.synchronize()
            self.total_steps += 1
            
        elif self._method == 'torch':
            # PyTorch version - same simple physics
            torch = self._torch
            x = self._gpu_arrays['x']
            y = self._gpu_arrays['y']
            vx = self._gpu_arrays['vx']
            vy = self._gpu_arrays['vy']
            mass = self._gpu_arrays['mass']
            radius = self._gpu_arrays['radius']
            active = self._gpu_arrays['active']
            bounce_cooldown = self._gpu_arrays['bounce_cooldown']
            color_state = self._gpu_arrays['color_state']
            glow_intensity = self._gpu_arrays['glow_intensity']
            should_split = self._gpu_arrays['should_split']
            split_cooldown = self._gpu_arrays['split_cooldown']
            ball_color = self._gpu_arrays['ball_color']
            
            dt = 0.016
            G = self._gravity_strength
            small_ball_speed = self._small_ball_speed
            initial_balls = int(self._initial_balls)  # Target for spawning
            max_balls_cap = int(self._max_balls_cap)  # Hard limit
            
            # Drop small balls until initial_balls reached
            if self._small_ball_count < initial_balls:
                if self._drop_timer <= 0:
                    inactive_indices = torch.where(~active)[0]
                    if len(inactive_indices) > 0:
                        idx = int(inactive_indices[0])
                        x[idx] = 500.0
                        y[idx] = 50.0
                        vx[idx] = (torch.rand(1, device=x.device) - 0.5) * small_ball_speed * 0.2
                        vy[idx] = small_ball_speed
                        mass[idx] = 1.0
                        radius[idx] = 8.0
                        active[idx] = True
                        ball_color[idx] = torch.tensor([1.0, 1.0, 1.0], dtype=torch.float32, device=x.device)  # White initially
                        self._active_count += 1
                        self._small_ball_count += 1
                        self._drop_timer = 0.3
                else:
                    self._drop_timer -= dt
            
            # Process active particles
            active_mask = active
            n_active = int(torch.sum(active_mask))
            
            if n_active > 0:
                x_act = x[active_mask]
                y_act = y[active_mask]
                vx_act = vx[active_mask]
                vy_act = vy[active_mask]
                mass_act = mass[active_mask]
                radius_act = radius[active_mask]
                cooldown_act = bounce_cooldown[active_mask]
                
                big_balls = mass_act >= 100.0
                ax = torch.zeros_like(vx_act)
                ay = torch.zeros_like(vy_act)
                
                # Gravity between big balls - ALWAYS ACTIVE
                # N×N pairwise computation for all big balls
                if torch.any(big_balls):
                    big_indices = torch.where(big_balls)[0]
                    n_big = len(big_indices)
                    
                    if n_big > 1:
                        x_big = x_act[big_indices]
                        y_big = y_act[big_indices]
                        mass_big = mass_act[big_indices]
                        
                        # Pairwise distance matrices
                        dx_matrix = x_big[:, None] - x_big[None, :]
                        dy_matrix = y_big[:, None] - y_big[None, :]
                        
                        r2_matrix = dx_matrix**2 + dy_matrix**2 + 10.0
                        r_matrix = torch.sqrt(r2_matrix)
                        
                        # Force matrix
                        force_matrix = G * mass_big[None, :] / (r2_matrix + 1.0)
                        force_matrix.fill_diagonal_(0.0)
                        
                        # Compute accelerations
                        ax_big = torch.sum(force_matrix * dx_matrix / (r_matrix + 1e-10), dim=1)
                        ay_big = torch.sum(force_matrix * dy_matrix / (r_matrix + 1e-10), dim=1)
                        
                        ax[big_indices] = ax_big
                        ay[big_indices] = ay_big
                
                # Update - only apply to big balls
                vx_act = torch.where(big_balls, vx_act + ax * dt, vx_act)
                vy_act = torch.where(big_balls, vy_act + ay * dt, vy_act)
                
                # Normalize small ball velocities
                small_balls_mask = ~big_balls
                if torch.any(small_balls_mask):
                    speed = torch.sqrt(vx_act**2 + vy_act**2)
                    vx_act = torch.where(small_balls_mask & (speed > 0), vx_act / speed * small_ball_speed, vx_act)
                    vy_act = torch.where(small_balls_mask & (speed > 0), vy_act / speed * small_ball_speed, vy_act)
                x_act = x_act + vx_act * dt
                y_act = y_act + vy_act * dt
                cooldown_act = torch.maximum(torch.tensor(0.0, device=x.device), cooldown_act - dt)
                
                # Wall collisions
                hit_left = x_act - radius_act < 0
                hit_right = x_act + radius_act > 1000
                vx_act = torch.where(hit_left | hit_right, -vx_act * 0.8, vx_act)
                x_act = torch.where(hit_left, radius_act, x_act)
                x_act = torch.where(hit_right, 1000 - radius_act, x_act)
                
                hit_top = y_act - radius_act < 0
                hit_bottom = y_act + radius_act > 800
                vy_act = torch.where(hit_top | hit_bottom, -vy_act * 0.8, vy_act)
                y_act = torch.where(hit_top, radius_act, y_act)
                y_act = torch.where(hit_bottom, 800 - radius_act, y_act)
                
                # GPU-ACCELERATED Ball collisions with proper momentum conservation
                # Build pairwise distance matrices [N×N]
                dx_matrix = x_act[:, None] - x_act[None, :]
                dy_matrix = y_act[:, None] - y_act[None, :]
                dist_matrix = torch.sqrt(dx_matrix**2 + dy_matrix**2 + 1e-10)
                
                # Sum of radii matrix [N×N]
                radius_sum = radius_act[:, None] + radius_act[None, :]
                
                # Collision mask: distance < sum of radii
                collision_mask = (dist_matrix < radius_sum + 2.0) & (dist_matrix > 1e-5)
                
                # Upper triangular only
                collision_mask = torch.triu(collision_mask, diagonal=1)
                
                # Get collision pairs
                collision_i, collision_j = torch.where(collision_mask)
                
                # Process all collisions in parallel on GPU
                if len(collision_i) > 0:
                    # Extract collision pair data
                    xi, yi = x_act[collision_i], y_act[collision_i]
                    xj, yj = x_act[collision_j], y_act[collision_j]
                    vxi, vyi = vx_act[collision_i], vy_act[collision_i]
                    vxj, vyj = vx_act[collision_j], vy_act[collision_j]
                    mi, mj = mass_act[collision_i], mass_act[collision_j]
                    ri, rj = radius_act[collision_i], radius_act[collision_j]
                    
                    # Collision normals
                    dx_col = xj - xi
                    dy_col = yj - yi
                    dist_col = torch.sqrt(dx_col**2 + dy_col**2 + 1e-10)
                    nx = dx_col / dist_col
                    ny = dy_col / dist_col
                    
                    # Relative velocity
                    dvx = vxj - vxi
                    dvy = vyj - vyi
                    dot = dvx * nx + dvy * ny
                    
                    # Only process if approaching
                    approaching = dot < 0
                    
                    # PROPER ELASTIC COLLISION with momentum conservation
                    # v'_i = v_i + (2*m_j / (m_i + m_j)) * dot * n
                    total_mass = mi + mj
                    
                    # Big balls are slightly less rigid (0.95 coefficient of restitution)
                    big_i = mass_act[collision_i] >= 100.0
                    big_j = mass_act[collision_j] >= 100.0
                    restitution = torch.where(big_i | big_j, torch.tensor(0.95, device=mi.device), torch.tensor(1.0, device=mi.device))
                    
                    impulse_factor_i = 2.0 * mj / (total_mass + 1e-10) * restitution
                    impulse_factor_j = 2.0 * mi / (total_mass + 1e-10) * restitution
                    
                    # Apply impulse (only where approaching)
                    impulse_i_x = torch.where(approaching, impulse_factor_i * dot * nx, torch.zeros_like(nx))
                    impulse_i_y = torch.where(approaching, impulse_factor_i * dot * ny, torch.zeros_like(ny))
                    impulse_j_x = torch.where(approaching, -impulse_factor_j * dot * nx, torch.zeros_like(nx))
                    impulse_j_y = torch.where(approaching, -impulse_factor_j * dot * ny, torch.zeros_like(ny))
                    
                    # Accumulate velocity changes
                    vx_act.index_add_(0, collision_i, impulse_i_x)
                    vy_act.index_add_(0, collision_i, impulse_i_y)
                    vx_act.index_add_(0, collision_j, impulse_j_x)
                    vy_act.index_add_(0, collision_j, impulse_j_y)
                    
                    # Mark small balls that hit big balls
                    big_balls_array = mass_act >= 100.0
                    small_i = (~big_balls_array[collision_i]) & big_balls_array[collision_j]
                    small_j = (~big_balls_array[collision_j]) & big_balls_array[collision_i]
                    
                    # Copy big ball color to small ball permanently
                    ball_color_act = ball_color[active_mask]
                    for idx in range(len(collision_i)):
                        if small_i[idx]:  # Small ball i hit big ball j
                            ball_color_act[collision_i[idx]] = ball_color_act[collision_j[idx]]
                        if small_j[idx]:  # Small ball j hit big ball i
                            ball_color_act[collision_j[idx]] = ball_color_act[collision_i[idx]]
                    ball_color[active_mask] = ball_color_act
                    
                    color_state_act = color_state[active_mask]
                    color_state_act[collision_i] = torch.where(small_i, torch.ones_like(color_state_act[collision_i]), color_state_act[collision_i])
                    color_state_act[collision_j] = torch.where(small_j, torch.ones_like(color_state_act[collision_j]), color_state_act[collision_j])
                    color_state[active_mask] = color_state_act
                    
                    # Mark ALL colliding small balls for splitting (controlled by toggle)
                    # Small balls split on ANY collision (small-big OR small-small)
                    # Only if they're not on cooldown (5 seconds after previous split)
                    if self._split_enabled:
                        should_split_act = should_split[active_mask]
                        split_cooldown_act = split_cooldown[active_mask]
                        is_small_i = mass_act[collision_i] < 100.0
                        is_small_j = mass_act[collision_j] < 100.0
                        can_split_i = split_cooldown_act[collision_i] <= 0.0
                        can_split_j = split_cooldown_act[collision_j] <= 0.0
                        # Split if: small ball + off cooldown (regardless of what it hit)
                        should_split_act[collision_i] = torch.where(is_small_i & can_split_i, torch.ones_like(should_split_act[collision_i], dtype=torch.bool), should_split_act[collision_i])
                        should_split_act[collision_j] = torch.where(is_small_j & can_split_j, torch.ones_like(should_split_act[collision_j], dtype=torch.bool), should_split_act[collision_j])
                        should_split[active_mask] = should_split_act
                    
                    # Separate overlapping balls
                    overlap = ri + rj - dist_col
                    separation = overlap * 0.6
                    x_act.index_add_(0, collision_i, -nx * separation)
                    y_act.index_add_(0, collision_i, -ny * separation)
                    x_act.index_add_(0, collision_j, nx * separation)
                    y_act.index_add_(0, collision_j, ny * separation)
                
                x[active_mask] = x_act
                y[active_mask] = y_act
                vx[active_mask] = vx_act
                vy[active_mask] = vy_act
                bounce_cooldown[active_mask] = cooldown_act
                
                # GPU-compute glow based on speed
                speed = torch.sqrt(vx_act**2 + vy_act**2)
                glow_act = torch.minimum(torch.ones_like(speed), speed / 500.0)
                glow_intensity[active_mask] = glow_act
                
                # Fade color state
                color_state_act = torch.maximum(torch.zeros_like(color_state[active_mask]), color_state[active_mask] - dt * 2.0)
                color_state[active_mask] = color_state_act
                
                # Decay split cooldown timer
                split_cooldown_act = torch.maximum(torch.zeros_like(split_cooldown[active_mask]), split_cooldown[active_mask] - dt)
                split_cooldown[active_mask] = split_cooldown_act
            
            # Spawn child particles (2 per parent) - with safety limit
            if self._split_enabled and self._active_count < 50000:
                split_indices = torch.where(should_split & active)[0]
                if len(split_indices) > 0:
                    inactive_indices = torch.where(~active)[0]
                    spawn_count = min(len(split_indices) * 2, len(inactive_indices), 1000)
                    
                    if spawn_count > 0:
                        for idx in range(min(len(split_indices), spawn_count // 2)):
                            parent_idx = split_indices[idx]
                            if idx * 2 + 1 < len(inactive_indices):
                                child1_idx = inactive_indices[idx * 2]
                                child2_idx = inactive_indices[idx * 2 + 1]
                                
                                # Spawn children
                                x[child1_idx] = x[parent_idx] + torch.randn(1, device=x.device) * 10
                                y[child1_idx] = y[parent_idx] + torch.randn(1, device=x.device) * 10
                                angle1 = torch.rand(1, device=x.device) * 2 * 3.14159
                                vx[child1_idx] = torch.cos(angle1) * small_ball_speed
                                vy[child1_idx] = torch.sin(angle1) * small_ball_speed
                                mass[child1_idx] = 1.0
                                radius[child1_idx] = 8.0
                                active[child1_idx] = True
                                split_cooldown[child1_idx] = 5.0  # 5-second cooldown
                                ball_color[child1_idx] = ball_color[parent_idx]  # Inherit parent color
                                
                                x[child2_idx] = x[parent_idx] + torch.randn(1, device=x.device) * 10
                                y[child2_idx] = y[parent_idx] + torch.randn(1, device=x.device) * 10
                                angle2 = torch.rand(1, device=x.device) * 2 * 3.14159
                                vx[child2_idx] = torch.cos(angle2) * small_ball_speed
                                vy[child2_idx] = torch.sin(angle2) * small_ball_speed
                                mass[child2_idx] = 1.0
                                radius[child2_idx] = 8.0
                                active[child2_idx] = True
                                split_cooldown[child2_idx] = 5.0  # 5-second cooldown
                                ball_color[child2_idx] = ball_color[parent_idx]  # Inherit parent color
                                
                                # Set parent cooldown
                                split_cooldown[parent_idx] = 5.0
                                
                                self._active_count += 2
                                self._small_ball_count += 2
                    
                    should_split[split_indices] = False
            
            # Enforce max_balls_cap by removing excess balls
            if self._small_ball_count > max_balls_cap:
                excess = self._small_ball_count - max_balls_cap
                small_balls = (mass < 100.0) & active
                small_indices = torch.where(small_balls)[0]
                if len(small_indices) > max_balls_cap:
                    remove_indices = small_indices[max_balls_cap:]
                    active[remove_indices] = False
                    self._active_count -= len(remove_indices)
                    self._small_ball_count = max_balls_cap
            
            elif self._active_count >= 50000:
                print(f"\n[SAFETY] Particle count reached {self._active_count} - disabling splitting")
                self._split_enabled = False
            
            self._gpu_arrays['x'] = x
            self._gpu_arrays['y'] = y
            self._gpu_arrays['vx'] = vx
            self._gpu_arrays['vy'] = vy
            self._gpu_arrays['bounce_cooldown'] = bounce_cooldown
            self._gpu_arrays['color_state'] = color_state
            self._gpu_arrays['glow_intensity'] = glow_intensity
            self._gpu_arrays['should_split'] = should_split
            self._gpu_arrays['split_cooldown'] = split_cooldown
            
            torch.cuda.synchronize()
            self.total_steps += 1
    
    def get_particle_sample(self, max_samples: int = 2000):
        """
        Get a sampled subset of ACTIVE particle positions, masses, colors, and glow for visualization.
        
        Args:
            max_samples: Maximum number of particles to return
            
        Returns:
            tuple of (positions, masses, colors, glows) or (None, None, None, None) if not available
            positions: numpy array of shape (N, 2) with [x, y]
            masses: numpy array of shape (N,) with particle masses
            colors: numpy array of shape (N,) with color state (0-1)
            glows: numpy array of shape (N,) with glow intensity (0-1)
        """
        if not self._initialized or self.benchmark_type != "particle":
            return None, None, None, None
        
        try:
            x = self._gpu_arrays.get('x')
            y = self._gpu_arrays.get('y')
            mass = self._gpu_arrays.get('mass')
            active = self._gpu_arrays.get('active')
            color_state = self._gpu_arrays.get('color_state')
            glow_intensity = self._gpu_arrays.get('glow_intensity')
            
            if x is None or y is None or mass is None or active is None:
                return None, None, None, None
            
            if self._method == 'cupy':
                # Get only active particles
                active_mask = active.get()  # Transfer to CPU
                x_all = x.get()
                y_all = y.get()
                mass_all = mass.get()
                color_all = color_state.get() if color_state is not None else np.zeros(len(active_mask))
                glow_all = glow_intensity.get() if glow_intensity is not None else np.zeros(len(active_mask))
                
                x_active = x_all[active_mask]
                y_active = y_all[active_mask]
                mass_active = mass_all[active_mask]
                color_active = color_all[active_mask]
                glow_active = glow_all[active_mask]
                
            elif self._method == 'torch':
                active_mask = active.cpu().numpy()
                x_all = x.cpu().numpy()
                y_all = y.cpu().numpy()
                mass_all = mass.cpu().numpy()
                color_all = color_state.cpu().numpy() if color_state is not None else np.zeros(len(active_mask))
                glow_all = glow_intensity.cpu().numpy() if glow_intensity is not None else np.zeros(len(active_mask))
                
                x_active = x_all[active_mask]
                y_active = y_all[active_mask]
                mass_active = mass_all[active_mask]
                color_active = color_all[active_mask]
                glow_active = glow_all[active_mask]
            else:
                return None, None, None, None
            
            # Sample if too many
            n_active = len(x_active)
            if n_active > max_samples:
                step = n_active // max_samples
                x_active = x_active[::step]
                y_active = y_active[::step]
                mass_active = mass_active[::step]
                color_active = color_active[::step]
                glow_active = glow_active[::step]
            
            # Stack into Nx2 array
            import numpy as np
            positions = np.column_stack([x_active, y_active])
            return positions, mass_active, color_active, glow_active
            
        except Exception:
            return None, None, None, None
    
    def get_influence_boundaries(self, gravity_strength: float = 500.0):
        """
        Get positions of large bodies with gravity radius based on actual force strength.
        Radius shows where gravitational force drops to visible threshold.
        
        Args:
            gravity_strength: Current gravity constant
            
        Returns:
            list of (x, y, radius) tuples for large bodies, or empty list
        """
        if not self._initialized or self.benchmark_type != "particle":
            return []
        
        try:
            x = self._gpu_arrays.get('x')
            y = self._gpu_arrays.get('y')
            mass = self._gpu_arrays.get('mass')
            active = self._gpu_arrays.get('active')
            
            if x is None or y is None or mass is None or active is None:
                return []
            
            if self._method == 'cupy':
                x_all = x.get()
                y_all = y.get()
                mass_all = mass.get()
                active_mask = active.get()
            elif self._method == 'torch':
                x_all = x.cpu().numpy()
                y_all = y.cpu().numpy()
                mass_all = mass.cpu().numpy()
                active_mask = active.cpu().numpy()
            else:
                return []
            
            # Find large bodies (mass >= 1000)
            large_mask = (mass_all >= 1000.0) & active_mask
            
            boundaries = []
            for i in range(len(x_all)):
                if large_mask[i]:
                    # Calculate radius where gravitational force is perceptible
                    # F = G*M/r^2 -> r = sqrt(G*M/F_threshold)
                    # Reduced by factor of 5 for much smaller visual circles
                    grav_radius = max(50.0, np.sqrt(gravity_strength * mass_all[i] / 1.0) / 5.0)
                    boundaries.append((float(x_all[i]), float(y_all[i]), float(grav_radius)))
            
            return boundaries
            
        except Exception:
            return []
    
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
