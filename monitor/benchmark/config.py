"""Benchmark configuration management."""

from dataclasses import dataclass


@dataclass
class BenchmarkConfig:
    """Configuration for GPU benchmark runs."""
    
    mode: str = "fixed"
    benchmark_type: str = "gemm"
    duration_seconds: int = 30
    memory_limit_mb: int = 0
    temp_limit_c: int = 85
    power_limit_w: int = 0
    sample_interval_ms: int = 500
    matrix_size: int = 2048
    num_particles: int = 30000  # Reduced for better sustained performance
    auto_scale: bool = False
    target_gpu_util: int = 98
    
    @classmethod
    def from_mode(cls, mode: str, benchmark_type: str = "gemm") -> 'BenchmarkConfig':
        """Create configuration from preset mode."""
        presets = {
            'quick': cls(
                mode='quick',
                benchmark_type=benchmark_type,
                duration_seconds=15,
                temp_limit_c=85,
                sample_interval_ms=500
            ),
            'standard': cls(
                mode='standard',
                benchmark_type=benchmark_type,
                duration_seconds=60,
                temp_limit_c=85,
                sample_interval_ms=500
            ),
            'stress': cls(
                mode='stress',
                benchmark_type=benchmark_type,
                duration_seconds=180,
                temp_limit_c=92,
                sample_interval_ms=250
            ),
        }
        return presets.get(mode, cls(mode='standard', benchmark_type=benchmark_type))
    
    @classmethod
    def custom(
        cls,
        duration: int,
        temp_limit: int,
        memory_limit: int = 0,
        power_limit: int = 0,
        benchmark_type: str = "gemm",
        matrix_size: int = 2048,
        num_particles: int = 100000
    ) -> 'BenchmarkConfig':
        """Create custom configuration."""
        return cls(
            mode='custom',
            benchmark_type=benchmark_type,
            duration_seconds=duration,
            temp_limit_c=temp_limit,
            memory_limit_mb=memory_limit,
            power_limit_w=power_limit,
            sample_interval_ms=500,
            matrix_size=matrix_size,
            num_particles=num_particles
        )
