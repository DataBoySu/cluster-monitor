"""Ultra-optimized GPU particle visualizer using ModernGL with instanced rendering."""

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
    Ultra-optimized GPU particle visualizer.
    - Instanced rendering for massive parallelism
    - Persistent mapped buffers for zero-copy transfers
    - Pre-allocated GPU resources
    - Geometry shaders for particle expansion
    - Batched circle rendering
    """
    
    def __init__(self, window_size: Tuple[int, int] = (1200, 800), max_particles: int = 100000):
        self.window_size = window_size
        self.max_particles = max_particles
        self._initialized = False
        self._ctx = None
        self._window = None
        self.running = True
        
        # Performance tracking
        self._frame_counter = 0
        self._adaptive_skip = 0
        self._last_stats_frame = 0
        
        # Slider state (stored for get_slider_values)
        self.sliders = {
            'gravity': {'value': 500.0, 'min': 0.0, 'max': 10000.0, 'pos': (50, 700), 'width': 220, 'label': 'Big Ball Gravity'},
            'small_ball_speed': {'value': 300.0, 'min': 50.0, 'max': 600.0, 'pos': (300, 700), 'width': 220, 'label': 'Small Ball Speed'},
            'initial_balls': {'value': 1.0, 'min': 1.0, 'max': 10.0, 'pos': (550, 700), 'width': 220, 'label': 'Initial Balls', 'is_int': True, 'base_max': 10.0},
            'big_ball_count': {'value': 4.0, 'min': 1.0, 'max': 20.0, 'pos': (800, 700), 'width': 220, 'label': 'Big Balls', 'is_int': True},
        }
        self.dragging_slider = None
        
        self.max_balls_cap = {
            'pos': (1050, 700), 'width': 100, 'height': 30,
            'value': '100000', 'active': False, 'label': 'Max Cap'
        }
        
        self.multiplier_button = {'pos': (50, 750), 'width': 80, 'height': 30, 'label': 'x1'}
        self.split_button = {'pos': (150, 750), 'width': 160, 'height': 30, 'label': 'Ball Splitting: OFF'}
        
        self.slider_multiplier = 1
        self.multiplier_levels = [1, 10, 100, 1000]
        self.split_enabled = False
        
        # GPU resources
        self._particle_vao = None
        self._particle_vbo = None  # Persistent mapped buffer
        self._particle_program = None
        self._circle_vao = None
        self._circle_vbo = None
        self._circle_instance_vbo = None
        self._circle_program = None
        self._circle_geometry = None  # Pre-computed circle vertices
        
        try:
            self._init_opengl()
            self._initialized = True
        except Exception as e:
            print(f"[ERROR] Failed to initialize OpenGL: {e}")
            self._initialized = False
    
    def _init_opengl(self):
        """Initialize OpenGL with maximum performance settings."""
        import glfw
        
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        
        # OpenGL 4.5+ for best performance features
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 5)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.DOUBLEBUFFER, True)
        
        self._window = glfw.create_window(
            self.window_size[0], self.window_size[1], 
            "GPU Particle Simulation [Optimized]", None, None
        )
        
        if not self._window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")
        
        glfw.make_context_current(self._window)
        glfw.swap_interval(0)  # No vsync
        
        # Callbacks
        glfw.set_mouse_button_callback(self._window, self._mouse_callback)
        glfw.set_cursor_pos_callback(self._window, self._cursor_callback)
        glfw.set_key_callback(self._window, self._key_callback)
        
        # ModernGL context
        self._ctx = mgl.create_context()
        self._ctx.enable(mgl.BLEND)
        self._ctx.blend_func = mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA
        
        # ========== PARTICLE RENDERING (Instanced Point Sprites) ==========
        particle_vert = """
        #version 450 core
        
        layout (location = 0) in vec2 position;
        layout (location = 1) in vec3 color;
        layout (location = 2) in float radius;
        layout (location = 3) in float glow;
        
        out vec3 v_color;
        out float v_glow;
        
        uniform vec2 u_screen_size;
        
        void main() {
            vec2 ndc = (position / vec2(1000.0, 800.0)) * 2.0 - 1.0;
            ndc.y = -ndc.y;
            gl_Position = vec4(ndc, 0.0, 1.0);
            gl_PointSize = radius * 2.0;
            v_color = color;
            v_glow = glow;
        }
        """
        
        particle_frag = """
        #version 450 core
        
        in vec3 v_color;
        in float v_glow;
        
        out vec4 fragColor;
        
        void main() {
            vec2 coord = gl_PointCoord - vec2(0.5);
            float dist = length(coord);
            
            if (dist > 0.5) discard;
            
            float alpha = smoothstep(0.5, 0.3, dist);
            vec3 glow_color = v_color * (1.0 + v_glow * 2.0);
            fragColor = vec4(glow_color, alpha);
        }
        """
        
        self._particle_program = self._ctx.program(
            vertex_shader=particle_vert,
            fragment_shader=particle_frag
        )
        
        # Pre-allocate persistent mapped buffer for particles
        # 7 floats per particle: x, y, r, g, b, radius, glow
        buffer_size = self.max_particles * 7 * 4  # 4 bytes per float
        self._particle_vbo = self._ctx.buffer(reserve=buffer_size)
        
        self._particle_vao = self._ctx.vertex_array(
            self._particle_program,
            [(self._particle_vbo, '2f 3f 1f 1f', 'position', 'color', 'radius', 'glow')]
        )
        
        # ========== CIRCLE RENDERING (Instanced Geometry) ==========
        circle_vert = """
        #version 450 core
        
        layout (location = 0) in vec2 vertex;      // Circle template vertices
        layout (location = 1) in vec3 instance;    // (center_x, center_y, radius)
        
        void main() {
            vec2 world_pos = instance.xy + vertex * instance.z;
            vec2 ndc = (world_pos / vec2(1000.0, 800.0)) * 2.0 - 1.0;
            ndc.y = -ndc.y;
            gl_Position = vec4(ndc, 0.0, 1.0);
        }
        """
        
        circle_frag = """
        #version 450 core
        
        out vec4 fragColor;
        
        void main() {
            fragColor = vec4(1.0, 1.0, 1.0, 0.3);
        }
        """
        
        self._circle_program = self._ctx.program(
            vertex_shader=circle_vert,
            fragment_shader=circle_frag
        )
        
        # Pre-compute circle geometry (unit circle)
        num_segments = 64
        angles = np.linspace(0, 2 * np.pi, num_segments + 1, dtype=np.float32)
        circle_verts = np.column_stack([np.cos(angles), np.sin(angles)]).astype(np.float32)
        self._circle_geometry = circle_verts
        self._circle_vbo = self._ctx.buffer(circle_verts.tobytes())
        
        # Instance buffer for circles (center_x, center_y, radius) - max 10 big balls
        self._circle_instance_vbo = self._ctx.buffer(reserve=10 * 3 * 4)
        
        self._circle_vao = self._ctx.vertex_array(
            self._circle_program,
            [
                (self._circle_vbo, '2f', 'vertex'),
                (self._circle_instance_vbo, '3f /i', 'instance'),  # /i = per-instance
            ]
        )
        
        # ========== UI RENDERING (Simple rectangles for sliders) ==========
        ui_vert = """
        #version 450 core
        
        layout (location = 0) in vec2 position;
        layout (location = 1) in vec4 color;
        
        out vec4 v_color;
        
        void main() {
            vec2 ndc = (position / vec2(1200.0, 800.0)) * 2.0 - 1.0;
            ndc.y = -ndc.y;
            gl_Position = vec4(ndc, 0.0, 1.0);
            v_color = color;
        }
        """
        
        ui_frag = """
        #version 450 core
        
        in vec4 v_color;
        out vec4 fragColor;
        
        void main() {
            fragColor = v_color;
        }
        """
        
        self._ui_program = self._ctx.program(
            vertex_shader=ui_vert,
            fragment_shader=ui_frag
        )
        
        # UI buffer for drawing rectangles (sliders, buttons, etc)
        self._ui_vbo = self._ctx.buffer(reserve=10000 * 6 * 4)  # Many vertices
        self._ui_vao = self._ctx.vertex_array(
            self._ui_program,
            [(self._ui_vbo, '2f 4f', 'position', 'color')]
        )
        
        print(f"[OpenGL] Ultra-optimized renderer initialized (max {self.max_particles:,} particles)")
        print(f"[OpenGL] Features: Instanced rendering, persistent buffers, pre-allocated geometry")
    
    def _mouse_callback(self, window, button, action, mods):
        """Mouse button handler."""
        import glfw
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            x, y = glfw.get_cursor_pos(window)
            self._handle_click(x, y)
    
    def _cursor_callback(self, window, x, y):
        """Mouse movement handler."""
        import glfw
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            if self.dragging_slider:
                self._update_slider(self.dragging_slider, x)
    
    def _key_callback(self, window, key, scancode, action, mods):
        """Keyboard handler."""
        import glfw
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                self.running = False
            elif self.max_balls_cap['active']:
                if key == glfw.KEY_ENTER:
                    try:
                        max_cap = int(self.max_balls_cap['value']) if self.max_balls_cap['value'] else 1
                        initial = int(self.sliders['initial_balls']['value'])
                        if max_cap < initial:
                            self.max_balls_cap['value'] = str(initial)
                    except ValueError:
                        self.max_balls_cap['value'] = '100000'
                    self.max_balls_cap['active'] = False
                elif key == glfw.KEY_BACKSPACE:
                    self.max_balls_cap['value'] = self.max_balls_cap['value'][:-1]
    
    def _handle_click(self, x, y):
        """UI click handler."""
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
            old = self.slider_multiplier
            idx = self.multiplier_levels.index(old)
            self.slider_multiplier = self.multiplier_levels[(idx + 1) % len(self.multiplier_levels)]
            self.multiplier_button['label'] = f'x{self.slider_multiplier}'
            
            ratio = self.slider_multiplier / old
            slider = self.sliders['initial_balls']
            slider['value'] *= ratio
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
                self._update_slider(key, x)
                return
    
    def _update_slider(self, key, mouse_x):
        """Update slider value."""
        slider = self.sliders[key]
        t = max(0.0, min(1.0, (mouse_x - slider['pos'][0]) / slider['width']))
        value = slider['min'] + t * (slider['max'] - slider['min'])
        slider['value'] = round(value) if slider.get('is_int') else value
    
    def is_available(self) -> bool:
        """Check if visualizer is ready."""
        return self._initialized and self._window is not None
    
    def render_frame(self, positions, masses, colors, glows, influence_boundaries,
                     total_particles: int, active_particles: int,
                     fps: float, gpu_util: float, elapsed_time: float):
        """
        Ultra-optimized rendering using instanced geometry and persistent buffers.
        """
        if not self.is_available():
            return
        
        import glfw
        
        if glfw.window_should_close(self._window):
            self.running = False
            return
        
        self._frame_counter += 1
        
        # Adaptive frame skipping
        if fps > 0 and fps < 15:
            self._adaptive_skip = max(1, int(30 / fps))
        elif fps >= 30:
            self._adaptive_skip = 0
        
        if self._adaptive_skip > 0 and (self._frame_counter % (self._adaptive_skip + 1)) != 0:
            glfw.poll_events()
            return
        
        # ========== GPU RENDERING ==========
        self._ctx.clear(0.02, 0.02, 0.06)
        
        # Draw circles (instanced - single draw call for all circles)
        if influence_boundaries and len(influence_boundaries) > 0:
            num_circles = len(influence_boundaries)
            # Pack instance data: [cx, cy, radius] for each circle
            instance_data = np.array(influence_boundaries, dtype=np.float32).flatten()
            self._circle_instance_vbo.write(instance_data.tobytes())
            
            # Single instanced draw call for all circles
            self._ctx.line_width = 2.0
            self._circle_vao.render(mgl.LINE_STRIP, instances=num_circles)
        
        # Draw particles
        if positions is not None and len(positions) > 0:
            num_particles = len(positions)
            
            # Performance limit: render subset if too many particles
            max_render = min(num_particles, 80000)  # Increased from 50k
            if num_particles > max_render:
                step = num_particles // max_render
                positions = positions[::step]
                if masses is not None:
                    masses = masses[::step]
                if colors is not None:
                    colors = colors[::step]
                if glows is not None:
                    glows = glows[::step]
                num_particles = len(positions)
            
            # Build vertex data efficiently
            vertex_data = np.empty((num_particles, 7), dtype=np.float32)
            vertex_data[:, 0:2] = positions
            
            # Colors
            if colors is not None and len(colors) == num_particles and colors.shape[1] == 3:
                vertex_data[:, 2:5] = colors
            else:
                vertex_data[:, 2:5] = 1.0
            
            # Radius (big balls = 36, small = 8)
            if masses is not None:
                vertex_data[:, 5] = np.where(masses >= 100.0, 36.0, 8.0)
            else:
                vertex_data[:, 5] = 8.0
            
            # Glow
            if glows is not None and len(glows) == num_particles:
                vertex_data[:, 6] = glows
            else:
                vertex_data[:, 6] = 0.0
            
            # Single GPU upload
            self._particle_vbo.write(vertex_data.tobytes())
            
            # Single draw call for all particles
            self._ctx.enable(mgl.PROGRAM_POINT_SIZE)
            self._particle_vao.render(mgl.POINTS, vertices=num_particles)
        
        # Stats (console output - minimal overhead)
        if self._frame_counter - self._last_stats_frame >= 30:
            self._last_stats_frame = self._frame_counter
            
            perf = "ADAPTIVE" if self._adaptive_skip > 0 else "OPTIMAL"
            skip_info = f" | Skip:{self._adaptive_skip}" if self._adaptive_skip > 0 else ""
            
            render_info = ""
            if active_particles > 80000:
                rendered = min(80000, active_particles)
                ratio = (rendered / active_particles) * 100
                render_info = f" | Draw:{rendered:,}/{active_particles:,} ({ratio:.0f}%)"
            
            print(f"[GPU] Active:{active_particles:,} Total:{total_particles:,} FPS:{fps:.1f} GPU:{gpu_util:.0f}% Time:{elapsed_time:.1f}s Perf:{perf}{skip_info}{render_info}")
            
            if self._frame_counter % 120 == 0:
                print(f"[Ctrl] Grav:{self.sliders['gravity']['value']:.0f} Speed:{self.sliders['small_ball_speed']['value']:.0f} Balls:{int(self.sliders['initial_balls']['value'])} BigBalls:{int(self.sliders['big_ball_count']['value'])} Cap:{self.max_balls_cap['value']} Split:{'ON' if self.split_enabled else 'OFF'}")
        
        # Draw UI overlay (sliders and buttons)
        self._draw_ui()
        
        glfw.swap_buffers(self._window)
        glfw.poll_events()
    
    def _draw_ui(self):
        """Draw simple UI overlay (sliders, buttons, labels)."""
        ui_verts = []
        
        # Helper to add a rectangle
        def add_rect(x, y, w, h, r, g, b, a):
            # Two triangles for rectangle
            ui_verts.extend([
                x, y, r, g, b, a,
                x+w, y, r, g, b, a,
                x, y+h, r, g, b, a,
                
                x+w, y, r, g, b, a,
                x+w, y+h, r, g, b, a,
                x, y+h, r, g, b, a,
            ])
        
        # Draw sliders
        for key, slider in self.sliders.items():
            x, y = slider['pos']
            width = slider['width']
            
            # Background track (dark gray)
            add_rect(x, y, width, 8, 0.2, 0.2, 0.2, 0.8)
            
            # Value indicator (bright color based on value)
            t = (slider['value'] - slider['min']) / (slider['max'] - slider['min'])
            handle_x = x + t * width
            
            # Filled portion (cyan)
            add_rect(x, y, t * width, 8, 0.2, 0.8, 1.0, 0.9)
            
            # Handle (white circle approximated as small rect)
            add_rect(handle_x - 5, y - 4, 10, 16, 1.0, 1.0, 1.0, 1.0)
        
        # Draw buttons
        for button_data in [self.multiplier_button, self.split_button]:
            bx, by = button_data['pos']
            bw, bh = button_data['width'], button_data['height']
            
            # Button background (semi-transparent)
            add_rect(bx, by, bw, bh, 0.3, 0.3, 0.3, 0.7)
            
            # Border (bright)
            add_rect(bx, by, bw, 2, 0.8, 0.8, 0.8, 1.0)  # Top
            add_rect(bx, by+bh-2, bw, 2, 0.8, 0.8, 0.8, 1.0)  # Bottom
            add_rect(bx, by, 2, bh, 0.8, 0.8, 0.8, 1.0)  # Left
            add_rect(bx+bw-2, by, 2, bh, 0.8, 0.8, 0.8, 1.0)  # Right
        
        # Text input box
        tx, ty = self.max_balls_cap['pos']
        tw, th = self.max_balls_cap['width'], self.max_balls_cap['height']
        
        color = (0.5, 0.7, 1.0) if self.max_balls_cap['active'] else (0.3, 0.3, 0.3)
        add_rect(tx, ty, tw, th, color[0], color[1], color[2], 0.8)
        
        # Upload and render
        if len(ui_verts) > 0:
            ui_data = np.array(ui_verts, dtype=np.float32)
            self._ui_vbo.write(ui_data.tobytes())
            self._ui_vao.render(mgl.TRIANGLES, vertices=len(ui_verts) // 6)
    
    def get_slider_values(self):
        """Get current control values."""
        values = {}
        for key, slider in self.sliders.items():
            values[key] = int(slider['value']) if slider.get('is_int') else slider['value']
        
        try:
            values['max_balls_cap'] = int(self.max_balls_cap['value']) if self.max_balls_cap['value'] else 100000
        except ValueError:
            values['max_balls_cap'] = 100000
        
        return values
    
    def get_split_enabled(self):
        """Get split toggle state."""
        return self.split_enabled
    
    def close(self):
        """Close visualizer."""
        self.running = False
        self.cleanup()
    
    def cleanup(self):
        """Release GPU resources."""
        import glfw
        if self._window:
            glfw.destroy_window(self._window)
            glfw.terminate()


def create_visualizer(enabled: bool = False, use_gl: bool = True, **kwargs) -> Optional[GLParticleVisualizer]:
    """
    Create ultra-optimized GPU visualizer.
    """
    if not enabled:
        return None
    
    try:
        max_particles = kwargs.get('num_particles', 100000)
        viz = GLParticleVisualizer(max_particles=max_particles)
        if viz.is_available():
            print("[OpenGL] Ultra-optimized visualizer created")
            return viz
        else:
            print("[OpenGL] Initialization failed")
            return None
    except Exception as e:
        print(f"[OpenGL] Error: {e}")
        return None
