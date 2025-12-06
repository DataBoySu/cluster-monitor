"""GPU-accelerated particle visualizer using ModernGL (OpenGL compute shaders)."""

import time
import numpy as np
from typing import Optional, Tuple

try:
    import moderngl as mgl
    MGL_AVAILABLE = True
except ImportError:
    mgl = None
    MGL_AVAILABLE = False


class GLParticleVisualizer:
    """
    GPU-accelerated particle visualizer using ModernGL and OpenGL shaders.
    All rendering happens on GPU with minimal CPU overhead.
    """
    
    def __init__(self, window_size: Tuple[int, int] = (1200, 800)):
        self.window_size = window_size
        self._initialized = False
        self._ctx = None
        self._window = None
        self.running = True
        
        # Performance tracking
        self._frame_times = []
        self._last_fps = 0
        self._adaptive_skip = 0  # Skip frames when FPS drops
        self._frame_counter = 0
        
        # Slider state
        self.sliders = {
            'gravity': {'value': 500.0, 'min': 0.0, 'max': 10000.0, 'pos': (50, 700), 'width': 220, 'label': 'Big Ball Gravity'},
            'small_ball_speed': {'value': 300.0, 'min': 50.0, 'max': 600.0, 'pos': (300, 700), 'width': 220, 'label': 'Small Ball Speed'},
            'initial_balls': {'value': 1.0, 'min': 1.0, 'max': 10.0, 'pos': (550, 700), 'width': 220, 'label': 'Initial Balls', 'is_int': True, 'base_max': 10.0},
        }
        self.dragging_slider = None
        
        # UI state
        self.max_balls_cap = {
            'pos': (800, 700),
            'width': 100,
            'height': 30,
            'value': '100000',
            'active': False,
            'label': 'Max Cap'
        }
        
        self.multiplier_button = {
            'pos': (920, 700),
            'width': 80,
            'height': 30,
            'label': 'x1'
        }
        
        self.split_button = {
            'pos': (1020, 700),
            'width': 160,
            'height': 30,
            'label': 'Ball Splitting: OFF'
        }
        
        self.slider_multiplier = 1
        self.multiplier_levels = [1, 10, 100, 1000]
        self.split_enabled = False
        
        # OpenGL resources
        self._vao = None
        self._vbo = None
        self._particle_program = None
        self._ui_program = None
        self._last_particle_count = 0
        
        try:
            self._init_opengl()
            self._initialized = True
        except Exception as e:
            print(f"[WARNING] Failed to initialize OpenGL visualizer: {e}")
            self._initialized = False
    
    def _init_opengl(self):
        """Initialize OpenGL context and shaders."""
        import glfw
        
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        
        # Create window with OpenGL 4.3+ for compute shaders
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        
        self._window = glfw.create_window(
            self.window_size[0], 
            self.window_size[1], 
            "GPU Particle Simulation", 
            None, 
            None
        )
        
        if not self._window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")
        
        glfw.make_context_current(self._window)
        glfw.swap_interval(0)  # Disable vsync for max FPS
        
        # Setup callbacks
        glfw.set_mouse_button_callback(self._window, self._mouse_button_callback)
        glfw.set_cursor_pos_callback(self._window, self._cursor_pos_callback)
        glfw.set_key_callback(self._window, self._key_callback)
        
        # Create ModernGL context
        self._ctx = mgl.create_context()
        self._ctx.enable(mgl.BLEND)
        self._ctx.blend_func = mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA
        
        # Particle vertex shader (GPU)
        particle_vertex = """
        #version 430
        
        layout (location = 0) in vec2 in_position;
        layout (location = 1) in vec3 in_color;
        layout (location = 2) in float in_radius;
        layout (location = 3) in float in_glow;
        
        out vec3 color;
        out float glow;
        out vec2 center;
        
        uniform vec2 screen_size;
        
        void main() {
            // Transform to normalized device coordinates
            vec2 pos = (in_position / vec2(1000.0, 800.0)) * 2.0 - 1.0;
            pos.y = -pos.y;  // Flip Y
            
            gl_Position = vec4(pos, 0.0, 1.0);
            gl_PointSize = in_radius * 2.0;
            
            color = in_color;
            glow = in_glow;
            center = pos;
        }
        """
        
        # Particle fragment shader with glow effect (GPU)
        particle_fragment = """
        #version 430
        
        in vec3 color;
        in float glow;
        in vec2 center;
        
        out vec4 fragColor;
        
        void main() {
            // Circular particle shape
            vec2 coord = gl_PointCoord - vec2(0.5);
            float dist = length(coord);
            
            if (dist > 0.5) {
                discard;
            }
            
            // Soft edge with glow
            float alpha = smoothstep(0.5, 0.3, dist);
            vec3 glow_color = color * (1.0 + glow * 2.0);
            
            fragColor = vec4(glow_color, alpha);
        }
        """
        
        self._particle_program = self._ctx.program(
            vertex_shader=particle_vertex,
            fragment_shader=particle_fragment
        )
        
        # Circle shader for gravity boundaries
        circle_vertex = """
        #version 430
        
        layout (location = 0) in vec2 in_position;
        
        void main() {
            vec2 pos = (in_position / vec2(1000.0, 800.0)) * 2.0 - 1.0;
            pos.y = -pos.y;
            gl_Position = vec4(pos, 0.0, 1.0);
        }
        """
        
        circle_fragment = """
        #version 430
        
        out vec4 fragColor;
        
        void main() {
            fragColor = vec4(1.0, 1.0, 1.0, 0.3);  // Semi-transparent white
        }
        """
        
        self._circle_program = self._ctx.program(
            vertex_shader=circle_vertex,
            fragment_shader=circle_fragment
        )
        
        # Create vertex buffer (will be updated each frame)
        self._vbo = self._ctx.buffer(reserve=1024 * 1024 * 4)  # 1MB buffer
        
        # Vertex array object
        self._vao = self._ctx.vertex_array(
            self._particle_program,
            [
                (self._vbo, '2f 3f 1f 1f', 'in_position', 'in_color', 'in_radius', 'in_glow')
            ]
        )
        
        print("[OpenGL] GPU-accelerated visualizer initialized (ModernGL)")
    
    def _mouse_button_callback(self, window, button, action, mods):
        """Handle mouse button events."""
        import glfw
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            x, y = glfw.get_cursor_pos(window)
            self._handle_click(x, y)
    
    def _cursor_pos_callback(self, window, x, y):
        """Handle mouse movement."""
        import glfw
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            if self.dragging_slider:
                self._update_slider_value(self.dragging_slider, x)
    
    def _key_callback(self, window, key, scancode, action, mods):
        """Handle keyboard input."""
        import glfw
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                self.running = False
            elif self.max_balls_cap['active']:
                if key == glfw.KEY_ENTER:
                    # Validate max cap
                    try:
                        max_cap = int(self.max_balls_cap['value']) if self.max_balls_cap['value'] else 1
                        initial = int(self.sliders['initial_balls']['value']) if 'initial_balls' in self.sliders else 1
                        if max_cap < initial:
                            self.max_balls_cap['value'] = str(initial)
                    except ValueError:
                        self.max_balls_cap['value'] = '100000'
                    self.max_balls_cap['active'] = False
                elif key == glfw.KEY_BACKSPACE:
                    self.max_balls_cap['value'] = self.max_balls_cap['value'][:-1]
    
    def _handle_click(self, x, y):
        """Handle UI clicks."""
        # Text input
        tx, ty = self.max_balls_cap['pos']
        tw, th = self.max_balls_cap['width'], self.max_balls_cap['height']
        if tx <= x <= tx + tw and ty <= y <= ty + th:
            self.max_balls_cap['active'] = True
            return
        else:
            self.max_balls_cap['active'] = False
        
        # Multiplier button
        mx, my = self.multiplier_button['pos']
        mw, mh = self.multiplier_button['width'], self.multiplier_button['height']
        if mx <= x <= mx + mw and my <= y <= my + mh:
            old_multiplier = self.slider_multiplier
            current_idx = self.multiplier_levels.index(self.slider_multiplier)
            next_idx = (current_idx + 1) % len(self.multiplier_levels)
            self.slider_multiplier = self.multiplier_levels[next_idx]
            self.multiplier_button['label'] = f'x{self.slider_multiplier}'
            
            multiplier_ratio = self.slider_multiplier / old_multiplier
            if 'initial_balls' in self.sliders:
                slider = self.sliders['initial_balls']
                slider['value'] = slider['value'] * multiplier_ratio
                slider['max'] = slider['base_max'] * self.slider_multiplier
            return
        
        # Split button
        bx, by = self.split_button['pos']
        bw, bh = self.split_button['width'], self.split_button['height']
        if bx <= x <= bx + bw and by <= y <= by + bh:
            self.split_enabled = not self.split_enabled
            self.split_button['label'] = f"Ball Splitting: {'ON' if self.split_enabled else 'OFF'}"
            return
        
        # Sliders
        for key, slider in self.sliders.items():
            sx, sy = slider['pos']
            width = slider['width']
            if sx <= x <= sx + width and sy - 12 <= y <= sy + 32:
                self.dragging_slider = key
                self._update_slider_value(key, x)
                return
    
    def _update_slider_value(self, key, mouse_x):
        """Update slider value based on mouse position."""
        slider = self.sliders[key]
        x = slider['pos'][0]
        width = slider['width']
        
        t = max(0.0, min(1.0, (mouse_x - x) / width))
        value = slider['min'] + t * (slider['max'] - slider['min'])
        
        if slider.get('is_int', False):
            value = round(value)
        
        slider['value'] = value
    
    def is_available(self) -> bool:
        """Check if OpenGL visualizer is available."""
        return self._initialized and self._window is not None
    
    def render_frame(self, positions, masses, colors, glows, influence_boundaries, 
                     total_particles: int, active_particles: int,
                     fps: float, gpu_util: float, elapsed_time: float):
        """
        Render a frame using GPU (OpenGL).
        All rendering happens on GPU with point sprites and shaders.
        
        Args:
            positions: Nx2 array of [x, y] positions
            masses: N array of particle masses
            colors: Nx3 array of RGB colors (0-1 range)
            glows: N array of glow intensities (0-1 range)
            influence_boundaries: List of (center_x, center_y, radius) for big balls
            total_particles: Total number of particles (initial count)
            active_particles: Number of currently active particles
            fps: Current render FPS
            gpu_util: Current GPU utilization percentage
            elapsed_time: Time elapsed since start
        """
        if not self.is_available():
            return
        
        import glfw
        import time
        
        # Check if window should close
        if glfw.window_should_close(self._window):
            self.running = False
            return
        
        # Adaptive rendering: Skip frames if FPS is too low
        self._frame_counter += 1
        if fps > 0 and fps < 15:  # If FPS drops below 15
            self._adaptive_skip = max(1, int(30 / fps))  # Skip more frames
        elif fps >= 30:
            self._adaptive_skip = 0  # No skipping at good FPS
        
        # Skip rendering if needed (but still poll events)
        if self._adaptive_skip > 0 and (self._frame_counter % (self._adaptive_skip + 1)) != 0:
            glfw.poll_events()
            return
        
        # Clear screen (GPU)
        self._ctx.clear(0.02, 0.02, 0.06)  # Dark background
        
        # Draw gravity influence boundaries (white circles)
        if influence_boundaries and len(influence_boundaries) > 0:
            self._ctx.line_width = 2.0
            for center_x, center_y, radius in influence_boundaries:
                # Generate circle vertices
                num_segments = 64
                circle_verts = []
                for i in range(num_segments + 1):
                    angle = (i / num_segments) * 2.0 * np.pi
                    x = center_x + radius * np.cos(angle)
                    y = center_y + radius * np.sin(angle)
                    circle_verts.extend([x, y])
                
                circle_data = np.array(circle_verts, dtype=np.float32)
                circle_vbo = self._ctx.buffer(circle_data.tobytes())
                circle_vao = self._ctx.simple_vertex_array(
                    self._circle_program,
                    circle_vbo,
                    'in_position'
                )
                circle_vao.render(mode=self._ctx.LINE_STRIP)
                circle_vbo.release()
                circle_vao.release()
        
        # Prepare particle data for GPU
        if positions is not None and len(positions) > 0:
            num_particles = len(positions)
            
            # Performance optimization: Render only a subset when particle count is very high
            # This prevents CPU-side bottleneck from data transfer and vertex processing
            max_render_particles = 50000
            if num_particles > max_render_particles:
                # Sample particles uniformly
                sample_indices = np.linspace(0, num_particles - 1, max_render_particles, dtype=np.int32)
                positions = positions[sample_indices]
                if masses is not None:
                    masses = masses[sample_indices]
                if colors is not None:
                    colors = colors[sample_indices]
                if glows is not None:
                    glows = glows[sample_indices]
                num_particles = max_render_particles
            
            # Build vertex data: [x, y, r, g, b, radius, glow]
            vertex_data = np.zeros((num_particles, 7), dtype=np.float32)
            vertex_data[:, 0:2] = positions  # x, y
            
            # Colors (RGB)
            if colors is not None and len(colors) == num_particles:
                if len(colors.shape) == 2 and colors.shape[1] == 3:
                    vertex_data[:, 2:5] = colors
                else:
                    vertex_data[:, 2:5] = 1.0  # White fallback
            else:
                vertex_data[:, 2:5] = 1.0
            
            # Radius based on mass
            if masses is not None:
                vertex_data[:, 5] = np.where(masses >= 100.0, 36.0, 8.0)
            else:
                vertex_data[:, 5] = 8.0
            
            # Glow intensity
            if glows is not None and len(glows) == num_particles:
                vertex_data[:, 6] = glows
            else:
                vertex_data[:, 6] = 0.0
            
            # Upload to GPU (single transfer)
            self._vbo.write(vertex_data.tobytes())
            
            # Render particles as point sprites (GPU)
            self._ctx.point_size = 1.0
            self._ctx.enable(mgl.PROGRAM_POINT_SIZE)
            self._vao.render(mode=self._ctx.POINTS, vertices=num_particles)
        
        # Print stats to console periodically
        if self._frame_counter % 30 == 0:  # Every ~30 frames
            perf_status = "ADAPTIVE" if self._adaptive_skip > 0 else "GOOD"
            skip_info = f" | Skip: {self._adaptive_skip}" if self._adaptive_skip > 0 else ""
            
            # Show render optimization if active
            render_info = ""
            if active_particles > 50000:
                render_ratio = min(1.0, 50000 / active_particles)
                rendered_count = int(active_particles * render_ratio)
                render_info = f" | Rendering: {rendered_count:,}/{active_particles:,} ({render_ratio*100:.0f}%)"
            
            print(f"[OpenGL] Active: {active_particles:,} | Total: {total_particles:,} | FPS: {fps:.1f} | GPU: {gpu_util:.0f}% | Time: {elapsed_time:.1f}s | Perf: {perf_status}{skip_info}{render_info}")
            
            # Show current slider values every 120 frames
            if self._frame_counter % 120 == 0:
                print(f"[Controls] Gravity: {self.sliders['gravity']['value']:.0f} | Speed: {self.sliders['small_ball_speed']['value']:.0f} | Balls: {self.sliders['initial_balls']['value']:.0f} | Max Cap: {self.max_balls_cap['value']} | Split: {'ON' if self.split_enabled else 'OFF'}")
        
        # Swap buffers
        glfw.swap_buffers(self._window)
        glfw.poll_events()
    
    def get_slider_values(self):
        """Get current slider values."""
        values = {}
        for key, slider in self.sliders.items():
            if slider.get('is_int', False):
                values[key] = int(slider['value'])
            else:
                values[key] = slider['value']
        
        # Add max balls cap
        try:
            values['max_balls_cap'] = int(self.max_balls_cap['value']) if self.max_balls_cap['value'] else 100000
        except ValueError:
            values['max_balls_cap'] = 100000
        
        return values
    
    def get_split_enabled(self):
        """Get split toggle state."""
        return self.split_enabled
    
    def close(self):
        """Close visualizer and cleanup."""
        self.running = False
        self.cleanup()
    
    def cleanup(self):
        """Clean up OpenGL resources."""
        import glfw
        if self._window:
            glfw.destroy_window(self._window)
            glfw.terminate()


def create_visualizer(enabled: bool = False, use_gl: bool = True, **kwargs) -> Optional[GLParticleVisualizer]:
    """
    Create GPU-accelerated particle visualizer (OpenGL).
    
    Args:
        enabled: Whether to enable visualization
        use_gl: Use OpenGL visualizer (default True)
        **kwargs: Additional arguments
        
    Returns:
        GLParticleVisualizer instance or None
    """
    if not enabled:
        return None
    
    try:
        viz = GLParticleVisualizer()
        if viz.is_available():
            print("[OpenGL] GPU-accelerated visualizer created successfully")
            return viz
        else:
            print("[OpenGL] Failed to initialize - falling back to pygame")
            return None
    except Exception as e:
        print(f"[OpenGL] Error creating visualizer: {e}")
        return None
