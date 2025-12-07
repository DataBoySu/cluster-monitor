"""UI component rendering for particle visualizer."""


def draw_stats(screen, font, window_size, stats_data):
    """
    Draw statistics overlay.
    
    Args:
        screen: Pygame screen surface
        font: Pygame font object
        window_size: Tuple of (width, height)
        stats_data: Dict with keys: total_particles, active_particles, rendered_particles,
                    fps, gpu_util, elapsed_time
    """
    backend_mult = stats_data.get('backend_multiplier', 1)
    total_computed = stats_data['total_particles'] * backend_mult
    
    stats = [
        f"Screen: {stats_data['rendered_particles']:,} particles",
        f"Visual Sim: {stats_data['active_particles']:,} / {stats_data['total_particles']:,} particles",
        f"Backend: {backend_mult}x multiplier",
        f"Total Computed: {total_computed:,} particles",
        f"FPS: {stats_data['fps']:.1f}",
        f"GPU Util: {stats_data['gpu_util']:.0f}%",
        f"Time: {stats_data['elapsed_time']:.1f}s"
    ]
    
    y_offset = 15
    for text in stats:
        # Draw shadow
        shadow = font.render(text, True, (0, 0, 0))
        screen.blit(shadow, (17, y_offset + 2))
        
        # Draw text
        rendered = font.render(text, True, (255, 255, 255))
        screen.blit(rendered, (15, y_offset))
        y_offset += 30
    
    # Draw controls hint
    hint = font.render("Press ESC to stop", True, (150, 150, 150))
    screen.blit(hint, (15, window_size[1] - 40))


def draw_sliders(pygame, screen, small_font, sliders, dragging_slider):
    """Draw interactive sliders for real-time control with filled bar style."""
    import math
    
    for key, slider in sliders.items():
        x, y = slider['pos']
        width = slider['width']
        
        # Draw track background (dark)
        pygame.draw.rect(screen, (60, 60, 80), (x, y, width, 20), border_radius=10)
        
        # Calculate handle position
        normalized = (slider['value'] - slider['min']) / (slider['max'] - slider['min'])
        handle_x = x + int(normalized * width)
        
        # Draw filled portion (cyan/blue gradient)
        if normalized > 0:
            pygame.draw.rect(screen, (80, 120, 200), (x, y, handle_x - x, 20), border_radius=10)
        
        # Draw handle (white circle)
        pygame.draw.circle(screen, (150, 180, 255), (handle_x, y + 10), 12)
        pygame.draw.circle(screen, (200, 220, 255), (handle_x, y + 10), 8)
        
        # Draw label and value
        display_val = slider['value']
        if math.isnan(display_val) or math.isinf(display_val):
            display_val = slider['min']
        
        if slider.get('is_int', False):
            label = small_font.render(f"{slider['label']}: {int(display_val)}", True, (200, 200, 200))
        else:
            label = small_font.render(f"{slider['label']}: {display_val:.1f}", True, (200, 200, 200))
        
        screen.blit(label, (x, y - 25))


def draw_text_input(pygame, screen, font, small_font, text_input_data):
    """Draw text input box for max balls cap."""
    x, y = text_input_data['pos']
    width, height = text_input_data['width'], text_input_data['height']
    
    # Draw box
    color = (100, 200, 255) if text_input_data['active'] else (60, 60, 80)
    pygame.draw.rect(screen, color, (x, y, width, height), 2)
    pygame.draw.rect(screen, (30, 30, 40), (x + 2, y + 2, width - 4, height - 4))
    
    # Draw label
    label = small_font.render(text_input_data['label'], True, (200, 200, 200))
    screen.blit(label, (x, y - 20))
    
    # Draw value
    value_text = font.render(text_input_data['value'] or '0', True, (255, 255, 255))
    screen.blit(value_text, (x + 5, y + 5))


def draw_multiplier_button(pygame, screen, font, button_data):
    """Draw multiplier button."""
    x, y = button_data['pos']
    width, height = button_data['width'], button_data['height']
    
    # Draw button
    pygame.draw.rect(screen, (80, 120, 180), (x, y, width, height))
    pygame.draw.rect(screen, (120, 160, 220), (x, y, width, height), 2)
    
    # Draw label
    label = font.render(button_data['label'], True, (255, 255, 255))
    label_rect = label.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(label, label_rect)


def draw_toggle_button(pygame, screen, font, button_data, enabled):
    """Draw toggle button."""
    x, y = button_data['pos']
    width, height = button_data['width'], button_data['height']
    
    # Draw button with state-dependent color
    color = (180, 80, 80) if enabled else (80, 80, 120)
    pygame.draw.rect(screen, color, (x, y, width, height))
    pygame.draw.rect(screen, (200, 100, 100) if enabled else (120, 120, 160), (x, y, width, height), 2)
    
    # Draw label
    label_text = "Ball Splitting: ON" if enabled else "Ball Splitting: OFF"
    label = font.render(label_text, True, (255, 255, 255))
    label_rect = label.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(label, label_rect)
