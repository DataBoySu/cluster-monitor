"""Baseline storage for benchmark results."""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class BaselineStorage:
    """Storage for benchmark baseline results in SQLite."""
    
    def __init__(self, db_path: str = './metrics.db'):
        self.db_path = Path(db_path)
        self._ensure_table()
    
    def _ensure_table(self):
        """Ensure baseline table exists with correct schema."""
        conn = sqlite3.connect(str(self.db_path))
        
        # Check if table exists and has old schema
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_baseline'"
        )
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # Check if benchmark_type column exists
            cursor = conn.execute("PRAGMA table_info(benchmark_baseline)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'benchmark_type' not in columns or 'run_mode' not in columns:
                # Migrate old table - drop and recreate
                conn.execute('DROP TABLE IF EXISTS benchmark_baseline')
        
        # Create table with new schema
        conn.execute('''
            CREATE TABLE IF NOT EXISTS benchmark_baseline (
                gpu_name TEXT NOT NULL,
                benchmark_type TEXT NOT NULL,
                run_mode TEXT NOT NULL DEFAULT 'benchmark',
                timestamp TEXT NOT NULL,
                iterations_completed INTEGER,
                avg_iteration_time_ms REAL,
                avg_utilization REAL,
                avg_temperature REAL,
                avg_power REAL,
                avg_memory_used REAL,
                results_json TEXT,
                PRIMARY KEY (gpu_name, benchmark_type, run_mode)
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_baseline(self, gpu_name: str, benchmark_type: str, results: Dict[str, Any], run_mode: str = 'benchmark'):
        """Save benchmark results as baseline for a GPU and benchmark type."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute('''
            INSERT OR REPLACE INTO benchmark_baseline 
            (gpu_name, benchmark_type, run_mode, timestamp, iterations_completed, avg_iteration_time_ms, 
             avg_utilization, avg_temperature, avg_power, avg_memory_used, results_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            gpu_name,
            benchmark_type,
            run_mode,
            results.get('timestamp', datetime.now().isoformat()),
            results.get('iterations_completed', 0),
            results.get('avg_iteration_time_ms', 0),
            results.get('utilization', {}).get('avg', 0),
            results.get('temperature_c', {}).get('avg', 0),
            results.get('power_w', {}).get('avg', 0),
            results.get('memory_used_mb', {}).get('avg', 0),
            json.dumps(results)
        ))
        conn.commit()
        conn.close()
    
    def get_baseline(self, gpu_name: str, benchmark_type: str, run_mode: str = 'benchmark') -> Optional[Dict[str, Any]]:
        """Retrieve baseline for a GPU and benchmark type."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            'SELECT * FROM benchmark_baseline WHERE gpu_name = ? AND benchmark_type = ? AND run_mode = ?', 
            (gpu_name, benchmark_type, run_mode)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'gpu_name': row['gpu_name'],
                'benchmark_type': row['benchmark_type'],
                'run_mode': row['run_mode'],
                'timestamp': row['timestamp'],
                'iterations_completed': row['iterations_completed'],
                'avg_iteration_time_ms': row['avg_iteration_time_ms'],
                'avg_utilization': row['avg_utilization'],
                'avg_temperature': row['avg_temperature'],
                'avg_power': row['avg_power'],
                'avg_memory_used': row['avg_memory_used'],
                'full_results': json.loads(row['results_json']) if row['results_json'] else None
            }
        return None
