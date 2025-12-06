"""Utility functions for particle sampling and visualization."""

import numpy as np


def get_particle_sample(gpu_arrays, method, max_samples=2000):
    """
    Get a sampled subset of ACTIVE particle positions, masses, colors, and glow for visualization.
    
    Args:
        gpu_arrays: Dictionary of GPU arrays (CuPy or PyTorch)
        method: 'cupy' or 'torch'
        max_samples: Maximum number of particles to return
        
    Returns:
        tuple of (positions, masses, colors, glows) or (None, None, None, None) if not available
        positions: numpy array of shape (N, 2) with [x, y]
        masses: numpy array of shape (N,) with particle masses
        colors: numpy array of shape (N, 3) with RGB colors (0-1 range)
        glows: numpy array of shape (N,) with glow intensity (0-1)
    """
    try:
        x = gpu_arrays.get('x')
        y = gpu_arrays.get('y')
        mass = gpu_arrays.get('mass')
        active = gpu_arrays.get('active')
        color_state = gpu_arrays.get('color_state')
        glow_intensity = gpu_arrays.get('glow_intensity')
        ball_color = gpu_arrays.get('ball_color')
        
        if x is None or y is None or mass is None or active is None:
            return None, None, None, None
        
        if method == 'cupy':
            # Get only active particles
            active_mask = active.get()  # Transfer to CPU
            x_all = x.get()
            y_all = y.get()
            mass_all = mass.get()
            color_all = color_state.get() if color_state is not None else np.zeros(len(active_mask))
            glow_all = glow_intensity.get() if glow_intensity is not None else np.zeros(len(active_mask))
            ball_color_all = ball_color.get() if ball_color is not None else np.zeros((len(active_mask), 3))
            
            x_active = x_all[active_mask]
            y_active = y_all[active_mask]
            mass_active = mass_all[active_mask]
            color_active = color_all[active_mask]
            glow_active = glow_all[active_mask]
            ball_color_active = ball_color_all[active_mask]
            
        elif method == 'torch':
            active_mask = active.cpu().numpy()
            x_all = x.cpu().numpy()
            y_all = y.cpu().numpy()
            mass_all = mass.cpu().numpy()
            color_all = color_state.cpu().numpy() if color_state is not None else np.zeros(len(active_mask))
            glow_all = glow_intensity.cpu().numpy() if glow_intensity is not None else np.zeros(len(active_mask))
            ball_color_all = ball_color.cpu().numpy() if ball_color is not None else np.zeros((len(active_mask), 3))
            
            x_active = x_all[active_mask]
            y_active = y_all[active_mask]
            mass_active = mass_all[active_mask]
            color_active = color_all[active_mask]
            glow_active = glow_all[active_mask]
            ball_color_active = ball_color_all[active_mask]
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
            ball_color_active = ball_color_active[::step]
        
        # Stack into Nx2 array
        positions = np.column_stack([x_active, y_active])
        return positions, mass_active, ball_color_active, glow_active
        
    except Exception:
        return None, None, None, None


def get_influence_boundaries(gpu_arrays, method, gravity_strength=500.0):
    """
    Get positions of large bodies with gravity radius based on actual force strength.
    Radius shows where gravitational force drops to visible threshold.
    
    Args:
        gpu_arrays: Dictionary of GPU arrays (CuPy or PyTorch)
        method: 'cupy' or 'torch'
        gravity_strength: Current gravity constant
        
    Returns:
        list of (x, y, radius) tuples for large bodies, or empty list
    """
    try:
        x = gpu_arrays.get('x')
        y = gpu_arrays.get('y')
        mass = gpu_arrays.get('mass')
        active = gpu_arrays.get('active')
        
        if x is None or y is None or mass is None or active is None:
            return []
        
        if method == 'cupy':
            x_all = x.get()
            y_all = y.get()
            mass_all = mass.get()
            active_mask = active.get()
        elif method == 'torch':
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
