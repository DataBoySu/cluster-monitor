from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json
import csv
import io
import asyncio
import threading

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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
        title="MyGPU",
        description="MyGPU — Lightweight GPU monitoring and benchmark dashboard",
        version=_pkg_version
    )
    # Determine if the process is running with admin/elevated rights or was started with --admin
    try:
        import sys
        import platform
        import os
        is_elev = False
        if platform.system() == 'Windows':
            try:
                import ctypes
                is_elev = bool(ctypes.windll.shell32.IsUserAnAdmin())
            except Exception:
                is_elev = False
        else:
            try:
                is_elev = os.getuid() == 0
            except Exception:
                is_elev = False

        started_with_flag = '--admin' in (sys.argv[1:] if len(sys.argv) > 1 else [])
        app.state.is_admin = bool(is_elev or started_with_flag)
    except Exception:
        app.state.is_admin = False
    
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    
    storage = MetricsStorage(config['storage']['path'])
    alert_engine = AlertEngine(config.get('alerts', {}))
    
    app.include_router(benchmark_router.router)
    # VRAM cap persistence helpers (simple JSON file next to package)
    def _vram_caps_file() -> Path:
        return Path(__file__).parent.parent / "vram_caps.json"

    def _vram_watchlist_file() -> Path:
        return Path(__file__).parent.parent / "vram_watchlist.json"

    def _load_vram_watchlist() -> list:
        p = _vram_watchlist_file()
        if not p.exists():
            return []
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
            if isinstance(data, list):
                return [int(x) for x in data]
        except Exception:
            pass
        return []

    def _save_vram_watchlist(wl: list):
        try:
            p = _vram_watchlist_file()
            p.write_text(json.dumps([int(x) for x in wl], indent=2), encoding='utf-8')
        except Exception:
            pass

    def _load_vram_caps() -> Dict[int, Any]:
        p = _vram_caps_file()
        if not p.exists():
            return {}
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
            # keys are stored as strings in JSON, convert to ints
            return {int(k): v for k, v in data.items()}
        except Exception:
            return {}

    def _save_vram_caps(caps: Dict[int, Any]):
        try:
            p = _vram_caps_file()
            p.write_text(json.dumps({str(k): v for k, v in caps.items()}, indent=2), encoding='utf-8')
        except Exception:
            pass

    app.state.vram_caps = _load_vram_caps()
    app.state.vram_watchlist = _load_vram_watchlist()
    try:
        from monitor.enforcer import get_enforcer
        app.state.vram_enforcer = get_enforcer()
    except Exception:
        app.state.vram_enforcer = None

    # Helper: re-check GPUs after a delay and terminate watched PIDs if still exceeded
    async def _vram_recheck_and_terminate_task(gpus_to_check, watchlist_snapshot, caps_snapshot):
        await asyncio.sleep(5)
        try:
            collector = GPUCollector()
            gnow = collector.collect()
            try:
                procs2 = collector.collect_processes()
            except Exception:
                procs2 = []
            import psutil as _ps
            for gpu2 in gnow:
                if gpu2.get('error'):
                    continue
                gi = gpu2.get('index')
                if gi not in gpus_to_check:
                    continue
                total_mb = float(gpu2.get('memory_total', 0))
                used_mb = float(gpu2.get('memory_used', 0))
                entry2 = caps_snapshot.get(gi) if isinstance(caps_snapshot, dict) else None
                still_exceeded = False
                try:
                    if entry2:
                        if 'cap_mb' in entry2 and entry2['cap_mb'] is not None:
                            if used_mb > float(entry2['cap_mb']):
                                still_exceeded = True
                        elif 'cap_percent' in entry2 and entry2['cap_percent'] is not None and total_mb > 0:
                            used_pct = (used_mb / total_mb) * 100.0
                            if used_pct > float(entry2['cap_percent']):
                                still_exceeded = True
                except Exception:
                    still_exceeded = False

                if still_exceeded:
                    try:
                        for proc in procs2:
                            try:
                                pid = int(proc.get('pid'))
                            except Exception:
                                continue
                            if pid not in watchlist_snapshot:
                                continue
                            if proc.get('gpu_index') == gi:
                                try:
                                    p = _ps.Process(pid)
                                    try:
                                        p.terminate()
                                        try:
                                            p.wait(timeout=5)
                                        except Exception:
                                            p.kill()
                                    except Exception:
                                        try:
                                            p.kill()
                                        except Exception:
                                            pass
                                    alert_engine.active_alerts.append({
                                        'timestamp': datetime.now().isoformat(),
                                        'hostname': 'local',
                                        'name': f'pid_{pid}_terminated_after_retry',
                                        'severity': 'info',
                                        'message': f'Auto-terminated PID {pid} (retry) on GPU {gi} due to VRAM cap'
                                    })
                                except Exception:
                                    pass
                    except Exception:
                        pass
        except Exception:
            pass
    
    @app.on_event("startup")
    async def startup():
        await storage.initialize()
        async def _vram_cap_watcher():
            from monitor.alerting.toaster import send_toast
            from datetime import datetime
            while True:
                try:
                    caps = getattr(app.state, 'vram_caps', {}) or {}
                    if not caps:
                        await asyncio.sleep(config.get('monitoring', {}).get('interval_seconds', 5))
                        continue

                    try:
                        collector = GPUCollector()
                        gpus = collector.collect()
                    except Exception:
                        gpus = []

                    for gpu in gpus:
                        if gpu.get('error'):
                            continue
                        idx = gpu.get('index')
                        if idx is None:
                            continue
                        if idx not in caps:
                            continue
                        entry = caps[idx]
                        total_mb = float(gpu.get('memory_total', 0))
                        used_mb = float(gpu.get('memory_used', 0))

                        exceeded = False
                        reason = None
                        if 'cap_mb' in entry and entry['cap_mb'] is not None:
                            try:
                                cap_mb = float(entry['cap_mb'])
                                if used_mb > cap_mb:
                                    exceeded = True
                                    reason = f"used {int(used_mb)} MB > cap {int(cap_mb)} MB"
                            except Exception:
                                pass
                        elif 'cap_percent' in entry and entry['cap_percent'] is not None and total_mb > 0:
                            try:
                                cap_pct = float(entry['cap_percent'])
                                used_pct = (used_mb / total_mb) * 100.0
                                if used_pct > cap_pct:
                                    exceeded = True
                                    reason = f"used {used_pct:.0f}% > cap {cap_pct:.0f}%"
                            except Exception:
                                pass

                        if exceeded:
                            ts = datetime.now().isoformat()
                            msg = f"GPU {idx} VRAM cap exceeded: {reason}"
                            alert = {
                                'timestamp': ts,
                                'hostname': gpu.get('name', 'local'),
                                'name': f'gpu_{idx}_vram_cap_exceeded',
                                'severity': 'warning',
                                'message': msg,
                            }
                            try:
                                alert_engine.active_alerts.append(alert)
                            except Exception:
                                pass
                            # send a prominent red toast for exceeded VRAM
                            try:
                                send_toast('VRAM Exceeded', f'VRAM of GPU {idx} exceeded ({reason})', duration=8, severity='critical')
                            except Exception:
                                pass
                            # attempt auto-terminate of watched PIDs on this GPU (admin-only)
                            try:
                                if getattr(app.state, 'is_admin', False):
                                    watchlist = set(getattr(app.state, 'vram_watchlist', []) or [])
                                    if watchlist:
                                        # collect processes and terminate those on this GPU and in watchlist
                                        try:
                                            proc_list = collector.collect_processes()
                                            import psutil
                                            for proc in proc_list:
                                                try:
                                                    pid = int(proc.get('pid'))
                                                except Exception:
                                                    continue
                                                if pid not in watchlist:
                                                    continue
                                                if proc.get('gpu_index') == idx:
                                                    try:
                                                        p = psutil.Process(pid)
                                                        pname = None
                                                        try:
                                                            pname = p.name()
                                                        except Exception:
                                                            pname = None
                                                        # attempt graceful terminate then kill if needed
                                                        try:
                                                            p.terminate()
                                                            try:
                                                                p.wait(timeout=5)
                                                            except Exception:
                                                                p.kill()
                                                        except Exception:
                                                            try:
                                                                p.kill()
                                                            except Exception:
                                                                pass

                                                        # also attempt to terminate/kill any children
                                                        try:
                                                            for child in p.children(recursive=True):
                                                                try:
                                                                    child.terminate()
                                                                except Exception:
                                                                    pass
                                                        except Exception:
                                                            pass

                                                        alert_engine.active_alerts.append({
                                                            'timestamp': datetime.now().isoformat(),
                                                            'hostname': 'local',
                                                            'name': f'pid_{pid}_terminated',
                                                            'severity': 'info',
                                                            'message': f'Auto-terminated PID {pid} (name={pname}) on GPU {idx} due to VRAM cap'
                                                        })

                                                        # additionally try to find running processes with same name on this GPU and kill them (best-effort)
                                                        if pname:
                                                            for p2 in proc_list:
                                                                try:
                                                                    pid2 = int(p2.get('pid'))
                                                                except Exception:
                                                                    continue
                                                                if pid2 == pid:
                                                                    continue
                                                                if p2.get('gpu_index') != idx:
                                                                    continue
                                                                try:
                                                                    if str(p2.get('exe') or '').endswith(pname) or str(p2.get('name') or '') == pname:
                                                                        try:
                                                                            p_other = psutil.Process(pid2)
                                                                            p_other.terminate()
                                                                            try:
                                                                                p_other.wait(timeout=3)
                                                                            except Exception:
                                                                                p_other.kill()
                                                                            alert_engine.active_alerts.append({
                                                                                'timestamp': datetime.now().isoformat(),
                                                                                'hostname': 'local',
                                                                                'name': f'pid_{pid2}_terminated',
                                                                                'severity': 'info',
                                                                                'message': f'Also terminated PID {pid2} (name={pname}) on GPU {idx}'
                                                                            })
                                                                        except Exception:
                                                                            pass
                                                                except Exception:
                                                                    pass
                                                    except Exception:
                                                        alert_engine.active_alerts.append({
                                                            'timestamp': datetime.now().isoformat(),
                                                            'hostname': 'local',
                                                            'name': f'pid_{pid}_terminate_failed',
                                                            'severity': 'warning',
                                                            'message': f'Failed to terminate PID {pid} on GPU {idx}'
                                                        })
                                        except Exception:
                                            pass
                            except Exception:
                                pass
                except asyncio.CancelledError:
                    break
                except Exception:
                    # swallow per-iteration errors to keep watcher alive
                    pass
                await asyncio.sleep(config.get('monitoring', {}).get('interval_seconds', 5))

        try:
            app.state._vram_watcher_task = asyncio.create_task(_vram_cap_watcher())
        except Exception:
            app.state._vram_watcher_task = None
    
    @app.on_event("shutdown")
    async def shutdown():
        storage.close()
        try:
            t = getattr(app.state, '_vram_watcher_task', None)
            if t:
                t.cancel()
        except Exception:
            pass
    
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
        update_task = None
        
        async def send_status_updates():
            while sim_runner and sim_runner.running:
                try:
                    status = sim_runner.get_status()
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
                            await websocket.send_json({
                                'type': 'frame',
                                'fps': status.get('fps', 0),
                                'gpu': status.get('gpu_util', 0),
                                'active_particles': status.get('iterations', 0) if sim_runner.stress_worker else 0,
                                'iterations': status.get('iterations', 0),
                                'particles': particles_data
                            })
                except Exception:
                    break
                await asyncio.sleep(0.033)
        
        try:
            while True:
                data = await websocket.receive_json()
                
                if data['type'] == 'start':
                    if sim_runner and sim_runner.running:
                        continue

                    num_particles = data.get('particles', 100000)
                    backend_mult = data.get('backend', 1)
                    
                    config = benchmark_config.BenchmarkConfig(
                        benchmark_type='particle',
                        duration_seconds=3600,
                        sample_interval_ms=100,
                        num_particles=num_particles,
                        backend_multiplier=backend_mult
                    )
                    
                    sim_runner = benchmark_runner.get_benchmark_instance()
                    sim_thread = threading.Thread(
                        target=sim_runner.run,
                        args=(config, True),
                        daemon=True
                    )
                    sim_thread.start()
                    
                    if update_task:
                        update_task.cancel()
                    update_task = asyncio.create_task(send_status_updates())
                
                elif data['type'] == 'spawn' and sim_runner and sim_runner.stress_worker:
                    x = data.get('x', 500)
                    y = data.get('y', 400)
                    count = data.get('count', 1)
                    sim_runner.stress_worker.spawn_big_balls(x, y, count)
                
                elif data['type'] == 'update_params' and sim_runner and sim_runner.stress_worker:
                    sim_runner.stress_worker.update_physics_params(
                        gravity_strength=data.get('gravity'),
                        small_ball_speed=data.get('speed'),
                        initial_balls=data.get('initial_balls')
                    )
                
                elif data['type'] == 'stop':
                    if sim_runner:
                        sim_runner.running = False
                        sim_runner.stop()
                    if update_task:
                        update_task.cancel()
                    break
        
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            if sim_runner:
                sim_runner.running = False
                sim_runner.stop()
            if update_task:
                update_task.cancel()
    
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
        
        # Calculate total VRAM usage from processes and compute cap exceed status
        gpu_memory_stats = {}
        vram_cap_exceeded = {}
        caps = getattr(app.state, 'vram_caps', {}) or {}
        for gpu in gpus:
            if not gpu.get('error'):
                idx = gpu['index']
                total = gpu.get('memory_total', 0)
                used = gpu.get('memory_used', 0)
                free = gpu.get('memory_free', 0)
                gpu_memory_stats[idx] = {'total': total, 'used': used, 'free': free}
                exceeded = False
                reason = None
                if idx in caps:
                    entry = caps[idx]
                    try:
                        if 'cap_mb' in entry and entry['cap_mb'] is not None:
                            if used > float(entry['cap_mb']):
                                exceeded = True
                                reason = f"used {int(used)} MB > cap {int(entry['cap_mb'])} MB"
                        elif 'cap_percent' in entry and entry['cap_percent'] is not None and total > 0:
                            used_pct = (used / total) * 100.0
                            if used_pct > float(entry['cap_percent']):
                                exceeded = True
                                reason = f"used {used_pct:.0f}% > cap {float(entry['cap_percent']):.0f}%"
                    except Exception:
                        exceeded = False
                vram_cap_exceeded[idx] = {'exceeded': bool(exceeded), 'reason': reason}

        return {
            'processes': processes,
            'gpu_memory': gpu_memory_stats,
            'vram_caps': caps,
            'vram_cap_exceeded': vram_cap_exceeded,
        }

    @app.get('/api/vram_caps')
    async def get_vram_caps():
        """Return currently configured per-GPU VRAM caps.

        Response: { "vram_caps": { "0": {"cap_mb": 8192} } }
        """
        return {'vram_caps': getattr(app.state, 'vram_caps', {})}

    @app.get('/api/processes/watchlist')
    async def get_processes_watchlist():
        return {'watchlist': list(getattr(app.state, 'vram_watchlist', []))}

    @app.post('/api/processes/watchlist')
    async def update_processes_watchlist(payload: Dict[str, Any]):
        """Add or remove a pid from the watchlist.

        JSON: { "pid": 1234, "action": "add"|"remove" }
        """
        try:
            pid = int(payload.get('pid'))
        except Exception:
            return {'status': 'error', 'error': 'invalid_pid'}
        action = str(payload.get('action', '')).lower()
        watch = set(getattr(app.state, 'vram_watchlist', []) or [])
        if action == 'add':
            watch.add(pid)
        elif action == 'remove':
            watch.discard(pid)
        else:
            return {'status': 'error', 'error': 'invalid_action'}
        app.state.vram_watchlist = list(watch)
        try:
            _save_vram_watchlist(app.state.vram_watchlist)
        except Exception:
            pass
        return {'status': 'ok', 'watchlist': app.state.vram_watchlist}

    @app.post('/api/vram_caps')
    async def set_vram_cap(payload: Dict[str, Any]):
        """Set a cap for a GPU. Accepts JSON with either `cap_mb` or `cap_percent`.

        Example: {"gpu_index": 0, "cap_mb": 8192}
                 {"gpu_index": 1, "cap_percent": 80}
        """
        try:
            if not isinstance(payload, dict):
                raise ValueError('invalid_payload')
            gpu_index = int(payload.get('gpu_index'))
        except Exception:
            return {'status': 'error', 'error': 'invalid_gpu_index'}

        cap_entry: Dict[str, Any] = {}
        if 'cap_mb' in payload:
            try:
                cap_entry['cap_mb'] = int(payload.get('cap_mb'))
            except Exception:
                return {'status': 'error', 'error': 'invalid_cap_mb'}
        elif 'cap_percent' in payload:
            try:
                pct = float(payload.get('cap_percent'))
                if pct <= 0 or pct > 100:
                    raise ValueError()
                cap_entry['cap_percent'] = float(pct)
            except Exception:
                return {'status': 'error', 'error': 'invalid_cap_percent'}
        else:
            return {'status': 'error', 'error': 'missing_cap_value'}

        caps = getattr(app.state, 'vram_caps', {}) or {}
        caps[gpu_index] = cap_entry
        app.state.vram_caps = caps
        _save_vram_caps(caps)

        exceeded_gpus = []
        try:
            if getattr(app.state, 'is_admin', False):
                from monitor.alerting.toaster import send_toast
                gcoll = GPUCollector()
                try:
                    gpus = gcoll.collect()
                except Exception:
                    gpus = []

                watchlist = set(getattr(app.state, 'vram_watchlist', []) or [])
                if watchlist and gpus:
                    try:
                        proc_list = gcoll.collect_processes()
                    except Exception:
                        proc_list = []

                    import psutil
                    for gpu in gpus:
                        if gpu.get('error'):
                            continue
                        idx = gpu.get('index')
                        if idx is None or idx not in caps:
                            continue
                        entry = caps[idx]
                        total_mb = float(gpu.get('memory_total', 0))
                        used_mb = float(gpu.get('memory_used', 0))
                        exceeded = False
                        reason = None
                        try:
                            if entry.get('cap_mb') is not None:
                                cap_mb = float(entry['cap_mb'])
                                if used_mb > cap_mb:
                                    exceeded = True
                                    reason = f"used {int(used_mb)} MB > cap {int(cap_mb)} MB"
                            elif entry.get('cap_percent') is not None and total_mb > 0:
                                used_pct = (used_mb / total_mb) * 100.0
                                if used_pct > float(entry['cap_percent']):
                                    exceeded = True
                                    reason = f"used {used_pct:.0f}% > cap {float(entry['cap_percent']):.0f}%"
                        except Exception:
                            exceeded = False

                        if exceeded:
                            exceeded_gpus.append(idx)
                            try:
                                send_toast(f'VRAM of GPU {idx} exceeded', reason or 'VRAM cap exceeded', duration=8, severity='critical')
                            except Exception:
                                pass

                            for proc in proc_list:
                                try:
                                    pid = int(proc.get('pid'))
                                except Exception:
                                    continue
                                if pid not in watchlist:
                                    continue
                                if proc.get('gpu_index') != idx:
                                    continue
                                try:
                                    p = psutil.Process(pid)
                                    pname = None
                                    try:
                                        pname = p.name()
                                    except Exception:
                                        pname = None
                                    try:
                                        p.terminate()
                                        try:
                                            p.wait(timeout=5)
                                        except Exception:
                                            p.kill()
                                    except Exception:
                                        try:
                                            p.kill()
                                        except Exception:
                                            pass

                                    try:
                                        for child in p.children(recursive=True):
                                            try:
                                                child.terminate()
                                            except Exception:
                                                pass
                                    except Exception:
                                        pass

                                    alert_engine.active_alerts.append({
                                        'timestamp': datetime.now().isoformat(),
                                        'hostname': 'local',
                                        'name': f'pid_{pid}_terminated',
                                        'severity': 'info',
                                        'message': f'Auto-terminated PID {pid} (name={pname}) on GPU {idx} due to VRAM cap'
                                    })
                                except Exception:
                                    alert_engine.active_alerts.append({
                                        'timestamp': datetime.now().isoformat(),
                                        'hostname': 'local',
                                        'name': f'pid_{pid}_terminate_failed',
                                        'severity': 'warning',
                                        'message': f'Failed to terminate PID {pid} on GPU {idx}'
                                    })

                    # schedule retry after 5s to handle respawns
                    if exceeded_gpus:
                        snap = set(watchlist)
                        try:
                            asyncio.create_task(_vram_recheck_and_terminate_task(list(exceeded_gpus), snap, dict(caps)))
                        except Exception:
                            try:
                                loop = asyncio.get_event_loop()
                                loop.create_task(_vram_recheck_and_terminate_task(list(exceeded_gpus), snap, dict(caps)))
                            except Exception:
                                pass
        except Exception:
            pass

        # Optional enforcement: if payload includes enforce=true and server has admin
        if payload.get('enforce') and getattr(app.state, 'is_admin', False):
            enforcer = getattr(app.state, 'vram_enforcer', None)
            if enforcer is None:
                return {'status': 'error', 'error': 'no_enforcer_available', 'vram_caps': caps}
            if 'cap_mb' in cap_entry:
                mb_to_reserve = int(cap_entry['cap_mb'])
            elif 'cap_percent' in cap_entry and gpu_index in caps:
                # need GPU total to convert percent->MB; attempt to collect
                try:
                    g = GPUCollector()
                    gpustats = {gg['index']: gg for gg in g.collect() if not gg.get('error')}
                    total_mb = int(gpustats[gpu_index]['memory_total']) if gpu_index in gpustats else None
                    if total_mb is None:
                        return {'status': 'error', 'error': 'could_not_determine_total_mb'}
                    mb_to_reserve = int((float(cap_entry['cap_percent']) / 100.0) * total_mb)
                except Exception:
                    return {'status': 'error', 'error': 'could_not_determine_total_mb'}
            else:
                return {'status': 'error', 'error': 'missing_cap_for_enforce'}

            # Ask enforcer to allocate reserve to achieve cap: we allocate that amount (best-effort)
            try:
                res = enforcer.allocate_reserve(gpu_index, mb_to_reserve)
                return {'status': 'ok', 'vram_caps': caps, 'enforce_result': res}
            except Exception as e:
                return {'status': 'error', 'error': str(e), 'vram_caps': caps}

        # Also return immediate vram exceed status so clients can update UI without waiting
        vram_cap_exceeded_now = {}
        try:
            collector = GPUCollector()
            gpus_now = collector.collect()
            for gpu in gpus_now:
                if gpu.get('error'):
                    continue
                gi = gpu.get('index')
                if gi is None:
                    continue
                total = gpu.get('memory_total', 0)
                used = gpu.get('memory_used', 0)
                exceeded = False
                reason = None
                if gi in caps:
                    entry = caps[gi]
                    try:
                        if entry.get('cap_mb') is not None:
                            if used > float(entry['cap_mb']):
                                exceeded = True
                                reason = f"used {int(used)} MB > cap {int(entry['cap_mb'])} MB"
                        elif entry.get('cap_percent') is not None and total > 0:
                            used_pct = (used / total) * 100.0
                            if used_pct > float(entry['cap_percent']):
                                exceeded = True
                                reason = f"used {used_pct:.0f}% > cap {float(entry['cap_percent']):.0f}%"
                    except Exception:
                        exceeded = False
                vram_cap_exceeded_now[gi] = {'exceeded': bool(exceeded), 'reason': reason}
        except Exception:
            vram_cap_exceeded_now = {}

        return {'status': 'ok', 'vram_caps': caps, 'vram_cap_exceeded': vram_cap_exceeded_now}

    @app.delete('/api/vram_caps')
    async def clear_vram_caps(gpu_index: Optional[int] = None):
        """Clear configured VRAM caps. If `gpu_index` query param is provided, clears that GPU only."""
        caps = getattr(app.state, 'vram_caps', {}) or {}
        if gpu_index is None:
            enforcer = getattr(app.state, 'vram_enforcer', None)
            if enforcer is not None:
                for gi in list(caps.keys()):
                    try:
                        enforcer.release_reserve(int(gi))
                    except Exception:
                        pass
            app.state.vram_caps = {}
            _save_vram_caps({})
            return {'status': 'ok', 'vram_caps': {}}

        try:
            gi = int(gpu_index)
        except Exception:
            return {'status': 'error', 'error': 'invalid_gpu_index'}

        if gi in caps:
            caps.pop(gi, None)
            app.state.vram_caps = caps
            _save_vram_caps(caps)
        # release reserve for this gpu if present
        enforcer = getattr(app.state, 'vram_enforcer', None)
        if enforcer is not None:
            try:
                enforcer.release_reserve(gi)
            except Exception:
                pass

        return {'status': 'ok', 'vram_caps': caps}

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
            import platform
            import sys
            import os
            import subprocess
                # shlex not needed here; kept parameters safely quoted manually
            import threading
            import time

            def _log(msg):
                try:
                    ts = datetime.now().isoformat()
                    ln = f"[{ts}] {msg}\n"
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
                        try:
                            os._exit(0)
                        except Exception:
                            pass
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
                        try:
                            os._exit(0)
                        except Exception:
                            pass
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
        
        benchmark_instance = benchmark_runner.get_benchmark_instance()
        if benchmark_instance.running:
            benchmark_instance.stop()
            # Wait a bit for benchmark to stop
            await asyncio.sleep(1)
        
        storage.close()
        
        os.kill(os.getpid(), signal.SIGTERM)
        
        return {"status": "shutting_down", "message": "Server is shutting down gracefully"}
    
    return app
