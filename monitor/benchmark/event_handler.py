"""Event handling for particle visualizer UI."""


def handle_events(visualizer, pygame_events):
    """
    Process pygame events for visualizer.
    
    Args:
        visualizer: ParticleVisualizer instance
        pygame_events: List of pygame events
        
    Returns:
        bool: True if should continue running, False to stop
    """
    # Check if we have a valid visualizer and pygame
    if not visualizer or not hasattr(visualizer, 'pygame') or not visualizer.pygame:
        return True  # Continue running if visualizer not ready
    
    for event in pygame_events:
        if event.type == visualizer.pygame.QUIT:
            return False
        
        elif event.type == visualizer.pygame.KEYDOWN:
            if event.key == visualizer.pygame.K_ESCAPE:
                return False
            elif visualizer.max_balls_cap['active']:
                if not _handle_text_input(visualizer, event):
                    continue
        
        elif event.type == visualizer.pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                _handle_mouse_click(visualizer, event.pos)
        
        elif event.type == visualizer.pygame.MOUSEBUTTONUP:
            if event.button == 1:
                visualizer.dragging_slider = None
        
        elif event.type == visualizer.pygame.MOUSEMOTION:
            if visualizer.dragging_slider:
                visualizer._handle_slider_drag(event.pos)
    
    return True


def _handle_text_input(visualizer, event):
    """Handle keyboard input for max balls cap text field."""
    if event.key == visualizer.pygame.K_RETURN:
        # Validate: max_balls_cap must be >= initial_balls
        try:
            max_cap = int(visualizer.max_balls_cap['value']) if visualizer.max_balls_cap['value'] else 1
            initial = int(visualizer.sliders['initial_balls']['value']) if 'initial_balls' in visualizer.sliders else 1
            if max_cap < initial:
                visualizer.max_balls_cap['value'] = str(initial)
        except ValueError:
            visualizer.max_balls_cap['value'] = '100000'
        visualizer.max_balls_cap['active'] = False
    
    elif event.key == visualizer.pygame.K_BACKSPACE:
        visualizer.max_balls_cap['value'] = visualizer.max_balls_cap['value'][:-1]
    
    elif event.unicode.isdigit():
        current = visualizer.max_balls_cap['value'] + event.unicode
        if len(current) <= 6:  # Max 999999
            visualizer.max_balls_cap['value'] = current
    
    return True


def _handle_mouse_click(visualizer, pos):
    """Handle mouse click events."""
    # Check text input
    tx, ty = visualizer.max_balls_cap['pos']
    tw, th = visualizer.max_balls_cap['width'], visualizer.max_balls_cap['height']
    text_input_clicked = (tx <= pos[0] <= tx + tw and ty <= pos[1] <= ty + th)
    
    if text_input_clicked:
        visualizer.max_balls_cap['active'] = True
        return
    
    visualizer.max_balls_cap['active'] = False
    
    # Check multiplier button
    mx, my = visualizer.multiplier_button['pos']
    mw, mh = visualizer.multiplier_button['width'], visualizer.multiplier_button['height']
    if mx <= pos[0] <= mx + mw and my <= pos[1] <= my + mh:
        _handle_multiplier_cycle(visualizer)
        return
    
    # Check split toggle button
    bx, by = visualizer.split_button['pos']
    bw, bh = visualizer.split_button['width'], visualizer.split_button['height']
    if bx <= pos[0] <= bx + bw and by <= pos[1] <= by + bh:
        visualizer.split_enabled = not visualizer.split_enabled
        visualizer.split_button['label'] = f"Ball Splitting: {'ON' if visualizer.split_enabled else 'OFF'}"
        return
    
    # Check sliders
    for key, slider in visualizer.sliders.items():
        sx, sy = slider['pos']
        width = slider['width']
        if sx <= pos[0] <= sx + width and sy - 12 <= pos[1] <= sy + 32:
            visualizer._handle_slider_click(pos)
            return
    
    # Spawn big ball(s) at click position
    _handle_particle_spawn(visualizer, pos)


def _handle_multiplier_cycle(visualizer):
    """Cycle through multiplier levels."""
    import math
    
    old_multiplier = visualizer.slider_multiplier
    current_idx = visualizer.multiplier_levels.index(visualizer.slider_multiplier)
    next_idx = (current_idx + 1) % len(visualizer.multiplier_levels)
    visualizer.slider_multiplier = visualizer.multiplier_levels[next_idx]
    visualizer.multiplier_button['label'] = f'x{visualizer.slider_multiplier}'
    
    # Rescale initial_balls slider proportionally
    if old_multiplier > 0:
        multiplier_ratio = visualizer.slider_multiplier / old_multiplier
        if 'initial_balls' in visualizer.sliders:
            slider = visualizer.sliders['initial_balls']
            new_value = slider['value'] * multiplier_ratio
            new_max = slider['base_max'] * visualizer.slider_multiplier
            if not math.isnan(new_value) and not math.isinf(new_value):
                slider['value'] = new_value
                slider['max'] = new_max


def _handle_particle_spawn(visualizer, pos):
    """Handle spawning particles at click position."""
    click_x, click_y = pos
    
    # Convert screen coords to simulation coords (1000x800 space)
    scale_x = 1000.0 / visualizer.window_size[0]
    scale_y = 800.0 / visualizer.window_size[1]
    sim_x = click_x * scale_x
    sim_y = click_y * scale_y
    
    num_to_spawn = visualizer.slider_multiplier
    
    if not hasattr(visualizer, 'spawn_requests'):
        visualizer.spawn_requests = []
    visualizer.spawn_requests.append((sim_x, sim_y, num_to_spawn))
