#!/usr/bin/env python3
"""Cluster Health Monitor - Real-time GPU cluster monitoring."""

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

console = Console()

BANNER = """
╔══════════════════════════════════════════════════╗
║          CLUSTER HEALTH MONITOR v1.0.0           ║
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


@click.group(invoke_without_command=True)
@click.option('--config', '-c', type=click.Path(), help='Configuration file path.')
@click.option('--port', '-p', type=int, help='Web server port (default: 8090).')
@click.option('--update', is_flag=True, help='Check for and install updates.')
@click.pass_context
def cli(ctx, config, port, update):
    """Cluster Health Monitor: Real-time GPU and system health monitoring."""
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
        
        console.print(f"\n[yellow]Update available:[/yellow]")
        console.print(f"  Current: {status['current']}")
        console.print(f"  Latest: {status['latest']}")
        
        if click.confirm("\nDownload and install update?"):
            console.print("\n[cyan]Downloading update...[/cyan]")
            if perform_update():
                console.print("[green]Update complete! Restart the application.[/green]")
            else:
                console.print("[red]Update failed. Try again later.[/red]")
        return
    
    ctx.obj = {'config_path': config}
    if ctx.invoked_subcommand is None:
        _run_app(config, port=port, nodes=None, once=False, web_mode=True)

@cli.command()
@click.option('--port', '-p', type=int, help='Web server port (overrides config).')
@click.pass_context
def web(ctx, port):
    """Launch the web dashboard."""
    _run_app(ctx.obj['config_path'], port, nodes=None, once=False, web_mode=True)

@cli.command(name="cli")
@click.pass_context
def term(ctx):
    """Launch the interactive terminal dashboard."""
    _run_app(ctx.obj['config_path'], port=None, nodes=None, once=False, cli_mode=True)


if __name__ == '__main__':
    cli.add_command(benchmark_cli)
    cli()
