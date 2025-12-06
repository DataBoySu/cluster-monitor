"""API router for benchmark-related endpoints."""

import threading
from fastapi import APIRouter

from monitor.benchmark.gpu_bench import BenchmarkConfig, get_benchmark_instance

router = APIRouter(
    prefix="/api/benchmark",
    tags=["Benchmark"],
)

# Benchmark state should be managed here
benchmark_instance = get_benchmark_instance()
benchmark_thread = None
benchmark_lock = threading.Lock()

@router.post("/start")
async def start_benchmark(
    mode: str = "fixed",
    benchmark_type: str = "gemm",
    duration: int = 30,
    temp_limit: int = 85,
    memory_limit: int = 0,
    power_limit: int = 0,
    matrix_size: int = 2048,
    num_particles: int = 100000,
    auto_scale: bool = False
):
    global benchmark_thread
    with benchmark_lock:
        if benchmark_instance.running:
            return {'status': 'already_running', 'progress': benchmark_instance.progress}
        
        bench_config = BenchmarkConfig(
            mode=mode,
            benchmark_type=benchmark_type,
            duration_seconds=duration,
            temp_limit_c=temp_limit,
            memory_limit_mb=memory_limit,
            power_limit_w=power_limit,
            matrix_size=matrix_size,
            num_particles=num_particles,
            auto_scale=auto_scale,
            target_gpu_util=98
        )
        
        def run_benchmark():
            benchmark_instance.start(bench_config)
        
        benchmark_thread = threading.Thread(target=run_benchmark)
        benchmark_thread.start()
        
        return {'status': 'started', 'message': 'Benchmark started', 'config': bench_config.__dict__}

@router.get("/status")
async def get_benchmark_status():
    return benchmark_instance.get_status()

@router.get("/samples")
async def get_benchmark_samples():
    return {'samples': benchmark_instance.get_samples()}

@router.post("/stop")
async def stop_benchmark():
    with benchmark_lock:
        benchmark_instance.stop()
        return {'status': 'stopping'}

@router.get("/results")
async def get_benchmark_results():
    return benchmark_instance.get_results() if benchmark_instance.results else {'status': 'no_results'}

@router.get("/baseline")
async def get_benchmark_baseline(benchmark_type: str = "gemm"):
    baseline = benchmark_instance.get_baseline(benchmark_type)
    return baseline if baseline else {'status': 'no_baseline'}