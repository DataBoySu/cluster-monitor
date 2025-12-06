"""GPU Particle Simulation Visualizer.

Renders a sampled subset of particles for visual feedback during benchmarking.
GPU computes millions, screen renders thousands for smooth 60 FPS display.
"""

import time
import random
from typing import Optional, Tuple, List
import numpy as np


class ParticleVisualizer:
    """Pygame-based particle visualization for benchmarking."""
    
    def __init__(self, window_size: Tuple[int, int] = (1200, 800), max_render_particles: int = 2000):
        """
        Initialize visualizer.
        
        Args:
            window_size: (width, height) of pygame window
            max_render_particles: Maximum particles to render (for performance)
        """
        self.window_size = window_size
        self.max_render_particles = max_render_particles
        self.running = False
        self.pygame = None
        self.screen = None
        self.clock = None
        self.font = None
        self.small_font = None
        self.colors = []
        self.particle_sizes = []
        
        # UI Sliders with multiplier system
        self.slider_multiplier = 1  # x1, x10, x100, x1000
        self.multiplier_levels = [1, 10, 100, 1000]
        self.multiplier_button = {
            'pos': (920, 700),
            'width': 80,
            'height': 30,
            'label': 'x1'
        }
        self.sliders = {
            'gravity': {'value': 500.0, 'min': 0.0, 'max': 10000.0, 'pos': (50, 700), 'width': 220, 'label': 'Big Ball Gravity'},
            'small_ball_speed': {'value': 300.0, 'min': 50.0, 'max': 600.0, 'pos': (300, 700), 'width': 220, 'label': 'Small Ball Speed'},
            'initial_balls': {'value': 1.0, 'min': 1.0, 'max': 10.0, 'pos': (550, 700), 'width': 220, 'label': 'Initial Balls', 'is_int': True, 'base_max': 10.0},
        }
        self.dragging_slider = None
        
        # Text input box for max balls cap (hard limit)
        self.max_balls_cap = {
            'pos': (800, 700),
            'width': 100,
            'height': 30,
            'value': '100000',
            'active': False,
            'label': 'Max Cap'
        }
        
        # Toggle button for ball splitting
        self.split_enabled = False  # Start disabled for safety
        self.split_button = {
            'pos': (1020, 700),
            'width': 160,
            'height': 30,
            'label': 'Ball Splitting: OFF'
        }
        
        self._init_pygame()
    
    def _init_pygame(self):
        """Initialize pygame (optional dependency)."""
        try:
            import pygame
            self.pygame = pygame
            pygame.init()
            self.screen = pygame.display.set_mode(self.window_size)
            pygame.display.set_caption("GPU Particle Simulation - Benchmark Visualization")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 28)
            self.small_font = pygame.font.Font(None, 20)
            self.running = True
            
            # Pre-generate random colors and sizes for particles
            for _ in range(self.max_render_particles):
                # Vibrant random colors
                color = (
                    random.randint(100, 255),
                    random.randint(100, 255),
                    random.randint(100, 255)
                )
                self.colors.append(color)
                # Varying sizes for depth effect
                self.particle_sizes.append(random.randint(3, 8))
                
        except ImportError:
            self.running = False
            print("[WARNING] pygame not installed - visualization disabled")
            print("Install with: pip install pygame")
    
    def is_available(self) -> bool:
        """Check if visualizer is ready."""
        return self.running and self.pygame is not None
    
    def render_frame(
        self,
        positions: np.ndarray,
        masses: np.ndarray,
        colors: np.ndarray,
        glows: np.ndarray,
        influence_boundaries: list,
        total_particles: int,
        active_particles: int,
        fps: float = 0,
        gpu_util: float = 0,
        elapsed_time: float = 0
    ):
        """
        Render one frame with GPU-computed color and glow effects.
        
        Args:
            positions: Nx2 array of [x, y] positions
            masses: N array of particle masses
            colors: N array of color state (0-1, 0=normal, 1=just hit big ball)
            glows: N array of glow intensity (0-1, based on speed)
            influence_boundaries: List of (x, y, radius) for large bodies
            total_particles: Target particle count
            active_particles: Currently active count
            fps: Current FPS
            gpu_util: GPU utilization %
            elapsed_time: Benchmark elapsed time
        """
        if not self.is_available():
            return
        
        # Handle pygame events
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.running = False
                return
            elif event.type == self.pygame.KEYDOWN:
                if event.key == self.pygame.K_ESCAPE:
                    self.running = False
                    return
                elif self.max_balls_cap['active']:
                    # Handle text input for max cap
                    if event.key == self.pygame.K_RETURN:
                        # Validate: max_balls_cap must be >= initial_balls
                        try:
                            max_cap = int(self.max_balls_cap['value']) if self.max_balls_cap['value'] else 1
                            initial = int(self.sliders['initial_balls']['value']) if 'initial_balls' in self.sliders else 1
                            if max_cap < initial:
                                self.max_balls_cap['value'] = str(initial)  # Force to at least initial_balls
                        except ValueError:
                            self.max_balls_cap['value'] = '100000'
                        self.max_balls_cap['active'] = False
                    elif event.key == self.pygame.K_BACKSPACE:
                        self.max_balls_cap['value'] = self.max_balls_cap['value'][:-1]
                    elif event.unicode.isdigit():
                        # Limit to reasonable number
                        current = self.max_balls_cap['value'] + event.unicode
                        if len(current) <= 6:  # Max 999999
                            self.max_balls_cap['value'] = current
            elif event.type == self.pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check text input first but don't use continue
                    tx, ty = self.max_balls_cap['pos']
                    tw, th = self.max_balls_cap['width'], self.max_balls_cap['height']
                    text_input_clicked = (tx <= event.pos[0] <= tx + tw and ty <= event.pos[1] <= ty + th)
                    
                    if text_input_clicked:
                        self.max_balls_cap['active'] = True
                    elif self.max_balls_cap['active']:
                        self.max_balls_cap['active'] = False
                    
                    # Only check other UI if text input wasn't clicked
                    if not text_input_clicked:
                        # Check multiplier button
                        mx, my = self.multiplier_button['pos']
                        mw, mh = self.multiplier_button['width'], self.multiplier_button['height']
                        if mx <= event.pos[0] <= mx + mw and my <= event.pos[1] <= my + mh:
                            # Cycle multiplier: x1 -> x10 -> x100 -> x1000 -> x1
                            old_multiplier = self.slider_multiplier
                            current_idx = self.multiplier_levels.index(self.slider_multiplier)
                            next_idx = (current_idx + 1) % len(self.multiplier_levels)
                            self.slider_multiplier = self.multiplier_levels[next_idx]
                            self.multiplier_button['label'] = f'x{self.slider_multiplier}'
                            
                            # Rescale initial_balls slider proportionally
                            multiplier_ratio = self.slider_multiplier / old_multiplier
                            if 'initial_balls' in self.sliders:
                                slider = self.sliders['initial_balls']
                                slider['value'] = slider['value'] * multiplier_ratio
                                slider['max'] = slider['base_max'] * self.slider_multiplier
                        
                        # Check toggle button (split enable/disable)
                        bx, by = self.split_button['pos']
                        bw, bh = self.split_button['width'], self.split_button['height']
                        if bx <= event.pos[0] <= bx + bw and by <= event.pos[1] <= by + bh:
                            self.split_enabled = not self.split_enabled
                            self.split_button['label'] = f"Ball Splitting: {'ON' if self.split_enabled else 'OFF'}"
                        else:
                            # Check sliders
                            self._handle_slider_click(event.pos)
            elif event.type == self.pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_slider = None
            elif event.type == self.pygame.MOUSEMOTION:
                if self.dragging_slider:
                    self._handle_slider_drag(event.pos)
        
        # Clear screen with dark space background
        self.screen.fill((5, 5, 15))
        
        # Scale positions to screen coordinates
        scale_x = self.window_size[0] / 1000.0
        scale_y = self.window_size[1] / 800.0
        
        # Draw influence boundaries for large bodies (gravity field visualization)
        for bx, by, bradius in influence_boundaries:
            screen_x = int(bx * scale_x)
            screen_y = int(by * scale_y)
            screen_radius = max(10, int(bradius * min(scale_x, scale_y)))  # Minimum 10px radius
            
            # Draw gravity boundary (white line showing gravitational influence)
            if screen_radius > 5:  # Only draw if visible
                self.pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),  # WHITE - clear gravity boundary
                    (screen_x, screen_y),
                    screen_radius,
                    3  # Thicker line for visibility
                )
            
            # Also draw big ball physical boundary (thin inner circle)
            ball_radius = int(36 * min(scale_x, scale_y))
            self.pygame.draw.circle(
                self.screen,
                (200, 200, 200),  # Light gray for ball edge
                (screen_x, screen_y),
                ball_radius,
                1  # Thin line
            )
        
        # GPU-intensive effect: Motion blur/trails (requires more GPU texture operations)
        # Create a semi-transparent overlay to simulate motion blur
        blur_surface = self.pygame.Surface(self.window_size, self.pygame.SRCALPHA)
        blur_surface.fill((5, 5, 15, 8))  # Very transparent dark overlay
        self.screen.blit(blur_surface, (0, 0), special_flags=self.pygame.BLEND_RGBA_SUB)
        
        # Draw particles with GPU-computed colors and glow effects
        num_particles = len(positions)
        for i in range(num_particles):
            x = int(positions[i, 0] * scale_x)
            y = int(positions[i, 1] * scale_y)
            
            # Get GPU-computed values
            mass = masses[i]
            # colors is now RGB array (N, 3)
            if colors is not None and i < len(colors):
                if len(colors.shape) == 2 and colors.shape[1] == 3:
                    # RGB color from GPU
                    rgb = colors[i]
                    base_color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
                else:
                    # Fallback to old single-value color_state
                    color_state = colors[i]
                    base_color = (int(180 + 75 * color_state), int(180 - 180 * color_state), int(200 - 200 * color_state))
            else:
                base_color = (180, 180, 200)  # Default white
            
            glow_intensity = glows[i] if glows is not None and i < len(glows) else 0.0
            
            # Determine size by mass
            if mass >= 1000:  # Big balls
                radius = 36
            else:  # Small balls
                radius = 8
            
            # Calculate glow based on base color
            base_glow = (
                min(255, int(base_color[0] * 1.3)),
                min(255, int(base_color[1] * 1.3)),
                min(255, int(base_color[2] * 1.3))
            )
            
            # Amplify glow based on speed (GPU-computed)
            glow_radius = radius + int(3 + 5 * glow_intensity)
            glow_r = min(255, int(base_glow[0] * (0.8 + 0.4 * glow_intensity)))
            glow_g = min(255, int(base_glow[1] * (0.8 + 0.4 * glow_intensity)))
            glow_b = min(255, int(base_glow[2] * (0.8 + 0.4 * glow_intensity)))
            
            # Draw with dynamic glow
            self.pygame.draw.circle(self.screen, (glow_r, glow_g, glow_b), (x, y), glow_radius)
            self.pygame.draw.circle(self.screen, base_color, (x, y), radius)
        
        # Draw stats overlay
        self._draw_stats(total_particles, active_particles, num_particles, fps, gpu_util, elapsed_time)
        
        # Draw sliders
        self._draw_sliders()
        
        # Draw text input for max balls
        self._draw_text_input()
        
        # Draw multiplier button
        self._draw_multiplier_button()
        
        # Draw toggle button
        self._draw_toggle_button()
        
        # Update display
        self.pygame.display.flip()
        self.clock.tick(60)  # Cap at 60 FPS
    
    def _draw_stats(
        self,
        total_particles: int,
        active_particles: int,
        rendered_particles: int,
        fps: float,
        gpu_util: float,
        elapsed_time: float
    ):
        """Draw statistics overlay."""
        stats = [
            f"Computing: {total_particles:,} particles",
            f"Active: {active_particles:,} particles",
            f"Rendering: {rendered_particles:,} particles",
            f"FPS: {fps:.1f}",
            f"GPU: {gpu_util:.0f}%",
            f"Time: {elapsed_time:.1f}s"
        ]
        
        y_offset = 15
        for text in stats:
            # Draw shadow
            shadow = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(shadow, (17, y_offset + 2))
            
            # Draw text
            rendered = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(rendered, (15, y_offset))
            y_offset += 35
        
        # Draw controls hint
        hint = self.font.render("Press ESC to stop", True, (150, 150, 150))
        self.screen.blit(hint, (15, self.window_size[1] - 40))
    
    def _draw_sliders(self):
        """Draw interactive sliders for real-time control."""
        for key, slider in self.sliders.items():
            x, y = slider['pos']
            width = slider['width']
            
            # Draw slider background
            self.pygame.draw.rect(self.screen, (40, 40, 60), (x, y, width, 20))
            
            # Calculate handle position
            normalized = (slider['value'] - slider['min']) / (slider['max'] - slider['min'])
            handle_x = x + int(normalized * width)
            
            # Draw filled portion
            self.pygame.draw.rect(self.screen, (80, 120, 200), (x, y, handle_x - x, 20))
            
            # Draw handle
            self.pygame.draw.circle(self.screen, (150, 180, 255), (handle_x, y + 10), 12)
            self.pygame.draw.circle(self.screen, (200, 220, 255), (handle_x, y + 10), 8)
            
            # Draw label and value (slider['value'] is already in correct range)
            if slider.get('is_int', False):
                label = self.small_font.render(f"{slider['label']}: {int(slider['value'])}", True, (200, 200, 200))
            else:
                label = self.small_font.render(f"{slider['label']}: {slider['value']:.1f}", True, (200, 200, 200))
            self.screen.blit(label, (x, y - 25))
    
    def _draw_toggle_button(self):
        """Draw the ball splitting toggle button."""
        bx, by = self.split_button['pos']
        bw, bh = self.split_button['width'], self.split_button['height']
        
        # Button background (green if ON, red if OFF)
        button_color = (50, 200, 50) if self.split_enabled else (200, 50, 50)
        self.pygame.draw.rect(self.screen, button_color, (bx, by, bw, bh))
        self.pygame.draw.rect(self.screen, (255, 255, 255), (bx, by, bw, bh), 2)
        
        # Button text
        text = self.small_font.render(self.split_button['label'], True, (255, 255, 255))
        text_rect = text.get_rect(center=(bx + bw // 2, by + bh // 2))
        self.screen.blit(text, text_rect)
    
    def _draw_text_input(self):
        """Draw text input box for max balls cap."""
        tx, ty = self.max_balls_cap['pos']
        tw, th = self.max_balls_cap['width'], self.max_balls_cap['height']
        
        # Box background (highlight if active)
        box_color = (100, 120, 150) if self.max_balls_cap['active'] else (40, 40, 60)
        self.pygame.draw.rect(self.screen, box_color, (tx, ty, tw, th))
        self.pygame.draw.rect(self.screen, (255, 255, 255), (tx, ty, tw, th), 2)
        
        # Label above box
        label = self.small_font.render(self.max_balls_cap['label'], True, (200, 200, 200))
        self.screen.blit(label, (tx, ty - 25))
        
        # Text value (no multiplier - this is hard cap)
        display_value = self.max_balls_cap['value'] if self.max_balls_cap['value'] else '0'
        text = self.small_font.render(display_value, True, (255, 255, 255))
        text_rect = text.get_rect(center=(tx + tw // 2, ty + th // 2))
        self.screen.blit(text, text_rect)
    
    def _draw_multiplier_button(self):
        """Draw the multiplier cycle button."""
        mx, my = self.multiplier_button['pos']
        mw, mh = self.multiplier_button['width'], self.multiplier_button['height']
        
        # Button background (blue)
        self.pygame.draw.rect(self.screen, (60, 100, 180), (mx, my, mw, mh))
        self.pygame.draw.rect(self.screen, (255, 255, 255), (mx, my, mw, mh), 2)
        
        # Button text
        text = self.small_font.render(self.multiplier_button['label'], True, (255, 255, 255))
        text_rect = text.get_rect(center=(mx + mw // 2, my + mh // 2))
        self.screen.blit(text, text_rect)
    
    def _handle_slider_click(self, pos):
        """Handle mouse click on sliders."""
        mx, my = pos
        for key, slider in self.sliders.items():
            x, y = slider['pos']
            width = slider['width']
            if x <= mx <= x + width and y - 12 <= my <= y + 32:
                self.dragging_slider = key
                self._update_slider_value(key, mx)
                break
    
    def _handle_slider_drag(self, pos):
        """Handle mouse drag on slider."""
        if self.dragging_slider:
            self._update_slider_value(self.dragging_slider, pos[0])
    
    def _update_slider_value(self, key, mouse_x):
        """Update slider value based on mouse position."""
        slider = self.sliders[key]
        x = slider['pos'][0]
        width = slider['width']  # Always 220px
        
        # Clamp to slider bounds
        mouse_x = max(x, min(mouse_x, x + width))
        normalized = (mouse_x - x) / width
        value = slider['min'] + normalized * (slider['max'] - slider['min'])
        
        # Round to integer if flag is set
        if slider.get('is_int', False):
            value = round(value)
        
        slider['value'] = value
    
    def get_slider_values(self):
        """Get current slider values for physics engine."""
        values = {}
        for key, slider in self.sliders.items():
            values[key] = slider['value']
        
        # Add max_balls_cap from text input (hard limit, no multiplier)
        max_cap = int(self.max_balls_cap['value']) if self.max_balls_cap['value'] else 100000
        values['max_balls_cap'] = max_cap
        
        return values
    
    def get_split_enabled(self):
        """Return whether ball splitting is enabled."""
        return self.split_enabled
    
    def close(self):
        """Close visualizer and cleanup."""
        if self.pygame and self.running:
            self.pygame.quit()
        self.running = False


def create_visualizer(enabled: bool = False, **kwargs) -> Optional[ParticleVisualizer]:
    """
    Factory function to create visualizer.
    
    Args:
        enabled: Whether visualization is enabled
        **kwargs: Arguments for ParticleVisualizer
        
    Returns:
        ParticleVisualizer instance or None if disabled/unavailable
    """
    if not enabled:
        return None
    
    viz = ParticleVisualizer(**kwargs)
    if not viz.is_available():
        return None
    
    return viz
