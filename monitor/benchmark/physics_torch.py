"""PyTorch-based GPU physics engine for particle simulation."""


def run_particle_physics_torch(gpu_arrays, params, torch):
    """
    Run one physics step for particle simulation using PyTorch.
    
    Args:
        gpu_arrays: Dictionary of PyTorch GPU tensors (x, y, vx, vy, mass, radius, active, etc.)
        params: Dictionary with physics parameters:
            - dt: Time step (default 0.016)
            - gravity_strength: Gravitational constant
            - small_ball_speed: Speed for small balls
            - initial_balls: Target number of small balls to spawn
            - max_balls_cap: Hard limit on small balls
            - split_enabled: Whether splitting is enabled
            - active_count: Current number of active particles
            - small_ball_count: Current number of small balls
            - drop_timer: Timer for spawning small balls
        torch: PyTorch module
        
    Returns:
        Dictionary with updated counters:
            - active_count
            - small_ball_count
            - drop_timer
            - split_enabled
    """
    # Extract arrays
    x = gpu_arrays['x']
    y = gpu_arrays['y']
    vx = gpu_arrays['vx']
    vy = gpu_arrays['vy']
    mass = gpu_arrays['mass']
    radius = gpu_arrays['radius']
    active = gpu_arrays['active']
    bounce_cooldown = gpu_arrays['bounce_cooldown']
    color_state = gpu_arrays['color_state']
    glow_intensity = gpu_arrays['glow_intensity']
    should_split = gpu_arrays['should_split']
    split_cooldown = gpu_arrays['split_cooldown']
    ball_color = gpu_arrays['ball_color']
    
    # Extract parameters
    dt = params.get('dt', 0.016)
    G = params['gravity_strength']
    small_ball_speed = params['small_ball_speed']
    initial_balls = int(params['initial_balls'])
    max_balls_cap = int(params['max_balls_cap'])
    split_enabled = params['split_enabled']
    
    # Recalculate active_count from actual active array (in case balls were spawned externally)
    old_active_count = params.get('active_count', 0)
    active_count = int(torch.sum(active).item())
    small_ball_count = int(torch.sum((mass < 100.0) & active).item())
    big_ball_count = active_count - small_ball_count
    drop_timer = params['drop_timer']
    
    # Drop small balls until initial_balls reached
    if small_ball_count < initial_balls:
        if drop_timer <= 0:
            # Find inactive slots that are NOT big balls (mass < 1000)
            inactive_and_small = ~active & (mass < 1000.0)
            inactive_indices = torch.where(inactive_and_small)[0]
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
                active_count += 1
                small_ball_count += 1
                drop_timer = 0.3
        else:
            drop_timer -= dt
    
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
        split_cooldown_act = split_cooldown[active_mask]
        
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
        
        # Apply gravity force from big balls to small balls (all N×M pairs)
        small_balls_mask = ~big_balls
        if torch.any(small_balls_mask) and torch.any(big_balls):
            small_indices = torch.where(small_balls_mask)[0]
            big_indices = torch.where(big_balls)[0]
            
            if len(small_indices) > 0 and len(big_indices) > 0:
                # Get positions
                x_small = x_act[small_indices]
                y_small = y_act[small_indices]
                x_big = x_act[big_indices]
                y_big = y_act[big_indices]
                mass_big = mass_act[big_indices]
                
                # N_small × N_big distance matrices
                dx_matrix = x_big[None, :] - x_small[:, None]  # [small, big]
                dy_matrix = y_big[None, :] - y_small[:, None]
                r2_matrix = dx_matrix**2 + dy_matrix**2 + 10.0
                r_matrix = torch.sqrt(r2_matrix)
                
                # Force from each big ball on each small ball
                force_matrix = G * mass_big[None, :] / (r2_matrix + 1.0)
                
                # Sum forces from all big balls on each small ball
                ax_small = torch.sum(force_matrix * dx_matrix / (r_matrix + 1e-10), dim=1)
                ay_small = torch.sum(force_matrix * dy_matrix / (r_matrix + 1e-10), dim=1)
                
                ax[small_indices] = ax_small
                ay[small_indices] = ay_small
        
        # Update velocities - apply acceleration to ALL particles now
        vx_act = vx_act + ax * dt
        vy_act = vy_act + ay * dt
        
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
            
            # Copy big ball color to small ball permanently (VECTORIZED - GPU only)
            ball_color_act = ball_color[active_mask]
            # Vectorized color copying - use advanced indexing on GPU
            # For small_i collisions: copy color from j to i
            small_i_indices = collision_i[small_i]
            small_i_sources = collision_j[small_i]
            if len(small_i_indices) > 0:
                ball_color_act[small_i_indices] = ball_color_act[small_i_sources]
            
            # For small_j collisions: copy color from i to j
            small_j_indices = collision_j[small_j]
            small_j_sources = collision_i[small_j]
            if len(small_j_indices) > 0:
                ball_color_act[small_j_indices] = ball_color_act[small_j_sources]
            
            ball_color[active_mask] = ball_color_act
            
            color_state_act = color_state[active_mask]
            color_state_act[collision_i] = torch.where(small_i, torch.ones_like(color_state_act[collision_i]), color_state_act[collision_i])
            color_state_act[collision_j] = torch.where(small_j, torch.ones_like(color_state_act[collision_j]), color_state_act[collision_j])
            color_state[active_mask] = color_state_act
            
            # Mark ALL colliding small balls for splitting (controlled by toggle)
            if split_enabled:
                should_split_act = should_split[active_mask]
                is_small_i = mass_act[collision_i] < 100.0
                is_small_j = mass_act[collision_j] < 100.0
                can_split_i = split_cooldown_act[collision_i] <= 0.0
                can_split_j = split_cooldown_act[collision_j] <= 0.0
                # Split if: small ball + off cooldown
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
    if split_enabled and active_count < 50000:
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
                        
                        # Child 1
                        x[child1_idx] = x[parent_idx] + torch.randn(1, device=x.device) * 10
                        y[child1_idx] = y[parent_idx] + torch.randn(1, device=x.device) * 10
                        angle1 = torch.rand(1, device=x.device) * 2 * 3.14159
                        vx[child1_idx] = torch.cos(angle1) * small_ball_speed
                        vy[child1_idx] = torch.sin(angle1) * small_ball_speed
                        mass[child1_idx] = 1.0
                        radius[child1_idx] = 8.0
                        active[child1_idx] = True
                        split_cooldown[child1_idx] = 5.0
                        ball_color[child1_idx] = ball_color[parent_idx]  # Inherit parent color
                        
                        # Child 2
                        x[child2_idx] = x[parent_idx] + torch.randn(1, device=x.device) * 10
                        y[child2_idx] = y[parent_idx] + torch.randn(1, device=x.device) * 10
                        angle2 = torch.rand(1, device=x.device) * 2 * 3.14159
                        vx[child2_idx] = torch.cos(angle2) * small_ball_speed
                        vy[child2_idx] = torch.sin(angle2) * small_ball_speed
                        mass[child2_idx] = 1.0
                        radius[child2_idx] = 8.0
                        active[child2_idx] = True
                        split_cooldown[child2_idx] = 5.0
                        ball_color[child2_idx] = ball_color[parent_idx]  # Inherit parent color
                        
                        # Set parent cooldown
                        split_cooldown[parent_idx] = 5.0
                        
                        active_count += 2
                        small_ball_count += 2
            
            # Clear split flags
            should_split[split_indices] = False
    
    # Enforce max_balls_cap by removing excess balls
    if small_ball_count > max_balls_cap:
        excess = small_ball_count - max_balls_cap
        small_balls = (mass < 100.0) & active
        small_indices = torch.where(small_balls)[0]
        if len(small_indices) > max_balls_cap:
            remove_indices = small_indices[max_balls_cap:]
            active[remove_indices] = False
            active_count -= len(remove_indices)
            small_ball_count = max_balls_cap
    
    elif active_count >= 50000:
        # Safety shutdown
        print(f"\n[SAFETY] Particle count reached {active_count} - disabling splitting")
        split_enabled = False
    
    # Update GPU arrays
    gpu_arrays['x'] = x
    gpu_arrays['y'] = y
    gpu_arrays['vx'] = vx
    gpu_arrays['vy'] = vy
    gpu_arrays['bounce_cooldown'] = bounce_cooldown
    gpu_arrays['color_state'] = color_state
    gpu_arrays['glow_intensity'] = glow_intensity
    gpu_arrays['should_split'] = should_split
    gpu_arrays['split_cooldown'] = split_cooldown
    gpu_arrays['ball_color'] = ball_color
    
    # Return updated counters
    return {
        'active_count': active_count,
        'small_ball_count': small_ball_count,
        'drop_timer': drop_timer,
        'split_enabled': split_enabled
    }
