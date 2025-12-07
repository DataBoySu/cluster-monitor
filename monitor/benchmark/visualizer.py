"""GPU Particle Simulation Visualizer.

Renders a sampled subset of particles for visual feedback during benchmarking.
GPU computes millions, screen renders thousands for smooth 60 FPS display.
"""

import time
import random
from typing import Optional, Tuple, List
import numpy as np
from . import ui_components  # Import UI rendering functions
from . import event_handler  # Import event handling


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
        
        # UI Sliders with multiplier system (old UI style - 3 sliders)
        self.slider_multiplier = 1  # x1, x10, x100, x1000
        self.multiplier_levels = [1, 10, 100, 1000]
        self.multiplier_button = {
            'pos': (920, 700),
            'width': 80,
            'height': 30,
            'label': 'x1'
        }
        # Old UI layout: 3 sliders with 220px width
        self.sliders = {
            'gravity': {'value': 500.0, 'min': 0.0, 'max': 10000.0, 'pos': (50, 700), 'width': 220, 'label': 'Big Ball Gravity'},
            'small_ball_speed': {'value': 300.0, 'min': 50.0, 'max': 600.0, 'pos': (300, 700), 'width': 220, 'label': 'Small Ball Speed'},
            'initial_balls': {'value': 1.0, 'min': 1.0, 'max': 10.0, 'pos': (550, 700), 'width': 220, 'label': 'Initial Balls', 'is_int': True, 'base_max': 10.0}
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
            import os
            # Set SDL video driver for Windows to allow background thread display
            os.environ['SDL_VIDEODRIVER'] = 'windows'
            
            self.pygame = pygame
            pygame.init()
            self.screen = pygame.display.set_mode(self.window_size)
            pygame.display.set_caption("GPU Particle Simulation - Benchmark Visualization")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 28)
            self.small_font = pygame.font.Font(None, 20)
            self.running = True
            
            print(f"[VISUALIZER] Pygame initialized successfully - Window: {self.window_size}")
            
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
                
        except ImportError as e:
            self.running = False
            print(f"[WARNING] pygame not installed - visualization disabled: {e}")
            print("Install with: pip install pygame")
        except Exception as e:
            self.running = False
            print(f"[ERROR] Failed to initialize pygame: {e}")
    
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
        
        # NO on-screen stats - all stats go to console
        
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
        self.clock.tick()  # Unlimited FPS - no artificial cap
    
    def _draw_stats(
        self,
        total_particles: int,
        active_particles: int,
        rendered_particles: int,
        fps: float,
        gpu_util: float,
        elapsed_time: float
    ):
        """Draw statistics overlay using ui_components."""
        backend_mult = int(self.sliders.get('backend_multiplier', {}).get('value', 1))
        stats_data = {
            'total_particles': total_particles,
            'active_particles': active_particles,
            'rendered_particles': rendered_particles,
            'fps': fps,
            'gpu_util': gpu_util,
            'elapsed_time': elapsed_time,
            'backend_multiplier': backend_mult
        }
        ui_components.draw_stats(self.screen, self.font, self.window_size, stats_data)
    
    def _draw_sliders(self):
        """Draw interactive sliders using ui_components."""
        ui_components.draw_sliders(self.pygame, self.screen, self.small_font, self.sliders, self.dragging_slider)
    
    def _draw_toggle_button(self):
        """Draw the ball splitting toggle button using ui_components."""
        ui_components.draw_toggle_button(self.pygame, self.screen, self.small_font, self.split_button, self.split_enabled)
    
    def _draw_text_input(self):
        """Draw text input box using ui_components."""
        ui_components.draw_text_input(self.pygame, self.screen, self.font, self.small_font, self.max_balls_cap)
    
    def _draw_multiplier_button(self):
        """Draw multiplier button using ui_components."""
        ui_components.draw_multiplier_button(self.pygame, self.screen, self.small_font, self.multiplier_button)
    
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
        width = slider['width']
        
        # Clamp to slider bounds
        mouse_x = max(x, min(mouse_x, x + width))
        normalized = (mouse_x - x) / width
        value = slider['min'] + normalized * (slider['max'] - slider['min'])
        
        # Check for NaN or invalid values
        import math
        if math.isnan(value) or math.isinf(value):
            value = slider['min']  # Reset to minimum
        
        # Round to integer if flag is set
        if slider.get('is_int', False):
            value = round(value)
        
        slider['value'] = value
    
    def get_slider_values(self):
        """Get current slider values for physics engine."""
        import math
        values = {}
        for key, slider in self.sliders.items():
            val = slider['value']
            # Protect against NaN
            if math.isnan(val) or math.isinf(val):
                val = slider['min']  # Reset to safe default
                slider['value'] = val
            values[key] = val
        
        # Add max_balls_cap from text input (hard limit, no multiplier)
        max_cap = int(self.max_balls_cap['value']) if self.max_balls_cap['value'] else 100000
        values['max_balls_cap'] = max_cap
        
        # Default values for removed sliders (backend always 1x in old UI)
        values['backend_multiplier'] = 1
        values['big_ball_count'] = 3
        
        return values
    
    def get_split_enabled(self):
        """Return whether ball splitting is enabled."""
        return self.split_enabled
    
    def get_spawn_requests(self):
        """Get and clear pending big ball spawn requests."""
        if not hasattr(self, 'spawn_requests'):
            return []
        requests = self.spawn_requests[:]
        self.spawn_requests.clear()
        return requests
    
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
