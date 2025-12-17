"""FastAPI server for REST API and web dashboard.

Maintenance:
- Purpose: defines the web endpoints and WebSocket handlers used by the
    dashboard UI and simulation features.
- Debug: enable request logging and inspect `/api/*` endpoints; WebSocket
    simulation frames are sent from the benchmark runner. If server fails to
    start, check dependency imports (FastAPI, uvicorn) and configuration paths.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import json
import csv
import io
import asyncio
import threading

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from monitor.collectors.gpu import GPUCollector
from monitor.collectors.system import SystemCollector
from monitor.storage.sqlite import MetricsStorage
from monitor.alerting.rules import AlertEngine
from monitor import benchmark_router
from monitor.benchmark import runner as benchmark_runner, config as benchmark_config
from monitor.__version__ import __version__ as _pkg_version

# Path to the templates directory, relative to this file
TEMPLATE_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

def create_app(config: Dict[str, Any]) -> FastAPI:
    
    app = FastAPI(
        title="Local GPU Monitor",
        description="Local GPU monitoring and benchmark dashboard",
        version=_pkg_version
    )
    # Determine if the process is running with admin/elevated rights or was started with --admin
    try:
        import sys
        # Only Windows elevation is supported; POSIX fallbacks removed.
        try:
            import ctypes
            is_elev = bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            is_elev = False

        started_with_flag = '--admin' in (sys.argv[1:] if len(sys.argv) > 1 else [])
        app.state.is_admin = bool(is_elev or started_with_flag)
    except Exception:
        app.state.is_admin = False
    
    # Mount static files
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    
    storage = MetricsStorage(config['storage']['path'])
    alert_engine = AlertEngine(config.get('alerts', {}))
    
    # Include routers
    app.include_router(benchmark_router.router)
    
    @app.on_event("startup")
    async def startup():
        await storage.initialize()
    
    @app.on_event("shutdown")
    async def shutdown():
        storage.close()
    
    @app.get("/", response_class=HTMLResponse)
    async def read_dashboard():
        # Inject current package version into the static template placeholder
        tpl_path = TEMPLATE_DIR / "index.html"
        try:
            import re
            content = tpl_path.read_text(encoding='utf-8')
            # Replace {{VERSION}} or {{ VERSION }} (allow whitespace) with vX.Y.Z
            content = re.sub(r"\{\{\s*VERSION\s*\}\}", f"v{_pkg_version}", content)
            return HTMLResponse(content=content)
        except Exception:
            return FileResponse(tpl_path)
    
    @app.get("/simulation", response_class=HTMLResponse)
    async def read_simulation():
        # Simulation page doesn't display version currently, but keep parity
        tpl_path = TEMPLATE_DIR / "simulation.html"
        try:
            import re
            content = tpl_path.read_text(encoding='utf-8')
            content = re.sub(r"\{\{\s*VERSION\s*\}\}", f"v{_pkg_version}", content)
            return HTMLResponse(content=content)
        except Exception:
            return FileResponse(tpl_path)
    
    @app.websocket("/ws/simulation")
    async def websocket_simulation(websocket: WebSocket):
        await websocket.accept()
        sim_runner = None
        sim_thread = None
        
        try:
            while True:
                data = await websocket.receive_json()
                
                if data['type'] == 'start':
                    # Create benchmark configuration
                    particle_count = data.get('particles', 100000)
                    backend_mult = data.get('backend', 1)
                    
                    config = benchmark_config.BenchmarkConfig(
                        benchmark_type='particle',
                        duration_seconds=3600,  # Long duration, will be stopped manually
                        sample_interval_ms=100,
                        particle_count=particle_count,
                        backend_multiplier=backend_mult
                    )
                    
                    # Create benchmark runner
                    sim_runner = benchmark_runner.get_benchmark_instance()
                    
                    # Start in background thread
                    sim_thread = threading.Thread(
                        target=sim_runner.run,
                        args=(config, True),
                        daemon=True
                    )
                    sim_thread.start()
                    
                    # Send frames in a loop
                    while sim_runner.running:
                        status = sim_runner.get_status()
                        
                        # Get particle data
                        if sim_runner.stress_worker:
                            positions, masses, colors, glows = sim_runner.stress_worker.get_particle_sample(max_samples=500)
                            
                            if positions is not None:
                                particles_data = []
                                for i in range(len(positions)):
                                    particles_data.append({
                                        'x': float(positions[i][0]),
                                        'y': float(positions[i][1]),
                                        'mass': float(masses[i]),
                                        'color': [float(colors[i][0]), float(colors[i][1]), float(colors[i][2])],
                                        'glow': float(glows[i]),
                                        'radius': 36.0 if masses[i] > 100 else 8.0
                                    })
                                
                                # Send frame
                                await websocket.send_json({
                                    'type': 'frame',
                                    'fps': status.get('fps', 0),
                                    'gpu': status.get('gpu_util', 0),
                                    'active_particles': status.get('iterations', 0) if sim_runner.stress_worker else 0,
                                    'iterations': status.get('iterations', 0),
                                    'particles': particles_data
                                })
                        
                        await asyncio.sleep(0.033)  # ~30 FPS update rate
                
                elif data['type'] == 'spawn' and sim_runner and sim_runner.stress_worker:
                    # Spawn balls
                    x = data.get('x', 500)
                    y = data.get('y', 400)
                    count = data.get('count', 1)
                    sim_runner.stress_worker.spawn_big_balls(x, y, count)
                
                elif data['type'] == 'update_params' and sim_runner and sim_runner.stress_worker:
                    # Update physics parameters
                    sim_runner.stress_worker.update_physics_params(
                        gravity_strength=data.get('gravity'),
                        small_ball_speed=data.get('speed'),
                        initial_balls=data.get('initial_balls')
                    )
                
                elif data['type'] == 'stop':
                    if sim_runner:
                        sim_runner.running = False
                    break
        
        except WebSocketDisconnect:
            if sim_runner:
                sim_runner.running = False
        except Exception as e:
            print(f"WebSocket error: {e}")
            if sim_runner:
                sim_runner.running = False
        finally:
            if sim_runner:
                sim_runner.running = False
    
    @app.get("/api/status")
    async def get_status():
        gpu_collector = GPUCollector()
        sys_collector = SystemCollector()
        
        gpus = gpu_collector.collect()
        system = sys_collector.collect()
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'hostname': system.get('hostname', 'unknown'),
            'gpus': gpus,
            'system': system,
        }
        
        # Store metrics for history
        await storage.store(metrics)
        
        alerts = alert_engine.check(metrics)
        # Also surface recent benchmark state/errors to the UI so clients can display notifications
        try:
            benchmark_instance = benchmark_runner.get_benchmark_instance()
            bench_status = benchmark_instance.get_status()
            benchmark_error = None
            # If benchmark finished with a stop reason containing 'Error' or results contain error, surface it
            if bench_status and bench_status.get('stop_reason'):
                benchmark_error = bench_status.get('stop_reason')
            elif getattr(benchmark_instance, 'results', None) and isinstance(benchmark_instance.results, dict) and benchmark_instance.results.get('error'):
                benchmark_error = benchmark_instance.results.get('error')
        except Exception:
            benchmark_error = None

        return {
            'status': 'healthy' if not alerts else 'warning',
            'metrics': metrics,
            'alerts': alerts,
            'benchmark_status': bench_status if 'bench_status' in locals() else None,
            'benchmark_error': benchmark_error,
        }
    
    @app.get("/api/gpus")
    async def get_gpus():
        collector = GPUCollector()
        return {'gpus': collector.collect()}
    
    @app.get("/api/processes")
    async def get_processes():
        collector = GPUCollector()
        gpus = collector.collect()
        processes = collector.collect_processes()
        
        # Calculate total VRAM usage from processes
        gpu_memory_stats = {}
        for gpu in gpus:
            if not gpu.get('error'):
                gpu_memory_stats[gpu['index']] = {
                    'total': gpu.get('memory_total', 0),
                    'used': gpu.get('memory_used', 0),
                    'free': gpu.get('memory_free', 0)
                }
        
        return {
            'processes': processes,
            'gpu_memory': gpu_memory_stats
        }

    @app.post("/api/processes/terminate")
    async def terminate_process(payload: Dict[str, int]):
        """Terminate a process by PID. Expects JSON: {"pid": 1234}. Returns status."""
        # Require admin privileges to terminate arbitrary processes
        if not getattr(app.state, 'is_admin', False):
            return {'status': 'error', 'error': 'permission_denied', 'message': 'Server not running with administrative privileges'}

        pid = payload.get('pid') if isinstance(payload, dict) else None
        try:
            pid = int(pid)
        except Exception:
            return {'status': 'error', 'error': 'invalid_pid'}

        try:
            import psutil
            p = psutil.Process(pid)
            p.terminate()
            try:
                p.wait(timeout=3)
                return {'status': 'terminated'}
            except psutil.TimeoutExpired:
                p.kill()
                return {'status': 'killed'}
        except Exception as e:
            # psutil.NoSuchProcess and other errors
            errname = getattr(e, '__class__', type(e)).__name__
            if 'NoSuchProcess' in errname:
                return {'status': 'not_found'}
            return {'status': 'error', 'error': str(e)}

    @app.post("/api/restart_elevated")
    async def restart_elevated(payload: Dict = None):
        """Attempt to restart the application with elevated privileges on Windows.

        Expects optional JSON: { "args": ["web","--port","8890"] }
        Returns: {status: 'started'|'error', ...}
        """
        try:
            import platform, sys, os, subprocess, shlex, threading, time

            def _log(msg):
                try:
                    ts = datetime.now().isoformat()
                    ln = f"[{ts}] {msg}\n"
                    # write to console
                    print(ln, end='')
                    # append to a log file for easier debugging
                    try:
                        p = Path(__file__).parent / 'restart_elevated.log'
                        with open(p, 'a', encoding='utf-8') as fh:
                            fh.write(ln)
                    except Exception:
                        pass
                except Exception:
                    pass

            _log(f'restart_elevated called with payload: {payload!r}')

            if platform.system() != 'Windows':
                _log('restart_elevated: not running on Windows')
                return {'status': 'error', 'error': 'not_supported'}

            # locate health_monitor.py in repository root as best-effort
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            candidate = os.path.join(repo_root, 'health_monitor.py')
            if not os.path.exists(candidate):
                # fallback to the current argv[0]
                candidate = os.path.abspath(sys.argv[0])

            args_list = []
            if isinstance(payload, dict) and payload.get('args') and isinstance(payload.get('args'), list):
                args_list = payload.get('args')

            # Build params string to pass to python: "script" arg1 arg2 ...
            params = '"' + candidate + '"'
            if args_list:
                params += ' ' + ' '.join(str(a) for a in args_list)

            # If requested, perform an in-place restart using execv (restarts in the same terminal).
            if isinstance(payload, dict) and payload.get('inplace'):
                _log('Performing in-place execv restart (same terminal)')
                try:
                    # spawn a background thread to allow a HTTP response to be sent
                    def _do_exec():
                        try:
                            time.sleep(0.6)
                            os.execv(sys.executable, [sys.executable, candidate] + list(args_list))
                        except Exception as e:
                            _log('inplace execv failed: ' + str(e))

                    threading.Thread(target=_do_exec, daemon=True).start()
                    return {'status': 'started', 'method': 'inplace'}
                except Exception as e:
                    _log('inplace restart exception: ' + str(e))
                    return {'status': 'error', 'error': str(e)}

            # Try ShellExecuteW first
            try:
                import ctypes
                _log(f'Attempting ShellExecuteW runas: {sys.executable} {params}')
                h = ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, params, None, 1)
                try:
                    ok = int(h) > 32
                except Exception:
                    ok = False
                _log(f'ShellExecuteW returned: {h!r}, ok={ok}')
                if ok:
                    # schedule exit, but give small grace period
                    try:
                        threading.Timer(0.8, lambda: os._exit(0)).start()
                    except Exception:
                        try: os._exit(0)
                        except Exception: pass
                    return {'status': 'started', 'method': 'shellexecute', 'code': int(h) if isinstance(h, int) else str(h)}
                else:
                    _log('ShellExecuteW indicated failure; falling back to PowerShell Start-Process')
            except Exception as e:
                _log('ShellExecuteW exception: ' + str(e))

            # PowerShell fallback: use Start-Process -Verb RunAs
            try:
                # Build an argument list literal for PowerShell: '"script"','arg1','arg2'
                ps_args = [candidate] + list(args_list)
                def _ps_quote(s):
                    return "'" + str(s).replace("'", "''") + "'"
                arglist_literal = ','.join(_ps_quote(a) for a in ps_args)
                ps_cmd = [
                    'powershell', '-NoProfile', '-NonInteractive', '-Command',
                    f"Start-Process -FilePath '{sys.executable}' -ArgumentList {arglist_literal} -Verb RunAs"
                ]
                _log('PowerShell fallback command: ' + ' '.join(ps_cmd))
                proc = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=15)
                _log(f'PowerShell returncode={proc.returncode}; stdout={proc.stdout!r}; stderr={proc.stderr!r}')
                if proc.returncode == 0:
                    try:
                        threading.Timer(0.8, lambda: os._exit(0)).start()
                    except Exception:
                        try: os._exit(0)
                        except Exception: pass
                    return {'status': 'started', 'method': 'powershell', 'stdout': proc.stdout, 'stderr': proc.stderr}
                else:
                    return {'status': 'error', 'error': 'powershell_failed', 'code': proc.returncode, 'stderr': proc.stderr}
            except Exception as e:
                _log('PowerShell fallback exception: ' + str(e))
                return {'status': 'error', 'error': str(e)}
        except Exception as e:
            try:
                print('restart_elevated fatal error:', e)
            except Exception:
                pass
            return {'status': 'error', 'error': str(e)}
    
    @app.get("/api/system")
    async def get_system():
        collector = SystemCollector()
        return {'system': collector.collect()}

    @app.get("/api/launch_args")
    async def get_launch_args():
        """Return the command-line arguments used to launch this process (argv[1:])."""
        import sys
        try:
            return {'args': sys.argv[1:]}
        except Exception:
            return {'args': []}

    @app.get('/api/is_elevated')
    async def is_elevated():
        """Return whether the current process has elevated/admin privileges (Windows only)."""
        try:
            import sys
            elevated = False
            method = 'windows.IsUserAnAdmin'
            note = None
            try:
                import ctypes
                elevated = bool(ctypes.windll.shell32.IsUserAnAdmin())
            except Exception as e:
                note = str(e)

            # Also surface if server was started with explicit --admin flag
            try:
                started_with_flag = '--admin' in sys.argv[1:]
            except Exception:
                started_with_flag = False

            return {
                'elevated': bool(elevated),
                'method': method,
                'started_with_flag': bool(started_with_flag),
                'args': sys.argv[1:],
                'note': note
            }
        except Exception as e:
            return {'elevated': False, 'error': str(e)}
    
    @app.get("/api/alerts")
    async def get_alerts():
        return {'alerts': alert_engine.get_active_alerts()}
    
    @app.get("/api/history")
    async def get_history(hours: int = 1, metric: str = "gpu_0_utilization"):
        metrics = await storage.query(metric_name=metric, hours=hours)
        return {
            'metric': metric,
            'hours': hours,
            'data': [{'timestamp': m['timestamp'], 'value': m['metric_value']} for m in metrics]
        }
    
    @app.get("/api/history/available")
    async def get_available_metrics():
        return {
            'metrics': [
                'gpu_0_utilization', 'gpu_0_memory_used', 'gpu_0_temperature', 'gpu_0_power',
                'cpu_percent', 'memory_percent', 'disk_percent'
            ]
        }
    
    @app.get("/api/features")
    async def get_features_endpoint():
        """Get available features (always fresh to detect newly installed packages)."""
        from monitor.utils.features import detect_features
        return detect_features(force=True)
    
    @app.post("/api/update/check")
    async def check_update():
        """Check for available updates."""
        from monitor.utils import check_for_updates
        return check_for_updates()
    
    @app.post("/api/update/install")
    async def install_update():
        """Install available update."""
        from monitor.utils import perform_update
        success = perform_update()
        if success:
            return {'status': 'success', 'message': 'Update installed. Restart application.'}
        else:
            return {'status': 'error', 'message': 'Update failed'}
    
    @app.get("/api/export/json")
    async def export_json(hours: int = 24):
        metrics = await storage.query(hours=hours)
        return StreamingResponse(
            io.BytesIO(json.dumps(metrics, indent=2).encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
        )
    
    @app.get("/api/export/csv")
    async def export_csv(hours: int = 24):
        metrics = await storage.query(hours=hours)
        
        output = io.StringIO()
        if metrics:
            writer = csv.DictWriter(output, fieldnames=metrics[0].keys())
            writer.writeheader()
            writer.writerows(metrics)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
    
    @app.post("/api/shutdown")
    async def shutdown_server():
        """Gracefully shutdown the server."""
        import os
        import signal
        
        # Stop any running benchmark
        benchmark_instance = benchmark_runner.get_benchmark_instance()
        if benchmark_instance.running:
            benchmark_instance.stop()
            # Wait a bit for benchmark to stop
            await asyncio.sleep(1)
        
        # Close storage
        storage.close()
        
        # Send shutdown signal
        os.kill(os.getpid(), signal.SIGTERM)
        
        return {"status": "shutting_down", "message": "Server is shutting down gracefully"}
    
    return app
