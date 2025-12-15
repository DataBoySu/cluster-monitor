"""Backend stress multiplier for GPU workloads.

Maintenance:
 - Keeps imports lightweight at module import time.
 - Manages offscreen/backend arrays used to increase
     effective particle counts for GPU stress testing.
"""

from . import gpu_setup


class BackendStressManager:
    """Manages backend (offscreen) particle arrays for GPU stress testing."""
    
    def __init__(self):
        """Initialize backend stress manager."""
        self._backend_arrays = []
        self._backend_multiplier = 1
        self._method = None
        self._library = None  # cp or torch
        self._particle_count = 0
        self._initialized = False
    
    def initialize(self, method: str, library, particle_count: int, backend_multiplier: int):
        """
        Initialize backend arrays.
        
        Args:
            method: 'cupy' or 'torch'
            library: CuPy or PyTorch module
            particle_count: Number of particles per array
            backend_multiplier: Multiplier for stress (1 = no backend, 10 = 10x particles)
        """
        self._method = method
        self._library = library
        self._backend_multiplier = backend_multiplier
        self._particle_count = particle_count
        self._backend_arrays = []
        self._initialized = True
        
        if backend_multiplier > 1:
            for i in range(backend_multiplier - 1):  # -1 because main arrays count as 1x
                if method == 'cupy':
                    backend_gpu, _ = gpu_setup.setup_cupy_arrays(particle_count, library)
                elif method == 'torch':
                    backend_gpu, _ = gpu_setup.setup_torch_arrays(particle_count, library)
                else:
                    continue
                self._backend_arrays.append(backend_gpu)
    
    def update_multiplier(self, new_multiplier: int, particle_count: int):
        """
        Update backend multiplier by recreating arrays.
        
        Args:
            new_multiplier: New multiplier value (minimum 1, no upper limit)
            particle_count: Number of particles per array
        """
        if new_multiplier < 1:
            new_multiplier = 1
        # No upper limit - allow large multipliers for stress testing
        
        old_multiplier = self._backend_multiplier
        
        # Don't update if multiplier hasn't changed
        if new_multiplier == old_multiplier:
            return
        
        self._backend_multiplier = new_multiplier
        
        # Clear old arrays
        self._backend_arrays = []
        
        # Create new arrays
        if new_multiplier > 1 and self._method and self._library:
            for i in range(new_multiplier - 1):
                if self._method == 'cupy':
                    backend_gpu, _ = gpu_setup.setup_cupy_arrays(particle_count, self._library)
                elif self._method == 'torch':
                    backend_gpu, _ = gpu_setup.setup_torch_arrays(particle_count, self._library)
                else:
                    continue
                self._backend_arrays.append(backend_gpu)
    
    def run_physics(self, physics_module, params, library):
        """
        Run physics on all backend arrays.
        
        Args:
            physics_module: physics_cupy or physics_torch module
            params: Dictionary with physics parameters
            library: CuPy or PyTorch module
        """
        if not self._backend_arrays:
            return
        
        for backend_gpu in self._backend_arrays:
            if self._method == 'cupy':
                physics_module.run_particle_physics_cupy(backend_gpu, params, library)
            elif self._method == 'torch':
                physics_module.run_particle_physics_torch(backend_gpu, params, library)
    
    def get_multiplier(self) -> int:
        """Get current backend multiplier value."""
        return self._backend_multiplier
    
    def get_array_count(self) -> int:
        """Get number of backend arrays."""
        return len(self._backend_arrays)
    
    def is_initialized(self) -> bool:
        """Check if backend stress manager is initialized."""
        return self._initialized and self._method is not None
    
    def get_particle_count(self) -> int:
        """Get total backend particle count."""
        if not self._initialized:
            return 0
        return self._particle_count * self._backend_multiplier
    
    def scale_particles(self, new_total_count: int):
        """
        Scale backend particles to a new total count.
        
        Args:
            new_total_count: New total backend particle count
        """
        if not self._initialized or self._particle_count == 0:
            return
        
        # Calculate new multiplier based on desired total count
        new_multiplier = max(1, int(new_total_count / self._particle_count))
        if new_multiplier != self._backend_multiplier:
            self.update_multiplier(new_multiplier, self._particle_count)
