"""FastAPI server for REST API and web dashboard."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import json
import csv
import io
import asyncio
import threading

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from monitor.collectors.gpu import GPUCollector
from monitor.collectors.system import SystemCollector
from monitor.storage.sqlite import MetricsStorage
from monitor.alerting.rules import AlertEngine
from monitor import benchmark_router

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
    
    return app
