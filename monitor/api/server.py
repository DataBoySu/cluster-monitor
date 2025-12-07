"""FastAPI server for REST API and web dashboard."""

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

# Path to the templates directory, relative to this file
TEMPLATE_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

def create_app(config: Dict[str, Any]) -> FastAPI:
    
    app = FastAPI(
        title="Cluster Health Monitor",
        description="Real-time GPU cluster monitoring",
        version="1.0.0"
    )
    
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
        return FileResponse(TEMPLATE_DIR / "index.html")
    
    @app.get("/simulation", response_class=HTMLResponse)
    async def read_simulation():
        return FileResponse(TEMPLATE_DIR / "simulation.html")
    
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
        
        return {
            'status': 'healthy' if not alerts else 'warning',
            'metrics': metrics,
            'alerts': alerts,
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
    
    @app.get("/api/system")
    async def get_system():
        collector = SystemCollector()
        return {'system': collector.collect()}
    
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
