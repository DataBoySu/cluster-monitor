
"""CLI entry for benchmark utilities.

Maintenance:
- Purpose: provide a small CLI wrapper for running benchmarks from terminal.
- Debug: use `--help` to see available options; the CLI calls into
    `monitor.benchmark` modules and forwards configuration.
"""

import click
import time
import threading

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table

from monitor.benchmark import GPUBenchmark, BenchmarkConfig

console = Console()

@click.command(name='benchmark')
@click.option('--type', '-t', 'bench_type', 
              type=click.Choice(['gemm', 'particle'], case_sensitive=False),
              default='gemm', help='Benchmark type: gemm (matrix multiply) or particle simulation')
@click.option('--mode', '-m',
              type=click.Choice(['fixed', 'stress'], case_sensitive=False),
              default='fixed', help='fixed=use specified sizes, stress=auto-scale to push GPU limits')
@click.option('--duration', '-d', type=int, default=30, help='Duration in seconds')
@click.option('--matrix-size', type=int, default=2048, help='Matrix size for GEMM (fixed mode)')
@click.option('--particles', type=int, default=100000, help='Number of particles (fixed mode)')
@click.option('--temp-limit', type=int, default=0, help='Stop if temperature exceeds this (0=no limit)')
@click.option('--power-limit', type=int, default=0, help='Stop if power exceeds this in watts (0=no limit)')
@click.option('--save-baseline', is_flag=True, help='Save results as baseline (auto-saved if completed)')
@click.option('--compare-baseline', is_flag=True, help='Compare with existing baseline')
@click.option('--visualize', '-v', is_flag=True, help='Show particle visualization window (particles only, requires pygame)')
def benchmark_cli(bench_type, mode, duration, matrix_size, particles, temp_limit, power_limit, save_baseline, compare_baseline, visualize):
    """Run GPU benchmarks and simulations from the terminal.

Implementation: see monitor/benchmark/ for the workload implementations and configs.
"""
    from health_monitor import BANNER
    console.print(BANNER, style="bold cyan")

    # Create benchmark config
    auto_scale = (mode == 'stress')
    config = BenchmarkConfig(
        mode=mode,
        benchmark_type=bench_type,
        duration_seconds=duration,
        matrix_size=matrix_size,
        num_particles=particles,
        temp_limit_c=temp_limit,
        power_limit_w=power_limit,
        auto_scale=auto_scale,
        target_gpu_util=98,
    )

    # Initialize benchmark
    bench = GPUBenchmark()

    # Get GPU info
    gpu_info = bench.get_gpu_info()
    console.print(f"\n[cyan]GPU:[/cyan] {gpu_info.get('name', 'Unknown')}")
    console.print(f"[cyan]Memory:[/cyan] {gpu_info.get('memory_total_mb', 0):.0f} MB")
    console.print(f"[cyan]Driver:[/cyan] {gpu_info.get('driver_version', 'Unknown')}")

    console.print(f"[cyan]Mode:[/cyan] {'STRESS (auto-scaling to push GPU limits)' if auto_scale else 'FIXED (using predefined sizes)'}")

    # Get baseline if comparing
    baseline = None
    if compare_baseline:
        baseline = bench.get_baseline(bench_type)
        if baseline:
            console.print(f"\n[green]Baseline found:[/green] {baseline['timestamp']}")
            console.print(f"  Benchmark: {baseline.get('benchmark_type', bench_type)}")
            console.print(f"  Iterations: {baseline['iterations_completed']}")
            console.print(f"  Avg Time: {baseline['avg_iteration_time_ms']:.2f}ms")
            if baseline.get('full_results', {}).get('performance', {}).get('tflops'):
                console.print(f"  TFLOPS: {baseline['full_results']['performance']['tflops']}")
            elif baseline.get('full_results', {}).get('performance', {}).get('steps_per_second'):
                console.print(f"  Steps/sec: {baseline['full_results']['performance']['steps_per_second']:.1f}")
        else:
            console.print(f"[yellow]No baseline found for {bench_type.upper()} benchmark on this GPU[/yellow]")

    console.print(f"\n[bold green]Starting {bench_type.upper()} benchmark for {duration} seconds...[/bold green]")

    if visualize and bench_type != 'particle':
        console.print("[yellow]Note: Visualization only available for particle benchmarks, ignoring --visualize flag[/yellow]")
        visualize = False

    if visualize:
        console.print("[cyan]Visualization enabled - window will open during benchmark[/cyan]")

    # Run benchmark with progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]{bench_type.upper()} Benchmark", total=100)

        bench_thread = threading.Thread(target=lambda: bench.start(config, visualize=visualize))
        bench_thread.start()

        while bench.running:
            status = bench.get_status()
            fps = status.get('fps', 0.0)
            gpu = status.get('gpu_util', 0)
            workload = status.get('workload_type', bench_type)
            iters = status['iterations']

            desc = f"[cyan]FPS:{fps:5.1f} GPU:{gpu:3.0f}%  {workload} - {iters} iterations"
            progress.update(task, completed=status['progress'], description=desc)
            time.sleep(0.5)

        bench_thread.join()
        progress.update(task, completed=100)

    results = bench.get_results()

    if results.get('status') == 'failed':
        console.print(f"\n[red]Benchmark failed:[/red] {results.get('error', 'Unknown error')}")
        return

    # Check if we have minimal results to display
    if 'error' in results and 'duration_actual_sec' not in results:
        console.print(f"\n[red]Benchmark error:[/red] {results.get('error', 'Unknown error')}")
        return

    console.print("\n[bold green]Benchmark Complete[/bold green]")
    console.print(f"[dim]Stop reason: {results.get('stop_reason', 'Unknown')}[/dim]\n")

    table = Table(title="Benchmark Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="yellow")
    if baseline:
        table.add_column("Baseline", justify="right", style="dim")
        table.add_column("Δ", justify="right")

    table.add_row("Workload", results.get('workload_type', 'N/A'))
    table.add_row("Duration", f"{results.get('duration_actual_sec', 0):.1f}s")

    # Only add detailed metrics if we have valid samples
    if 'iterations_completed' in results:
        table.add_row("Iterations", f"{results['iterations_completed']:,}")
        table.add_row("Avg Iteration Time", f"{results.get('avg_iteration_time_ms', 0):.2f}ms", 
                      f"{baseline.get('avg_iteration_time_ms', 0):.2f}ms" if baseline else "",
                      f"{((results['avg_iteration_time_ms'] - baseline['avg_iteration_time_ms']) / baseline['avg_iteration_time_ms'] * 100):+.1f}%" if baseline and baseline.get('avg_iteration_time_ms') else "")
        table.add_row("Iterations/sec", f"{results.get('iterations_per_second', 0):.1f}")

    perf = results.get('performance', {})
    if 'tflops' in perf:
        baseline_tflops = baseline.get('full_results', {}).get('performance', {}).get('tflops', 0) if baseline else 0
        table.add_row("TFLOPS", f"{perf['tflops']:.3f}",
                     f"{baseline_tflops:.3f}" if baseline_tflops else "",
                     f"{((perf['tflops'] - baseline_tflops) / baseline_tflops * 100):+.1f}%" if baseline_tflops else "")
        table.add_row("GFLOPS", f"{perf['gflops']:.1f}")
    elif 'steps_per_second' in perf:
        table.add_row("Steps/sec", f"{perf['steps_per_second']:.1f}")
        table.add_row("Particles/sec", f"{perf['particles_updated_per_second']:,.0f}")

    # Only add GPU metrics if we have them
    if 'utilization' in results:
        table.add_section()
        table.add_row("GPU Utilization", f"{results['utilization']['avg']:.1f}% (min: {results['utilization']['min']}, max: {results['utilization']['max']})")
        table.add_row("Temperature", f"{results['temperature_c']['avg']:.1f}°C (max: {results['temperature_c']['max']}°C)")
        table.add_row("Power Draw", f"{results['power_w']['avg']:.1f}W (max: {results['power_w']['max']}W)")
        table.add_row("Memory Used", f"{results['memory_used_mb']['avg']:.0f} MB")

    if 'scores' in results:
        table.add_section()
        scores = results.get('scores', {})
        table.add_row("Stability Score", f"{scores.get('stability', 0)}/100")
        table.add_row("Thermal Score", f"{scores.get('thermal', 0)}/100")
        table.add_row("Performance Score", f"{scores.get('performance', 0)}/100")
        table.add_row("Overall Score", f"{scores.get('overall', 0)}/100")

    console.print(table)

    if results.get('saved_as_baseline'):
        console.print(f"\n[green]Results saved as new baseline[/green]")
    elif results.get('completed_full'):
        console.print(f"\n[dim]Baseline auto-saved on completion[/dim]")