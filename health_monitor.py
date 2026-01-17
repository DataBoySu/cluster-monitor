import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import shutil

import yaml
import click
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
import socket

from monitor.collectors.gpu import GPUCollector
from monitor.collectors.system import SystemCollector
from monitor.collectors.network import NetworkCollector
from monitor.storage.sqlite import MetricsStorage
from monitor.alerting.rules import AlertEngine
from monitor.cli.benchmark_cli import benchmark_cli

from monitor.__version__ import __version__ as _pkg_version

console = Console()

BANNER = f"""
╔══════════════════════════════════════════════════╗
║                   MyGPU v{_pkg_version}                   ║
║             A GPU Management Utility             ║
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
    metrics = {}

    try:
        gpu_collector = GPUCollector()
        metrics['gpus'] = gpu_collector.collect()
    except Exception as e:
        metrics['gpus'] = [{'error': str(e)}]

    try:
        sys_collector = SystemCollector()
        sys_metrics = sys_collector.collect()
        metrics['system'] = sys_metrics
        # Ensure a hostname is present at top-level for header
        if 'hostname' in sys_metrics and sys_metrics['hostname']:
            metrics['hostname'] = sys_metrics['hostname']
    except Exception as e:
        metrics['system'] = {'error': str(e)}

    # Optionally collect network metrics if collector exists
    try:
        from monitor.collectors.network import NetworkCollector
        net_collector = NetworkCollector()
        metrics['network'] = net_collector.collect()
    except Exception:
        pass

    return metrics


def create_dashboard(metrics: dict, alerts: list) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    
    layout["header"].update(Panel(
        f"[bold cyan]MyGPU[/bold cyan] | "
        f"Node: [green]{metrics.get('hostname', 'N/A')}[/green] | "
        f"Last Update: {datetime.now().strftime('%H:%M:%S')} | "
        f"Alerts: [{'red' if alerts else 'green'}]{len(alerts)}[/]",
        style="bold"
    ))
    
    layout["main"].split_row(
        Layout(name="gpus", ratio=2),
        Layout(name="system", ratio=1)
    )
    
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
    
    sys_info = metrics.get('system', {})
    system_content = (
        f"[bold]CPU:[/bold] {sys_info.get('cpu_percent', 0):.1f}%\n"
        f"[bold]RAM:[/bold] {sys_info.get('memory_used_gb', 0):.1f}/{sys_info.get('memory_total_gb', 0):.1f} GB\n"
        f"[bold]Disk:[/bold] {sys_info.get('disk_used_gb', 0):.1f}/{sys_info.get('disk_total_gb', 0):.1f} GB\n"
        f"[bold]Load:[/bold] {', '.join(map(str, sys_info.get('load_avg', [0,0,0])))}"
    )
    layout["system"].update(Panel(system_content, title="System"))
    
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

    # Use a fixed-size console for the CLI dashboard so it does not expand
    # with the user's terminal window. Width/height can be configured via
    # config['cli'] with keys 'width' and 'height'. Defaults: 120x30.
    cli_cfg = config.get('cli', {}) if isinstance(config, dict) else {}
    # Default to the current terminal width when a width is not configured
    try:
        term_width = shutil.get_terminal_size().columns
    except Exception:
        term_width = 120
    fixed_width = int(cli_cfg.get('width', term_width))
    # Use a smaller default height so the terminal dashboard is compact
    fixed_height = int(cli_cfg.get('height', 18))
    fixed_console = Console(width=fixed_width, height=fixed_height)

    # Do NOT mutate module-level `console`; use `fixed_console` explicitly.
    try:
        # Build an initial dashboard layout once and then update only the
        # inner renderables (Text and Table). We create mutable Text
        # objects for header/system/footer so updating their contents does
        # not recreate the top-level panels, minimizing redraw flicker.
        initial_metrics = collect_metrics()
        initial_alerts = alert_engine.check(initial_metrics)

        dashboard = Layout()
        dashboard.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )

        # Mutable text objects for in-place updates (use markup-aware Text)
        from rich.text import Text

        # Helper: format GPU list as a fixed-width monospaced text grid
        # Use stable fixed column widths to ensure all columns are visible
        def _format_gpu_grid(gpus, total_width: int = None):
            label_w = 6
            util_w = 8
            mem_w = 18
            temp_w = 8
            power_w = 8

            header = f"{ 'GPU':<{label_w}}{ 'Util':>{util_w}}{ 'Memory':>{mem_w}}{ 'Temp':>{temp_w}}{ 'Power':>{power_w}}"
            sep = "-" * (label_w + util_w + mem_w + temp_w + power_w)
            lines = [header, sep]

            for gpu in gpus:
                if 'error' in gpu:
                    lines.append(f"ERR    {str(gpu['error'])}")
                    continue
                idx = f"GPU{gpu.get('index', '?')}"
                util = f"{gpu.get('utilization', 0)}%"
                mem_used = gpu.get('memory_used', 0)
                mem_total = gpu.get('memory_total', 1)
                mem = f"{mem_used/1024:.1f}/{mem_total/1024:.1f}GB"
                temp = f"{gpu.get('temperature', 0)}C"
                power = f"{gpu.get('power', 0):.0f}W"
                lines.append(f"{idx:<{label_w}}{util:>{util_w}}{mem:>{mem_w}}{temp:>{temp_w}}{power:>{power_w}}")

            return Text("\n".join(lines), no_wrap=True)

        # Initial GPU text grid (use dashboard width)
        gpu_text = _format_gpu_grid(initial_metrics.get('gpus', []), fixed_width - 6)

        # Initialize header, system and footer text using markup-aware Text
        node_name = initial_metrics.get('hostname') or socket.gethostname()
        header_text = Text.from_markup(
            f"[bold cyan]MyGPU[/bold cyan] | Node: [green]{node_name}[/green] | "
            f"Last Update: {datetime.now().strftime('%H:%M:%S')} | Alerts: [{'red' if initial_alerts else 'green'}]{len(initial_alerts)}[/]"
        )

        sys_info = initial_metrics.get('system', {})
        system_text = Text.from_markup(
            f"[bold]CPU:[/bold] {sys_info.get('cpu_percent', 0):.1f}%\n"
            f"[bold]RAM:[/bold] {sys_info.get('memory_used_gb', 0):.1f}/{sys_info.get('memory_total_gb', 0):.1f} GB\n"
            f"[bold]Disk:[/bold] {sys_info.get('disk_used_gb', 0):.1f}/{sys_info.get('disk_total_gb', 0):.1f} GB"
        )

        if initial_alerts:
            footer_text = Text.from_markup(" | ".join([f"[red]{a['message']}[/red]" for a in initial_alerts[:3]]))
        else:
            footer_text = Text.from_markup("[green]All systems healthy[/green]")

        dashboard["header"].update(Panel(header_text, style="bold"))
        # Main split: left=GPUs, right=(system over help)
        dashboard["main"].split_row(Layout(name="gpus", ratio=2), Layout(name="right", ratio=1))
        # Allocate explicit sizes so Help panel has visible vertical space
        # Give Help a larger area so the full benchmark flags list is visible
        dashboard["right"].split_column(Layout(name="system", size=6), Layout(name="help", size=12))
        dashboard["gpus"].update(Panel(gpu_text, title="GPU Metrics"))
        dashboard["right"]["system"].update(Panel(system_text, title="System"))
        # Help panel with available CLI commands and flags (populated from repo)
        # Replace Help panel with a focused Benchmark panel (key options only)
        benchmark_text = Text.from_markup(
            "[bold]Benchmark (quick reference)[/bold]\n"
            "Run with: [cyan]python health_monitor.py benchmark -v[/cyan]\n"
            "[bold]Options:[/bold]\n"
            "  [cyan]-t, --type[/cyan]       : gemm | particle \n"
            "  [cyan]-v, --visualize[/cyan]   : Show simulation"
        )
        dashboard["right"]["help"].update(Panel(benchmark_text, title="Benchmark"))
        dashboard["footer"].update(Panel(footer_text, title="Status"))

        with Live(console=fixed_console, refresh_per_second=1) as live:
            live.update(dashboard)

            while True:
                try:
                    metrics = collect_metrics()

                    alerts = alert_engine.check(metrics)

                    await storage.store(metrics)

                    # Rebuild only the inner renderables (text grid and strings)
                    gpu_text = _format_gpu_grid(metrics.get('gpus', []), fixed_width - 6)

                    sys_info = metrics.get('system', {})
                    system_content = (
                        f"[bold]CPU:[/bold] {sys_info.get('cpu_percent', 0):.1f}%\n"
                        f"[bold]RAM:[/bold] {sys_info.get('memory_used_gb', 0):.1f}/{sys_info.get('memory_total_gb', 0):.1f} GB\n"
                        f"[bold]Disk:[/bold] {sys_info.get('disk_used_gb', 0):.1f}/{sys_info.get('disk_total_gb', 0):.1f} GB"
                    )

                    # Replace header/system/footer panels with updated Text
                    node_name = metrics.get('hostname') or socket.gethostname()
                    new_header = Text.from_markup(
                        f"[bold cyan]MyGPU[/bold cyan] | Node: [green]{node_name}[/green] | "
                        f"Last Update: {datetime.now().strftime('%H:%M:%S')} | Alerts: [{'red' if alerts else 'green'}]{len(alerts)}[/]"
                    )
                    dashboard["header"].update(Panel(new_header, style="bold"))

                    new_system = Text.from_markup(system_content)
                    dashboard["right"]["system"].update(Panel(new_system, title="System"))

                    if alerts:
                        new_footer = Text.from_markup(" | ".join([f"[red]{a['message']}[/red]" for a in alerts[:3]]))
                    else:
                        new_footer = Text.from_markup("[green]All systems healthy[/green]")
                    # keep the benchmark panel static (no per-iteration rebuild)
                    dashboard["right"]["help"].update(Panel(benchmark_text, title="Benchmark"))
                    dashboard["footer"].update(Panel(new_footer, title="Status"))

                    dashboard["gpus"].update(Panel(gpu_text, title="GPU Metrics"))

                    live.update(dashboard)

                    await asyncio.sleep(config['monitoring']['interval_seconds'])

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    # Print exceptions to the fixed console in-place
                    fixed_console.print(f"[red]Error: {e}[/red]")
                    await asyncio.sleep(5)
    finally:
        # Clean exit from CLI loop (no global console mutation to restore)
        pass


def _run_app(config_path, port, nodes, once, web_mode=False, cli_mode=False):
    """Helper to run main application logic."""
    # If the user requested admin mode via --admin in argv, and the process is not elevated,
    # attempt to relaunch elevated.
    try:
        import sys
        import platform
        import os
        import subprocess

        def _is_elevated():
            if platform.system() == 'Windows':
                try:
                    import ctypes
                    return bool(ctypes.windll.shell32.IsUserAnAdmin())
                except Exception:
                    return False
            else:
                return os.getuid() == 0

        if '--admin' in (sys.argv[1:] if len(sys.argv) > 1 else []) and not _is_elevated():
            if platform.system() == 'Windows':
                # Attempt relaunch elevated on Windows
                try:
                    import ctypes
                    params = '"' + os.path.abspath(sys.argv[0]) + '"'
                    other_args = [a for a in sys.argv[1:]]
                    if other_args:
                        params += ' ' + ' '.join(str(a) for a in other_args)

                    ret = ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, params, None, 1)
                    if int(ret) > 32:
                        os._exit(0)
                except Exception:
                    # Fallback to powershell if ShellExecuteW fails
                    try:
                        def _ps_quote(s):
                            return "'" + str(s).replace("'", "''") + "'"
                        ps_args = [os.path.abspath(sys.argv[0])] + list(sys.argv[1:])
                        arglist_literal = ','.join(_ps_quote(a) for a in ps_args)
                        ps_cmd = [
                            'powershell', '-NoProfile', '-NonInteractive', '-Command',
                            f"Start-Process -FilePath '{sys.executable}' -ArgumentList {arglist_literal} -Verb RunAs"
                        ]
                        subprocess.run(ps_cmd, capture_output=True, text=True, timeout=15)
                        os._exit(0)
                    except Exception:
                        pass
            else:
                # POSIX relaunch with sudo
                try:
                    args = ['sudo', sys.executable, os.path.abspath(sys.argv[0])] + sys.argv[1:]
                    # Ensure we don't end up in an infinite loop if sudo fails or doesn't grant root
                    if 'SUDO_COMMAND' not in os.environ:
                        os.execvp('sudo', args)
                except Exception:
                    pass
    except Exception:
        pass

    cfg = load_config(config_path)
    console.print(BANNER, style="bold cyan")
    
    # CLI port overrides config only if explicitly specified
    if port is not None:
        cfg['web']['port'] = port
    
    if nodes:
        cfg['cluster']['nodes'] = [{'hostname': n.strip()} for n in nodes.split(',')]

    if once:
        metrics = collect_metrics()
        console.print_json(data=metrics)
        return

    async def main():
        if web_mode and cli_mode:
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

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")


@click.group(invoke_without_command=True)
@click.option('--config', '-c', type=click.Path(), help='Configuration file path.')
@click.option('--port', '-p', type=int, help='Web server port (default: 8090).')
@click.option('--update', is_flag=True, help='Check for and install updates.')
@click.option('--admin', is_flag=True, help='Start in administrative mode (enables privileged dashboard actions).')
@click.pass_context
def cli(ctx, config, port, update, admin):
    """MyGPU: Real-time GPU and system health monitoring."""
    # If admin requested and not already elevated, attempt to relaunch elevated
    def _is_elevated():
        import platform
        import os
        if platform.system() == 'Windows':
            try:
                import ctypes
                return bool(ctypes.windll.shell32.IsUserAnAdmin())
            except Exception:
                return False
        else:
            try:
                return os.getuid() == 0
            except Exception:
                return False

    def _relaunch_elevated():
        import sys
        import os
        import platform
        import subprocess
        script = os.path.abspath(sys.argv[0])
        args = sys.argv[1:]
        if '--admin' not in args:
            args = args + ['--admin']

        if platform.system() == 'Windows':
            try:
                import ctypes
                params = '"' + script + '"'
                if args:
                    params += ' ' + ' '.join(str(a) for a in args)
                ret = ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, params, None, 1)
                if int(ret) > 32:
                    os._exit(0)
            except Exception:
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
                    subprocess.run(ps_cmd, capture_output=True, text=True, timeout=15)
                    os._exit(0)
                except Exception:
                    pass
        else:
            # POSIX relaunch with sudo
            try:
                sudo_args = ['sudo', sys.executable, script] + args
                if 'SUDO_COMMAND' not in os.environ:
                    os.execvp('sudo', sudo_args)
            except Exception as e:
                print(f'Relaunch elevation error: {e}')

    try:
        if admin and not _is_elevated():
            _relaunch_elevated()
    except Exception:
        pass
    if update:
        from monitor.utils import check_for_updates, perform_update
        console.print("\n[cyan]Checking for updates...[/cyan]")
        
        status = check_for_updates()
        
        if status.get('error'):
            console.print(f"[red]{status['error']}[/red]")
            return
        
        if not status['available']:
            console.print(f"[green]You have the latest version ({status['current']})[/green]")
            return
        
        console.print("\n[yellow]Update available:[/yellow]")
        console.print(f"  Current: {status['current']}")
        console.print(f"  Latest: {status['latest']}")
        
        if click.confirm("\nDownload and install update?"):
            console.print("\n[cyan]Downloading update...[/cyan]")
            if perform_update():
                console.print("[green]Update complete! Restart the application.[/green]")
            else:
                console.print("[red]Update failed. Try again later.[/red]")
        return
    
    ctx.obj = {'config_path': config, 'admin': admin}
    if ctx.invoked_subcommand is None:
        # If admin flag set, append to sys.argv so server.detect features and app.state see it
        if admin and '--admin' not in sys.argv:
            sys.argv.append('--admin')
        _run_app(config, port=port, nodes=None, once=False, web_mode=True)

@cli.command()
@click.option('--port', '-p', type=int, help='Web server port (overrides config).')
@click.option('--admin', is_flag=True, help='Start web server in administrative mode (enables privileged actions).')
@click.pass_context
def web(ctx, port, admin):
    """Launch the web dashboard."""
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
    _run_app(ctx.obj['config_path'], port, nodes=None, once=False, web_mode=True)

@cli.command(name="cli")
@click.pass_context
def term(ctx):
    """Launch the interactive terminal dashboard."""
    _run_app(ctx.obj['config_path'], port=None, nodes=None, once=False, cli_mode=True)

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
    
    console.print("\n[cyan]Running diagnostics...[/cyan]")
    
    try:
        import cupy as cp
        # Try to detect CuPy CUDA runtime major version
        cuda_ok = False
        try:
            cuda_version = None
            try:
                if hasattr(cp, 'cuda') and hasattr(cp.cuda, 'runtime') and hasattr(cp.cuda.runtime, 'get_runtime_version'):
                    cuda_version = cp.cuda.runtime.get_runtime_version()
            except Exception:
                cuda_version = None
            if cuda_version is None:
                try:
                    if hasattr(cp.cuda, 'runtime') and hasattr(cp.cuda.runtime, 'runtimeGetVersion'):
                        cuda_version = cp.cuda.runtime.runtimeGetVersion()
                except Exception:
                    cuda_version = None

            if cuda_version is not None:
                s = str(cuda_version)
                if s.startswith('12') or ('.' in s and s.split('.')[0] == '12'):
                    cuda_ok = True
        except Exception:
            cuda_ok = False

        try:
            cp.cuda.Device(0).compute_capability
        except Exception:
            console.print("  CuPy: [red]Error - cannot access GPU device[/red]")
            raise

        if cuda_ok:
            console.print("  CuPy: [green]OK (CUDA 12.x)[/green]")
        else:
            console.print("  CuPy: [yellow]Installed but NOT built for CUDA 12.x[/yellow]")
            console.print("           Install a CuPy wheel built for CUDA 12.x (e.g. cupy-cuda12x)")
    except ImportError:
        console.print("  CuPy: [yellow]Not installed[/yellow]")
    except Exception as e:
        console.print(f"  CuPy: [red]Error - {str(e)}[/red]")
    
    try:
        import torch
        cuda_report = getattr(torch.version, 'cuda', None)
        if cuda_report is None:
            console.print("  PyTorch: [yellow]Installed but CUDA version not reported[/yellow]")
        else:
            major = str(cuda_report).split('.')[0]
            if major == '12' and torch.cuda.is_available():
                console.print(f"  PyTorch: [green]OK (CUDA {cuda_report})[/green]")
            else:
                console.print(f"  PyTorch: [yellow]Installed but incompatible CUDA ({cuda_report})[/yellow]")
                console.print("           Install a PyTorch wheel built for CUDA 12.x and ensure CUDA 12.x is installed")
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
