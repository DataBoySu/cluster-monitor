"""GPU Benchmark module - modular benchmark system.

Maintenance:
- Purpose: contains the benchmark orchestration and helpers used to run
    GPU stress and workload tests. The submodules implement workloads,
    storage for baselines, and runner orchestration.
- Debug: importables are re-exported here for convenience; if a submodule
    fails to import, check its dependencies (CuPy, PyTorch) and GPU drivers.
"""

from .config import BenchmarkConfig
from .runner import GPUBenchmark, get_benchmark_instance
from .storage import BaselineStorage
from .workloads import GPUStressWorker

__all__ = [
        'BenchmarkConfig',
        'GPUBenchmark',
        'get_benchmark_instance',
        'BaselineStorage',
        'GPUStressWorker',
]
