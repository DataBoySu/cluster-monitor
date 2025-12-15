"""SQLite storage for metrics history."""
"""SQLite storage backend for metrics.

Maintenance:
- Purpose: persistent storage of collected metrics. Schema is created lazily.
- Debug: check `metrics.db` (path from config) and inspect `metrics` table.
"""

import json
import sqlite3
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional


class MetricsStorage:
    """SQLite-based metrics storage."""
    
    def __init__(self, db_path: str = './metrics.db'):
        self.db_path = Path(db_path)
        self.conn = None
    
    async def initialize(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                hostname TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                metric_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
            CREATE INDEX IF NOT EXISTS idx_metrics_hostname ON metrics(hostname);
            CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type);
            
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                hostname TEXT NOT NULL,
                alert_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                resolved_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
        ''')
        self.conn.commit()
    
    async def store(self, metrics: Dict[str, Any]):
        if not self.conn:
            await self.initialize()
        
        timestamp = metrics.get('timestamp', datetime.now().isoformat())
        hostname = metrics.get('hostname', 'unknown')
        
        # Store GPU metrics
        for gpu in metrics.get('gpus', []):
            if 'error' in gpu:
                continue
                
            self._insert_metric(timestamp, hostname, 'gpu', f"gpu_{gpu['index']}_utilization", gpu.get('utilization', 0))
            self._insert_metric(timestamp, hostname, 'gpu', f"gpu_{gpu['index']}_memory_used", gpu.get('memory_used', 0))
            self._insert_metric(timestamp, hostname, 'gpu', f"gpu_{gpu['index']}_temperature", gpu.get('temperature', 0))
            self._insert_metric(timestamp, hostname, 'gpu', f"gpu_{gpu['index']}_power", gpu.get('power', 0))
        
        # Store system metrics
        sys_metrics = metrics.get('system', {})
        self._insert_metric(timestamp, hostname, 'system', 'cpu_percent', sys_metrics.get('cpu_percent', 0))
        self._insert_metric(timestamp, hostname, 'system', 'memory_percent', sys_metrics.get('memory_percent', 0))
        self._insert_metric(timestamp, hostname, 'system', 'disk_percent', sys_metrics.get('disk_percent', 0))
        
        self.conn.commit()
    
    def _insert_metric(self, timestamp: str, hostname: str, metric_type: str, 
                       metric_name: str, metric_value: float):
        self.conn.execute('''
            INSERT INTO metrics (timestamp, hostname, metric_type, metric_name, metric_value)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, hostname, metric_type, metric_name, metric_value))
    
    async def query(self, hostname: Optional[str] = None, metric_type: Optional[str] = None,
                    metric_name: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        if not self.conn:
            await self.initialize()
        
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        query = 'SELECT * FROM metrics WHERE timestamp > ?'
        params = [since]
        
        if hostname:
            query += ' AND hostname = ?'
            params.append(hostname)
        
        if metric_type:
            query += ' AND metric_type = ?'
            params.append(metric_type)
        
        if metric_name:
            query += ' AND metric_name = ?'
            params.append(metric_name)
        
        query += ' ORDER BY timestamp DESC LIMIT 1000'
        
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    async def store_alert(self, alert: Dict[str, Any]):
        if not self.conn:
            await self.initialize()
        
        self.conn.execute('''
            INSERT INTO alerts (timestamp, hostname, alert_name, severity, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            alert.get('timestamp', datetime.now().isoformat()),
            alert.get('hostname', 'unknown'),
            alert.get('name', 'unknown'),
            alert.get('severity', 'warning'),
            alert.get('message', '')
        ))
        self.conn.commit()
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        if not self.conn:
            await self.initialize()
        
        cursor = self.conn.execute('''
            SELECT * FROM alerts WHERE resolved_at IS NULL ORDER BY timestamp DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    async def cleanup_old_data(self, retention_hours: int = 168):
        if not self.conn:
            return
        
        cutoff = (datetime.now() - timedelta(hours=retention_hours)).isoformat()
        
        self.conn.execute('DELETE FROM metrics WHERE timestamp < ?', (cutoff,))
        self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
