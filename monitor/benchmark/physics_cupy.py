"""CuPy-based GPU physics engine for particle simulation."""

def run_particle_physics_cupy(gpu_arrays, params, cp):
    """
    Run one frame of particle physics using CuPy.
    
    Args:
        gpu_arrays: Dictionary containing all GPU arrays
        params: Dictionary with physics parameters (gravity_strength, small_ball_speed, etc.)
        cp: CuPy module reference
        
    Returns:
        Updated counters (active_count, small_ball_count, drop_timer)
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
    dt = 0.016
    G = params['gravity_strength']
    small_ball_speed = params['small_ball_speed']
    initial_balls = int(params['initial_balls'])
    max_balls_cap = int(params['max_balls_cap'])
    split_enabled = params['split_enabled']
    active_count = params['active_count']
    small_ball_count = params['small_ball_count']
    drop_timer = params['drop_timer']
    
    # Drop small balls continuously until we reach initial_balls count
    if small_ball_count < initial_balls:
        if drop_timer <= 0:
            inactive_indices = cp.where(~active)[0]
            if len(inactive_indices) > 0:
                idx = int(inactive_indices[0])
                x[idx] = 500.0
                y[idx] = 50.0
                vx[idx] = (cp.random.rand() - 0.5) * small_ball_speed * 0.2
                vy[idx] = small_ball_speed
                mass[idx] = 1.0
                radius[idx] = 8.0
                active[idx] = True
                ball_color[idx] = cp.array([1.0, 1.0, 1.0], dtype=cp.float32)  # White initially
                active_count += 1
                small_ball_count += 1
                drop_timer = 0.3
        else:
            drop_timer -= dt
    
    # Process active particles
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
        
        # Gravity between big balls - N×N computation
        if cp.any(big_balls):
            big_indices = cp.where(big_balls)[0]
            n_big = len(big_indices)
            
            if n_big > 1:
                x_big = x_act[big_indices]
                y_big = y_act[big_indices]
                mass_big = mass_act[big_indices]
                
                # Distance matrices
                dx_matrix = x_big[:, cp.newaxis] - x_big[cp.newaxis, :]
                dy_matrix = y_big[:, cp.newaxis] - y_big[cp.newaxis, :]
                r2_matrix = dx_matrix**2 + dy_matrix**2 + 10.0
                r_matrix = cp.sqrt(r2_matrix)
                
                # Force matrix
                force_matrix = G * mass_big[cp.newaxis, :] / (r2_matrix + 1.0)
                cp.fill_diagonal(force_matrix, 0.0)
                
                # Acceleration
                ax_big = cp.sum(force_matrix * dx_matrix / (r_matrix + 1e-10), axis=1)
                ay_big = cp.sum(force_matrix * dy_matrix / (r_matrix + 1e-10), axis=1)
                
                ax[big_indices] = ax_big
                ay[big_indices] = ay_big
        
        # Apply gravity force from big balls to small balls (all N×M pairs)
        small_balls_mask = ~big_balls
        if cp.any(small_balls_mask) and cp.any(big_balls):
            small_indices = cp.where(small_balls_mask)[0]
            big_indices = cp.where(big_balls)[0]
            
            if len(small_indices) > 0 and len(big_indices) > 0:
                # Get positions
                x_small = x_act[small_indices]
                y_small = y_act[small_indices]
                x_big = x_act[big_indices]
                y_big = y_act[big_indices]
                mass_big = mass_act[big_indices]
                
                # N_small × N_big distance matrices
                dx_matrix = x_big[cp.newaxis, :] - x_small[:, cp.newaxis]  # [small, big]
                dy_matrix = y_big[cp.newaxis, :] - y_small[:, cp.newaxis]
                r2_matrix = dx_matrix**2 + dy_matrix**2 + 10.0
                r_matrix = cp.sqrt(r2_matrix)
                
                # Force from each big ball on each small ball
                force_matrix = G * mass_big[cp.newaxis, :] / (r2_matrix + 1.0)
                
                # Sum forces from all big balls on each small ball
                ax_small = cp.sum(force_matrix * dx_matrix / (r_matrix + 1e-10), axis=1)
                ay_small = cp.sum(force_matrix * dy_matrix / (r_matrix + 1e-10), axis=1)
                
                ax[small_indices] = ax_small
                ay[small_indices] = ay_small
        
        # Update velocities - apply acceleration to ALL particles now
        vx_act = vx_act + ax * dt
        vy_act = vy_act + ay * dt
        
        # Normalize small ball velocities
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
        hit_left = (x_act < radius_act) & (vx_act < 0) & (cooldown_act == 0)
        hit_right = (x_act > 1000 - radius_act) & (vx_act > 0) & (cooldown_act == 0)
        vx_act = cp.where(hit_left | hit_right, -vx_act, vx_act)
        x_act = cp.where(hit_left, radius_act, x_act)
        x_act = cp.where(hit_right, 1000 - radius_act, x_act)
        cooldown_act = cp.where(hit_left | hit_right, 0.1, cooldown_act)
        
        # Top/bottom walls
        hit_top = (y_act < radius_act) & (vy_act < 0) & (cooldown_act == 0)
        hit_bottom = (y_act > 800 - radius_act) & (vy_act > 0) & (cooldown_act == 0)
        vy_act = cp.where(hit_top | hit_bottom, -vy_act, vy_act)
        y_act = cp.where(hit_top, radius_act, y_act)
        y_act = cp.where(hit_bottom, 800 - radius_act, y_act)
        cooldown_act = cp.where(hit_top | hit_bottom, 0.1, cooldown_act)
        
        # Particle-particle collisions
        if n_active > 1:
            # Distance matrix
            dx_matrix = x_act[:, cp.newaxis] - x_act[cp.newaxis, :]
            dy_matrix = y_act[:, cp.newaxis] - y_act[cp.newaxis, :]
            dist_matrix = cp.sqrt(dx_matrix**2 + dy_matrix**2 + 1e-10)
            
            # Collision detection
            ri = radius_act[:, cp.newaxis]
            rj = radius_act[cp.newaxis, :]
            collision_matrix = (dist_matrix < ri + rj) & (dist_matrix > 0.1)
            
            collision_i, collision_j = cp.where(collision_matrix)
            # Keep only unique pairs where i < j to avoid double-processing
            mask = collision_i < collision_j
            collision_i = collision_i[mask]
            collision_j = collision_j[mask]
            
            if len(collision_i) > 0:
                # Get collision parameters
                dist_col = dist_matrix[collision_i, collision_j]
                ri = radius_act[collision_i]
                rj = radius_act[collision_j]
                mi = mass_act[collision_i]
                mj = mass_act[collision_j]
                
                # Normal vectors
                nx = dx_matrix[collision_i, collision_j] / dist_col
                ny = dy_matrix[collision_i, collision_j] / dist_col
                
                # Relative velocity
                vxi = vx_act[collision_i]
                vxj = vx_act[collision_j]
                vyi = vy_act[collision_i]
                vyj = vy_act[collision_j]
                dvx = vxj - vxi
                dvy = vyj - vyi
                dot = dvx * nx + dvy * ny
                
                approaching = dot < 0
                
                # Elastic collision with slight damping for big balls
                total_mass = mi + mj
                big_i = mass_act[collision_i] >= 100.0
                big_j = mass_act[collision_j] >= 100.0
                restitution = cp.where(big_i | big_j, 0.95, 1.0)
                
                impulse_factor_i = 2.0 * mj / (total_mass + 1e-10) * restitution
                impulse_factor_j = 2.0 * mi / (total_mass + 1e-10) * restitution
                
                impulse_i_x = cp.where(approaching, impulse_factor_i * dot * nx, 0.0)
                impulse_i_y = cp.where(approaching, impulse_factor_i * dot * ny, 0.0)
                impulse_j_x = cp.where(approaching, -impulse_factor_j * dot * nx, 0.0)
                impulse_j_y = cp.where(approaching, -impulse_factor_j * dot * ny, 0.0)
                
                cp.add.at(vx_act, collision_i, impulse_i_x)
                cp.add.at(vy_act, collision_i, impulse_i_y)
                cp.add.at(vx_act, collision_j, impulse_j_x)
                cp.add.at(vy_act, collision_j, impulse_j_y)
                
                # Copy big ball colors to small balls on collision (VECTORIZED - GPU only)
                # Note: ensure CuPy arrays are on the same device and shapes align;
                # mismatched shapes will raise an exception during advanced indexing.
                big_balls_array = mass_act >= 100.0
                small_i = ~big_balls_array[collision_i] & big_balls_array[collision_j]
                small_j = ~big_balls_array[collision_j] & big_balls_array[collision_i]
                
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
                
                # Set color state for visual effect
                color_state_act = color_state[active_mask]
                color_state_act[collision_i] = cp.where(small_i, 1.0, color_state_act[collision_i])
                color_state_act[collision_j] = cp.where(small_j, 1.0, color_state_act[collision_j])
                color_state[active_mask] = color_state_act
                
                # Mark for splitting
                if split_enabled:
                    should_split_act = should_split[active_mask]
                    is_small_i = mass_act[collision_i] < 100.0
                    is_small_j = mass_act[collision_j] < 100.0
                    can_split_i = split_cooldown_act[collision_i] <= 0.0
                    can_split_j = split_cooldown_act[collision_j] <= 0.0
                    should_split_act[collision_i] = cp.where(is_small_i & can_split_i, True, should_split_act[collision_i])
                    should_split_act[collision_j] = cp.where(is_small_j & can_split_j, True, should_split_act[collision_j])
                    should_split[active_mask] = should_split_act
                
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
        
        # GPU-compute glow
        speed = cp.sqrt(vx_act**2 + vy_act**2)
        glow_act = cp.minimum(1.0, speed / 500.0)
        glow_intensity[active_mask] = glow_act
        
        # Fade color state
        color_state_act = cp.maximum(0.0, color_state[active_mask] - dt * 2.0)
        color_state[active_mask] = color_state_act
        
        # Decay split cooldown
        split_cooldown_act = cp.maximum(0.0, split_cooldown_act - dt)
        split_cooldown[active_mask] = split_cooldown_act
    
    # Spawn children from splitting
    if split_enabled and active_count < 50000:
        split_indices = cp.where(should_split & active)[0]
        if len(split_indices) > 0:
            inactive_indices = cp.where(~active)[0]
            spawn_count = min(len(split_indices) * 2, len(inactive_indices), 1000)
            
            if spawn_count > 0:
                for idx, parent_idx in enumerate(split_indices[:spawn_count // 2]):
                    if idx * 2 + 1 < len(inactive_indices):
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
                        split_cooldown[child1_idx] = 5.0
                        ball_color[child1_idx] = ball_color[parent_idx]
                        
                        # Child 2
                        x[child2_idx] = x[parent_idx] + cp.random.uniform(-10, 10)
                        y[child2_idx] = y[parent_idx] + cp.random.uniform(-10, 10)
                        angle2 = cp.random.uniform(0, 2 * cp.pi)
                        vx[child2_idx] = cp.cos(angle2) * small_ball_speed
                        vy[child2_idx] = cp.sin(angle2) * small_ball_speed
                        mass[child2_idx] = 1.0
                        radius[child2_idx] = 8.0
                        active[child2_idx] = True
                        split_cooldown[child2_idx] = 5.0
                        ball_color[child2_idx] = ball_color[parent_idx]
                        
                        split_cooldown[parent_idx] = 5.0
                        
                        active_count += 2
                        small_ball_count += 2
            
            should_split[split_indices] = False
    
    # Enforce max cap
    if small_ball_count > max_balls_cap:
        small_balls = (mass < 100.0) & active
        small_indices = cp.where(small_balls)[0]
        if len(small_indices) > max_balls_cap:
            remove_indices = small_indices[max_balls_cap:]
            active[remove_indices] = False
            active_count -= len(remove_indices)
            small_ball_count = max_balls_cap
    elif active_count >= 50000:
        print(f"\n[SAFETY] Particle count reached {active_count} - disabling splitting")
        split_enabled = False
    
    # Write back arrays
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
    
    return {
        'active_count': active_count,
        'small_ball_count': small_ball_count,
        'drop_timer': drop_timer,
        'split_enabled': split_enabled
    }
