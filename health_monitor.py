#!/usr/bin/env python3
"""Cluster Health Monitor - Real-time GPU cluster monitoring.

Maintenance:
- Purpose: CLI entrypoint and small web/server launcher for the project.
- Debug: run `python health_monitor.py web` to start the server; check
    `config.yaml` for configuration. If debugging collectors, import and
    instantiate `monitor.collectors` classes directly.
"""

import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import yaml
import click
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

from monitor.collectors.gpu import GPUCollector
from monitor.collectors.system import SystemCollector
from monitor.collectors.network import NetworkCollector
from monitor.storage.sqlite import MetricsStorage
from monitor.alerting.rules import AlertEngine
from monitor.cli.benchmark_cli import benchmark_cli

from monitor.__version__ import __version__ as _pkg_version


# Preprocess argv so `--cli simulate 15` becomes `--cli simulate --simulate=15`
# and so a bare `--simulate` becomes `--simulate=15` (Click doesn't support
# optional option values). This runs before Click parses options.
try:
    # Handle `--cli simulate 15` -> insert `--simulate=15` token
    if '--cli' in sys.argv:
        i = sys.argv.index('--cli')
        # If user wrote `--cli simulate 15`, replace the numeric token with --simulate=<n>
        if i + 1 < len(sys.argv) and sys.argv[i + 1] == 'simulate' and i + 2 < len(sys.argv):
            tok = sys.argv[i + 2]
            if str(tok).lstrip('-').isdigit():
                sys.argv[i + 2] = f"--simulate={tok}"
        # If user provided no argument to --cli or next token is another option,
        # default to monitor mode by converting `--cli` to `--cli=monitor`.
        if i + 1 >= len(sys.argv) or str(sys.argv[i + 1]).startswith('-'):
            sys.argv[i] = '--cli=monitor'

    # Handle bare `--simulate` (no value) -> default to 15 seconds
    if '--simulate' in sys.argv:
        j = sys.argv.index('--simulate')
        # If there's no token after or the next token is another option, replace
        # the `--simulate` entry with `--simulate=15` so Click will parse it.
        if j + 1 >= len(sys.argv) or str(sys.argv[j + 1]).startswith('-'):
            sys.argv[j] = '--simulate=15'
except Exception:
    pass

console = Console()

BANNER = f"""
╔══════════════════════════════════════════════════╗
║          CLUSTER HEALTH MONITOR v{_pkg_version}  ║
║         Real-time GPU Cluster Monitoring         ║
╚══════════════════════════════════════════════════╝
"""

DEFAULT_CONFIG = {
    'cluster': {
        'name': 'Local System',
        'nodes': []
    },
    'monitoring': {
        'interval_seconds': 5,
        'history_retention_hours': 168
    },
    'alerts': {
        'gpu_temperature_warn': 80,
        'gpu_temperature_critical': 90,
        'gpu_memory_usage_warn': 90
    },
    'web': {
        'host': '127.0.0.1',
        'port': 8090
    },
    'storage': {
        'type': 'sqlite',
        'path': './metrics.db'
    }
}


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dicts."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: Optional[str]) -> dict:
    """Load config from file or use defaults."""
    import copy
    config = copy.deepcopy(DEFAULT_CONFIG)
    
    # Try default config.yaml if no path specified
    if not config_path:
        # Look for config.yaml in same directory as this script
        script_dir = Path(__file__).parent
        default_config = script_dir / 'config.yaml'
        if default_config.exists():
            config_path = default_config
    else:
        config_path = Path(config_path)
    
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
            if user_config:
                config = deep_merge(config, user_config)
                console.print(f"[dim]Loaded config from: {config_path}[/dim]")
    
    return config


def collect_metrics() -> dict:
    """Collect metrics from local system."""
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'hostname': None,
        'gpus': [],
        'system': {},
        'status': 'healthy'
    }
    
    # System metrics
    try:
        sys_collector = SystemCollector()
        metrics['system'] = sys_collector.collect()
        metrics['hostname'] = metrics['system'].get('hostname', 'unknown')
    except Exception as e:
        metrics['system'] = {'error': str(e)}
    
    # GPU metrics
    try:
        gpu_collector = GPUCollector()
        metrics['gpus'] = gpu_collector.collect()
    except Exception as e:
        metrics['gpus'] = [{'error': str(e)}]
    
    return metrics


def create_dashboard(metrics: dict, alerts: list) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    
    # Header
    layout["header"].update(Panel(
        f"[bold cyan]CLUSTER HEALTH MONITOR[/bold cyan] | "
        f"Node: [green]{metrics.get('hostname', 'N/A')}[/green] | "
        f"Last Update: {datetime.now().strftime('%H:%M:%S')} | "
        f"Alerts: [{'red' if alerts else 'green'}]{len(alerts)}[/]",
        style="bold"
    ))
    
    # Main content
    layout["main"].split_row(
        Layout(name="gpus", ratio=2),
        Layout(name="system", ratio=1)
    )
    
    # GPU Table
    gpu_table = Table(title="GPU Status", show_header=True, expand=True)
    gpu_table.add_column("GPU", style="cyan")
    gpu_table.add_column("Utilization", style="green")
    gpu_table.add_column("Memory", style="yellow")
    gpu_table.add_column("Temp", style="magenta")
    gpu_table.add_column("Power", style="blue")
    
    for gpu in metrics.get('gpus', []):
        if 'error' in gpu:
            gpu_table.add_row("Error", str(gpu['error']), "", "", "")
            continue
            
        util = gpu.get('utilization', 0)
        util_bar = "█" * (util // 10) + "░" * (10 - util // 10)
        
        mem_used = gpu.get('memory_used', 0)
        mem_total = gpu.get('memory_total', 1)
        mem_pct = (mem_used / mem_total * 100) if mem_total > 0 else 0
        
        temp = gpu.get('temperature', 0)
        temp_style = "green" if temp < 70 else "yellow" if temp < 85 else "red"
        
        gpu_table.add_row(
            f"GPU {gpu.get('index', '?')}",
            f"{util_bar} {util}%",
            f"{mem_used/1024:.1f}/{mem_total/1024:.1f} GB ({mem_pct:.0f}%)",
            f"[{temp_style}]{temp}°C[/{temp_style}]",
            f"{gpu.get('power', 0):.0f}W"
        )
    
    layout["gpus"].update(Panel(gpu_table, title="GPU Metrics"))
    
    # System Info
    sys_info = metrics.get('system', {})
    system_content = (
        f"[bold]CPU:[/bold] {sys_info.get('cpu_percent', 0):.1f}%\n"
        f"[bold]RAM:[/bold] {sys_info.get('memory_used_gb', 0):.1f}/{sys_info.get('memory_total_gb', 0):.1f} GB\n"
        f"[bold]Disk:[/bold] {sys_info.get('disk_used_gb', 0):.1f}/{sys_info.get('disk_total_gb', 0):.1f} GB\n"
        f"[bold]Load:[/bold] {', '.join(map(str, sys_info.get('load_avg', [0,0,0])))}"
    )
    layout["system"].update(Panel(system_content, title="System"))
    
    # Footer
    if alerts:
        alert_text = " | ".join([f"[red]{a['message']}[/red]" for a in alerts[:3]])
        layout["footer"].update(Panel(alert_text, title="Active Alerts"))
    else:
        layout["footer"].update(Panel("[green]All systems healthy[/green]", title="Status"))
    
    return layout


async def run_web_server(config: dict):
    try:
        from monitor.api.server import create_app
        import uvicorn
        
        app = create_app(config)
        
        console.print(f"\n[green]Starting web dashboard at http://{config['web']['host']}:{config['web']['port']}[/green]")
        
        uvicorn_config = uvicorn.Config(
            app,
            host=config['web']['host'],
            port=config['web']['port'],
            log_level="warning"
        )
        server = uvicorn.Server(uvicorn_config)
        await server.serve()
        
    except ImportError as e:
        console.print(f"[yellow]Warning: Could not start web server: {e}[/yellow]")
        console.print("[yellow]Install fastapi and uvicorn for web dashboard support.[/yellow]")


async def run_cli_monitor(config: dict):
    storage = MetricsStorage(config['storage']['path'])
    await storage.initialize()
    
    alert_engine = AlertEngine(config.get('alerts', {}))
    
    with Live(console=console, refresh_per_second=1) as live:
        while True:
            try:
                # Collect metrics
                metrics = collect_metrics()
                
                # Check alerts
                alerts = alert_engine.check(metrics)
                
                # Store metrics
                await storage.store(metrics)
                
                # Update dashboard
                dashboard = create_dashboard(metrics, alerts)
                live.update(dashboard)
                
                await asyncio.sleep(config['monitoring']['interval_seconds'])
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                await asyncio.sleep(5)


def _run_app(config_path, port, nodes, once, web_mode=False, cli_mode=False):
    """Helper to run main application logic."""
    # If the user requested admin mode via --admin in argv, and the process is not elevated,
    # attempt to relaunch elevated (UAC on Windows, sudo on POSIX). This check is done here
    # to cover both top-level and subcommand usages (e.g. `health_monitor.py web --admin`).
    try:
        import sys
        import platform
        import os
        def _is_elevated():
            try:
                if platform.system() == 'Windows':
                    import ctypes
                    return bool(ctypes.windll.shell32.IsUserAnAdmin())
                else:
                    return (os.geteuid() == 0)
            except Exception:
                return False

        if '--admin' in (sys.argv[1:] if len(sys.argv) > 1 else []) and not _is_elevated():
            # Attempt relaunch elevated. Use ShellExecuteW on Windows, fallback to PowerShell;
            # on POSIX try sudo exec.
            try:
                if platform.system() == 'Windows':
                    try:
                        import ctypes
                        params = '"' + os.path.abspath(sys.argv[0]) + '"'
                        other_args = [a for a in sys.argv[1:]]
                        if other_args:
                            params += ' ' + ' '.join(str(a) for a in other_args)
                        ret = ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, params, None, 1)
                        try:
                            ok = int(ret) > 32
                        except Exception:
                            ok = False
                        if ok:
                            print('Relaunching elevated, exiting original process')
                            try: os._exit(0)
                            except Exception: pass
                    except Exception:
                        pass

                    # PowerShell fallback
                    try:
                        import subprocess
                        def _ps_quote(s):
                            return "'" + str(s).replace("'", "''") + "'"
                        ps_args = [os.path.abspath(sys.argv[0])] + list(sys.argv[1:])
                        arglist_literal = ','.join(_ps_quote(a) for a in ps_args)
                        ps_cmd = [
                            'powershell', '-NoProfile', '-NonInteractive', '-Command',
                            f"Start-Process -FilePath '{sys.executable}' -ArgumentList {arglist_literal} -Verb RunAs"
                        ]
                        proc = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=15)
                        if proc.returncode == 0:
                            try: os._exit(0)
                            except Exception: pass
                    except Exception:
                        pass

                else:
                    # POSIX: try exec via sudo
                    try:
                        print('Attempting to relaunch with sudo...')
                        os.execvp('sudo', ['sudo', sys.executable, os.path.abspath(sys.argv[0])] + list(sys.argv[1:]))
                    except Exception:
                        pass
            except Exception:
                pass
    except Exception:
        pass

    console.print(BANNER, style="bold cyan")
    
    # Load configuration
    cfg = load_config(config_path)
    
    # CLI port overrides config only if explicitly specified
    if port is not None:
        cfg['web']['port'] = port
    
    if nodes:
        cfg['cluster']['nodes'] = [{'hostname': n.strip()} for n in nodes.split(',')]

    # Single collection mode
    if once:
        metrics = collect_metrics()
        console.print_json(data=metrics)
        return

    async def main():
        if web_mode and cli_mode:
            # Run both concurrently
            console.print("[cyan]Starting both web server and CLI dashboard...[/cyan]")
            web_task = asyncio.create_task(run_web_server(cfg))
            cli_task = asyncio.create_task(run_cli_monitor(cfg))
            await asyncio.gather(web_task, cli_task)
        elif web_mode:
            await run_web_server(cfg)
        elif cli_mode:
            await run_cli_monitor(cfg)
        else:
            # Default to CLI if no mode is specified on the root command
            await run_cli_monitor(cfg)

    # Run
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")


def _is_elevated():
    try:
        import platform
        if platform.system() == 'Windows':
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:
            import os
            return (os.geteuid() == 0)
    except Exception:
        return False


def _relaunch_elevated():
    try:
        import platform
        import sys
        import os
        import subprocess
        import shlex
        script = os.path.abspath(sys.argv[0])
        args = sys.argv[1:]
        # Ensure --admin present
        if '--admin' not in args:
            args = args + ['--admin']

        if platform.system() == 'Windows':
            try:
                import ctypes
                params = '"' + script + '"'
                if args:
                    params += ' ' + ' '.join(str(a) for a in args)
                ret = ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, params, None, 1)
                try:
                    ok = int(ret) > 32
                except Exception:
                    ok = False
                if ok:
                    # launched elevated; exit current process
                    print('Relaunching elevated, exiting original process')
                    try: os._exit(0)
                    except SystemExit: raise
                    except Exception: pass
                else:
                    print('ShellExecuteW failed to elevate (ret=' + str(ret) + ')')
            except Exception as e:
                print('Windows elevation exception:', e)

            # PowerShell fallback
            try:
                def _ps_quote(s):
                    return "'" + str(s).replace("'", "''") + "'"
                ps_args = [script] + list(args)
                arglist_literal = ','.join(_ps_quote(a) for a in ps_args)
                ps_cmd = [
                    'powershell', '-NoProfile', '-NonInteractive', '-Command',
                    f"Start-Process -FilePath '{sys.executable}' -ArgumentList {arglist_literal} -Verb RunAs"
                ]
                proc = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=15)
                if proc.returncode == 0:
                    try: os._exit(0)
                    except Exception: pass
                else:
                    print('PowerShell elevation failed:', proc.returncode, proc.stderr)
            except Exception as e:
                print('PowerShell fallback exception:', e)

        else:
            # POSIX: try exec via sudo
            try:
                print('Attempting to relaunch with sudo...')
                os.execvp('sudo', ['sudo', sys.executable, script] + list(args))
            except Exception as e:
                print('sudo relaunch failed:', e)

    except Exception as e:
        print('Relaunch elevation error:', e)


@click.group(invoke_without_command=True)
@click.option('--config', '-c', type=click.Path(), help='Configuration file path. If omitted, the bundled `config.yaml` (if present) or defaults are used.')
@click.option('--port', '-p', type=int, help='Web server port (overrides `web.port` from the config).')
@click.option('--nodes', type=str, help='Comma-separated list of hostnames to monitor (overrides `cluster.nodes` in config).')
@click.option('--update', is_flag=True, help='Check for updates and optionally install them. Interactive prompt will appear if an update is available.')
@click.option('--admin', is_flag=True, help='Start in administrative mode (attempts to relaunch elevated privileges where supported).')
@click.option('--once', is_flag=True, help='Collect metrics once and print JSON, then exit. Useful for scripting and CI checks.')
@click.option('--monitor', is_flag=True, help='Start the terminal monitor directly (same as `cli` subcommand).')
@click.option('--benchmark', is_flag=True, help='Run the benchmark subcommand directly; any following args are forwarded to `benchmark`.')
@click.option('--simulate', type=int, default=None, help='Run a particle simulation for N seconds (provide seconds). If no seconds given, defaults to 15s. If additional args are present after the duration they are forwarded to `benchmark`.')
@click.option('--cli', 'cli_mode', type=str, help='Run the chosen CLI mode directly (monitor|benchmark|simulate). When choosing simulate, pair with `--simulate N` or `--cli simulate 15` (both supported).')
@click.pass_context
def cli(ctx, config, port, nodes, update, admin, once, monitor, benchmark, simulate, cli_mode): # Line 321
    """Cluster Health Monitor — monitor and benchmark tools.

    See monitor/, monitor/benchmark/, and monitor/api/ for implementation.
    """

    # Minimal entry: populate context and delegate to runtime runner.
    ctx.obj = {'config_path': config, 'admin': admin}

    # If user passed --cli, map it to the existing flags to preserve behavior.
    if cli_mode:
        if cli_mode == 'monitor':
            monitor = True
        elif cli_mode == 'benchmark':
            benchmark = True
        elif cli_mode == 'simulate':
            # If simulate duration not provided explicitly, default to 15s.
            if simulate is None:
                simulate = 15

    # If user requested terminal monitor directly
    if monitor:
        if admin and '--admin' not in sys.argv:
            sys.argv.append('--admin')
        _run_app(config, port=None, nodes=nodes, once=once, cli_mode=True)
        return

    # If user requested benchmark directly, spawn a subprocess that runs
    # this script with the `benchmark` subcommand while forwarding remaining args.
    if benchmark:
        import subprocess, os
        script = os.path.abspath(sys.argv[0])
        # forward args after the '--benchmark' token, if any
        try:
            idx = sys.argv.index('--benchmark')
            extra = sys.argv[idx+1:]
        except ValueError:
            extra = []
        cmd = [sys.executable, script, 'benchmark'] + extra
        subprocess.run(cmd)
        return

    # If user requested a direct simulation run (possibly with a duration)
    if simulate is not None:
        # Examine raw argv to determine whether additional CLI args were provided
        # after the --simulate token. If extra non-duration args exist we forward
        # to the benchmark subprocess to preserve full CLI parsing.
        try:
            idx = sys.argv.index('--simulate')
        except ValueError:
            idx = None

        duration_from_argv = None
        extra_after = []
        if idx is not None:
            # If next token looks like an integer, treat it as the duration token
            if idx + 1 < len(sys.argv) and sys.argv[idx + 1].lstrip('-').isdigit():
                try:
                    duration_from_argv = int(sys.argv[idx + 1])
                except Exception:
                    duration_from_argv = None
                extra_after = sys.argv[idx + 2:]
            else:
                extra_after = sys.argv[idx + 1:]

        # If there are extra args beyond an optional single numeric duration, forward
        if extra_after:
            import subprocess, os
            script = os.path.abspath(sys.argv[0])
            # Recreate forwarded command: keep any provided duration token as-is
            forward_args = ['benchmark', '--type', 'particle'] + extra_after
            subprocess.run([sys.executable, script] + forward_args)
            return

        # Determine final duration preference: CLI option takes precedence,
        # else numeric token from argv, else default preset
        sim_seconds = simulate if simulate is not None else duration_from_argv

        try:
            from monitor.benchmark.config import BenchmarkConfig
            from monitor.benchmark.runner import GPUBenchmark
            import threading
            import sys as _sys
            import datetime as _dt

            console.print('[cyan]Starting local particle simulation (visualizer)...[/cyan]')
            cfg = BenchmarkConfig.from_mode('standard', benchmark_type='particle')
            cfg.mode = 'simulation'
            if sim_seconds and isinstance(sim_seconds, int) and sim_seconds > 0:
                cfg.duration_seconds = sim_seconds

            bench = GPUBenchmark()

            # Run benchmark in background thread so we can poll status
            results_holder = {}

            def _runner():
                try:
                    res = bench.run(cfg, visualize=True)
                    results_holder['results'] = res
                except Exception as _e:
                    results_holder['error'] = str(_e)

            th = threading.Thread(target=_runner, daemon=True)
            th.start()

            # Give pygame a moment to initialize and print its startup message
            time.sleep(1.2)

            # Live one-line metrics (colored for PowerShell via Rich)
            from rich.text import Text
            while th.is_alive() or getattr(bench, 'running', False):
                try:
                    status = bench.get_status()
                    fps = int(status.get('fps', 0) or 0)
                    gpu_util = int(status.get('gpu_util', 0) or 0)
                    iterations = int(status.get('iterations', 0) or 0)
                    progress = int(status.get('progress', 0) or 0)
                    timestamp = _dt.datetime.now().strftime('%H:%M:%S')

                    txt = Text()
                    txt.append(f"[{timestamp}] ", style="dim")
                    txt.append("FPS:", style="bold")
                    txt.append(f"{fps:4d} ", style="green")
                    txt.append("GPU:", style="bold")
                    gpu_style = "green" if gpu_util < 50 else "yellow" if gpu_util < 80 else "red"
                    txt.append(f"{gpu_util:3d}% ", style=gpu_style)
                    txt.append("Iter:", style="bold")
                    txt.append(f"{iterations:8d} ", style="cyan")
                    txt.append("Prog:", style="bold")
                    txt.append(f"{progress:3d}%", style="magenta")

                    console.print(txt, end='\r')
                except Exception:
                    pass
                time.sleep(1)

            # Ensure newline after live line
            print()

            # Fetch results or error
            if 'error' in results_holder:
                console.print(f"[red]Simulation failed: {results_holder['error']}[/red]")
                return

            results = results_holder.get('results') or getattr(bench, 'results', {})

            # Print a formatted concise summary
            duration_actual = results.get('duration_actual_sec', results.get('duration', cfg.duration_seconds))
            completed = results.get('completed_full', False)
            iterations_done = results.get('iterations_completed', getattr(bench.stress_worker, 'iterations', 0) if getattr(bench, 'stress_worker', None) else 0)
            stop_reason = results.get('stop_reason', 'N/A')

            console.print('\n[bold green]Simulation Summary[/bold green]')
            console.print(f"- Duration: [cyan]{duration_actual}s[/cyan]")
            console.print(f"- Completed: [cyan]{completed}[/cyan]")
            console.print(f"- Iterations: [cyan]{iterations_done}[/cyan]")

            if 'performance' in results and isinstance(results.get('performance'), dict):
                perf = results.get('performance', {})
                if 'steps_per_second' in perf:
                    console.print(f"- Avg steps/sec: [cyan]{perf.get('steps_per_second',0):.1f}[/cyan]")

            console.print(f"- Stop reason: [yellow]{stop_reason}[/yellow]")

        except Exception as e:
            console.print(f"[red]Failed to start simulation inline: {e}[/red]")
        return

    if ctx.invoked_subcommand is None:
        if admin and '--admin' not in sys.argv:
            sys.argv.append('--admin')
        _run_app(config, port=port, nodes=nodes, once=once, web_mode=True)

@cli.command()
@click.option('--config', '-c', type=click.Path(), help='Path to configuration file to use for the web server.')
@click.option('--port', '-p', type=int, help='Web server port (overrides config).')
@click.option('--admin', is_flag=True, help='Start web server in administrative mode (enables privileged actions).')
@click.option('--once', is_flag=True, help='Collect metrics once, print JSON, and exit (useful for testing).')
@click.pass_context
def web(ctx, config, port, admin, once):
    """Launch the web dashboard (FastAPI + Uvicorn)."""
    # If called as a subcommand with --admin, ensure argv contains --admin so server detection sees it
    import sys
    if admin and '--admin' not in sys.argv:
        sys.argv.append('--admin')
    # Also propagate admin from top-level invocation if present in ctx.obj
    try:
        if not admin and ctx and isinstance(ctx.obj, dict) and ctx.obj.get('admin'):
            if '--admin' not in sys.argv:
                sys.argv.append('--admin')
    except Exception:
        pass

    # If a config path is provided to the subcommand, prefer it over context
    config_path = ctx.obj.get('config_path') if ctx and isinstance(ctx.obj, dict) else None
    if config:
        config_path = config

    _run_app(config_path, port, nodes=None, once=once, web_mode=True)

@cli.command(name="cli")
@click.option('--config', '-c', type=click.Path(), help='Path to configuration file to use for the terminal dashboard.')
@click.option('--nodes', type=str, help='Comma-separated list of hostnames to monitor (overrides config).')
@click.option('--once', is_flag=True, help='Collect metrics once, print JSON, and exit (for scripting).')
@click.pass_context
def term(ctx, config, nodes, once):
    """Launch the interactive terminal dashboard.

    Shows live cluster metrics using the `monitor` package (collectors, storage, and utils).
    For running benchmarks or simulations use the `benchmark` subcommand (implementations in
    `monitor/benchmark/`). Use `health_monitor.py benchmark --help` for options.
    """
    # `--nodes` is supported and parsed as a comma-separated list; it
    # overrides `cluster.nodes` from the config when provided.
    config_path = ctx.obj.get('config_path') if ctx and isinstance(ctx.obj, dict) else None
    if config:
        config_path = config
    _run_app(config_path, port=None, nodes=nodes, once=once, cli_mode=True)

@cli.command()
def refresh():
    """Refresh feature detection cache (run after installing GPU libraries)."""
    from monitor.utils import detect_features
    import os
    from pathlib import Path
    
    cache_file = Path('.features_cache')
    if cache_file.exists():
        os.remove(cache_file)
        console.print("[yellow]Removed old cache[/yellow]")
    
    # Run diagnostics first
    console.print("\n[cyan]Running diagnostics...[/cyan]")
    
    # Test CuPy
    try:
        import cupy as cp
        cp.cuda.Device(0).compute_capability
        console.print("  CuPy: [green]OK[/green]")
    except ImportError:
        console.print("  CuPy: [yellow]Not installed[/yellow]")
    except Exception as e:
        console.print(f"  CuPy: [red]Error - {str(e)}[/red]")
    
    # Test PyTorch
    try:
        import torch
        if torch.cuda.is_available():
            console.print(f"  PyTorch: [green]OK (CUDA {torch.version.cuda})[/green]")
        else:
            console.print("  PyTorch: [yellow]Installed but CUDA not available[/yellow]")
            console.print(f"           [dim]PyTorch version: {torch.__version__}[/dim]")
    except ImportError:
        console.print("  PyTorch: [yellow]Not installed[/yellow]")
    except Exception as e:
        console.print(f"  PyTorch: [red]Error - {str(e)}[/red]")
    
    console.print("\n[cyan]Detecting features...[/cyan]")
    features = detect_features(force=True)
    
    console.print("\n[green]Feature Detection Results:[/green]")
    console.print(f"  NVIDIA GPU: {'[green]Available[/green]' if features.get('nvidia_smi') else '[red]Not found[/red]'}")
    console.print(f"  CuPy: {'[green]Available[/green]' if features.get('cupy') else '[yellow]Not installed[/yellow]'}")
    console.print(f"  PyTorch: {'[green]Available[/green]' if features.get('torch') else '[yellow]Not installed[/yellow]'}")
    console.print(f"  GPU Benchmark: {'[green]Enabled[/green]' if features.get('gpu_benchmark') else '[red]Disabled[/red]'}")
    
    if not features.get('gpu_benchmark'):
        console.print("\n[yellow]GPU Benchmark is DISABLED because:[/yellow]")
        if not features.get('cupy') and not features.get('torch'):
            console.print("  [red]Neither CuPy nor PyTorch with CUDA is available[/red]")
        console.print("\n[cyan]To fix:[/cyan]")
        console.print("  1. Install a GPU library:")
        console.print("     pip install \"cupy-cuda12x>=13.0.0\"")
        console.print("     OR")
        console.print("     pip install torch --index-url https://download.pytorch.org/whl/cu121")
        console.print("  2. Run 'python health_monitor.py refresh' again")
    else:
        console.print("\n[green]All GPU features enabled![/green]")
    
    console.print("\n[cyan]Cache updated successfully![/cyan]\n")



if __name__ == '__main__':
    cli.add_command(benchmark_cli)
    cli()
