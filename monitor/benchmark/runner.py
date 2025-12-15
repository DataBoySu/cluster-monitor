"""GPU benchmark orchestration and metrics collection.

Maintenance:
- Purpose: coordinate benchmark execution, collect samples and expose runtime
    status to the API/UI. This is the central orchestration class for stress
    tests and particle simulations.
- Debug: use `get_status()`, `get_samples()` and `get_results()` to inspect
    runtime state; long-running threads indicate worker shutdown or join issues.
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from .config import BenchmarkConfig
from .storage import BaselineStorage
from .workloads import GPUStressWorker
from .metrics_sampler import GPUMetricsSampler


class GPUBenchmark:
    """GPU Benchmark with real-time monitoring and stress workload."""
    
    def __init__(self, db_path: str = './metrics.db'):
        self.running = False
        self.should_stop = False
        self.config: Optional[BenchmarkConfig] = None
        self.samples: List[Dict[str, Any]] = []
        self.stop_reason: Optional[str] = None
        self.start_time: Optional[float] = None
        self.progress = 0
        self.current_phase = ""
        self.results: Dict[str, Any] = {}
        self.baseline_storage = BaselineStorage(db_path)
        self.stress_worker: Optional[GPUStressWorker] = None
        self.iteration_times: List[float] = []
        self.completed_full = False
        self.db_path = db_path
        
        # Initialize metrics sampler
        self.metrics_sampler = GPUMetricsSampler()
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information."""
        return self.metrics_sampler.get_gpu_info()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current benchmark status."""
        render_fps = getattr(self, 'render_fps', 0.0)
        gpu_util = self.metrics_sampler.get_current_util() if hasattr(self, 'metrics_sampler') and self.metrics_sampler else 0
        
        # Get latest sample with current metrics
        latest_sample = None
        if self.samples:
            latest_sample = self.samples[-1].copy()
            # Update with real-time GPU util if available
            latest_sample['utilization'] = gpu_util
        
        current_iteration = self.stress_worker.iterations if self.stress_worker else 0
        is_running = getattr(self, 'running', False)
        
        # Determine backend in use: prefer explicit worker method, else configured preference
        backend_in_use = None
        try:
            backend_in_use = self.stress_worker._method if self.stress_worker and hasattr(self.stress_worker, '_method') else None
        except Exception:
            backend_in_use = None

        return {
            'status': 'running' if is_running else 'idle',  # Add status field for web UI
            'running': is_running,
            'progress': getattr(self, 'progress', 0),
            'phase': getattr(self, 'current_phase', 'Running'),
            'samples_count': len(getattr(self, 'samples', [])),
            'iterations': current_iteration,
            'current_iteration': current_iteration,  # Add explicit field for web UI
            'workload_type': self.stress_worker.workload_type if self.stress_worker else 'N/A',
            'latest_sample': latest_sample,
            'latest_metrics': latest_sample,  # Alias for compatibility
            'fps': render_fps,
            'gpu_util': gpu_util,
            'results': self.results if not is_running else None,  # Include results when idle
            'stop_reason': self.stop_reason if not is_running else None,
            'backend': backend_in_use or (getattr(self, 'config', None).preferred_backend if getattr(self, 'config', None) else 'auto')
        }
    
    def get_samples(self) -> list:
        """Get all collected samples for real-time graphing."""
        return getattr(self, 'samples', []).copy()
    
    def get_baseline(self, benchmark_type: str, run_mode: str = 'benchmark') -> Optional[Dict[str, Any]]:
        """Get baseline for a benchmark type."""
        try:
            gpu_info = self.get_gpu_info()
            if gpu_info and 'name' in gpu_info:
                return self.baseline_storage.get_baseline(gpu_info['name'], benchmark_type, run_mode)
        except Exception:
            pass
        return None
    
    def get_results(self) -> Dict[str, Any]:
        """Get benchmark results."""
        return self.results
    
    def stop(self):
        """Request benchmark to stop."""
        self.should_stop = True
        
    def run_stress_benchmark(self, visualize: bool = False):
        """Run the stress benchmark loop with optional visualization."""
        from .visualizer import create_visualizer
        
        self.running = True
        self.start_time = time.time()
        
        # Create visualizer if requested
        visualizer = create_visualizer(
            enabled=visualize,
            window_size=(1200, 800),
            max_render_particles=2000
        ) if visualize else None
        
        if visualize and not visualizer:
            print("[WARNING] Visualization requested but not available")
        
        # Check if stress worker is properly initialized for visualization
        if visualize and visualizer and not self.stress_worker._initialized:
            print("[ERROR] Cannot visualize - GPU workload not initialized (cupy/torch not available)")
            if visualizer:
                visualizer.close()
            self.stop_reason = "Visualization failed - GPU libraries not available"
            return self._calculate_results()
        
        if visualize and visualizer and self.config.benchmark_type != "particle":
            print("[ERROR] Cannot visualize - visualization only available for particle benchmark")
            if visualizer:
                visualizer.close()
            self.stop_reason = "Visualization failed - not a particle benchmark"
            return self._calculate_results()
        
        # Start background GPU metrics collection
        self.metrics_sampler.start()
        
        sample_interval = self.config.sample_interval_ms / 1000.0
        last_sample_time = 0
        
        # FPS tracking independent of rendering
        frame_times = []
        max_frame_history = 10
        last_frame_time = time.time()
        
        # Auto-scaling for stress-test mode
        last_scale_check = 0
        scale_interval = 5.0  # Scale every 5 seconds
        current_backend_total = 200000  # Start with 200k total backend particles
        max_backend_total = 500000  # Max 500k total backend particles
        backend_increment = 50000  # Increase by 50k every 5 seconds
        auto_scale_timeout = 60.0 if visualize else float('inf')  # 60s timeout for visualization mode
        target_reached = False
        target_reached_time = None
        
        try:
            while True:
                elapsed = time.time() - self.start_time
                
                # Check duration
                if elapsed >= self.config.duration_seconds:
                    self.stop_reason = "Duration completed"
                    self.completed_full = True
                    break
                
                # Check auto-scale timeout for visualization mode
                if visualize and self.config.auto_scale and elapsed >= auto_scale_timeout and not target_reached:
                    self.stop_reason = "Auto-scale timeout - target GPU utilization not reached in 60s"
                    break
                
                # Run one iteration of stress work
                iter_time = self.stress_worker.run_iteration()
                self.iteration_times.append(iter_time)
                
                # Sample GPU metrics for storage (at configured interval)
                if elapsed - last_sample_time >= sample_interval:
                    sample = self.metrics_sampler.sample_metrics()
                    sample['elapsed_sec'] = round(elapsed, 2)
                    sample['iterations'] = self.stress_worker.iterations
                    sample['last_iter_ms'] = round(iter_time, 2)
                    self.samples.append(sample)
                    last_sample_time = elapsed
                
                # Render visualization frame (every frame, no throttling)
                if visualizer:
                    # Process pygame events separately
                    from . import event_handler
                    try:
                        events = visualizer.pygame.event.get() if visualizer.pygame else []
                        if not event_handler.handle_events(visualizer, events):
                            visualizer.running = False
                            self.stop_reason = "User closed visualization window"
                            break
                    except Exception as e:
                        print(f"[WARNING] Event handling error: {e}")
                    
                    # Only render if window is still open
                    if visualizer.running:
                        # Calculate stable FPS from recent frame times
                        now = time.time()
                        frame_time = now - last_frame_time
                        last_frame_time = now
                        
                        frame_times.append(frame_time)
                        if len(frame_times) > max_frame_history:
                            frame_times.pop(0)
                        
                        avg_frame_time = sum(frame_times) / len(frame_times)
                        render_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
                        self.render_fps = render_fps
                        
                        # Update physics parameters from UI
                        slider_values = visualizer.get_slider_values()
                        self.stress_worker.update_physics_params(
                            gravity_strength=slider_values['gravity'],
                            small_ball_speed=slider_values['small_ball_speed'],
                            initial_balls=int(slider_values['initial_balls']),
                            max_balls_cap=int(slider_values['max_balls_cap']),
                            big_ball_count=int(slider_values.get('big_ball_count', 5)),
                            backend_multiplier=int(slider_values.get('backend_multiplier', 1))
                        )
                        
                        self.stress_worker.update_split_enabled(visualizer.get_split_enabled())
                        
                        # Process spawn requests
                        spawn_requests = visualizer.get_spawn_requests()
                        for sim_x, sim_y, count in spawn_requests:
                            self.stress_worker.spawn_big_balls(sim_x, sim_y, count)
                        
                        # Get particle sample for rendering
                        positions, masses, colors, glows = self.stress_worker.get_particle_sample(max_samples=2000)
                        
                        # Always render to keep window responsive, even if no particle data
                        if positions is not None and len(positions) > 0:
                            # Update workload display with actual visible particle count
                            visible_count = len(positions)
                            self.stress_worker.update_workload_display(visible_count)
                            
                            influence_boundaries = self.stress_worker.get_influence_boundaries(
                                gravity_strength=slider_values['gravity']
                            )
                            active_particles = int(self.stress_worker._active_count)
                            
                            # Get real-time GPU utilization from background thread
                            gpu_util = self.metrics_sampler.get_current_util()
                            
                            visualizer.render_frame(
                                positions=positions,
                                masses=masses,
                                colors=colors,
                                glows=glows,
                                influence_boundaries=influence_boundaries,
                                total_particles=self.stress_worker._initial_particle_count,
                                active_particles=active_particles,
                                fps=render_fps,
                                gpu_util=gpu_util,
                                elapsed_time=elapsed
                            )
                        else:
                            # No particle data - render empty frame to keep window alive
                            print(f"[WARNING] No particle data available for rendering (positions={positions})")
                            # Still need to update the display to process events
                            if hasattr(visualizer, 'pygame') and visualizer.pygame:
                                visualizer.pygame.display.flip()
                
                # Auto-scaling check for stress-test mode - increase backend particles every 5 seconds
                if self.config.auto_scale and elapsed - last_scale_check >= scale_interval:
                    current_sample = self.samples[-1] if self.samples else {}
                    gpu_util_check = current_sample.get('utilization', 0)
                    
                    # Target 98% GPU util for stress test
                    target_util = 98
                    
                    if not target_reached:
                        if gpu_util_check >= target_util - 1:
                            target_reached = True
                            target_reached_time = elapsed
                        elif current_backend_total < max_backend_total:
                            # Increase total backend particles
                            current_backend_total += backend_increment
                            if current_backend_total > max_backend_total:
                                current_backend_total = max_backend_total
                            
                            # Apply the new backend particle count
                            if self.stress_worker._backend_stress.is_initialized():
                                new_total_backend = current_backend_total
                                visible_count = self.stress_worker._initial_particle_count
                                self.stress_worker._backend_stress.scale_particles(new_total_backend)
                                
                                # Update workload display
                                if self.stress_worker.visualize:
                                    self.stress_worker.workload_type = f"Bounce Simulation ({visible_count:,} visible, {new_total_backend:,} backend, {self.stress_worker._method})"
                    
                    last_scale_check = elapsed
                
                # Check stop conditions
                if self.samples:
                    latest_sample = self.samples[-1]
                    stop = self.metrics_sampler.check_stop_conditions(latest_sample, self.config)
                    if stop:
                        self.stop_reason = stop
                        break
                
                # Check if user stopped
                if self.should_stop:
                    self.stop_reason = "User stopped"
                    break
                
                # For visualization mode, don't auto-close on window events - only stop on duration or user stop button
                # The user can close the pygame window manually if they want
                
                # Update progress
                self.progress = int((elapsed / self.config.duration_seconds) * 100)
        
        except Exception as e:
            print(f"[ERROR] Benchmark loop exception: {e}")
            import traceback
            traceback.print_exc()
            self.stop_reason = f"Error: {str(e)}"
        
        # Cleanup
        if visualizer:
            visualizer.close()
        
        return self._calculate_results()
    
    def _calculate_results(self) -> Dict[str, Any]:
        """Calculate benchmark results from samples."""
        elapsed_sec = time.time() - self.start_time if self.start_time else 0
        
        if not self.samples:
            return {
                'error': 'No samples collected',
                'duration_actual_sec': round(elapsed_sec, 2),
                'stop_reason': self.stop_reason or 'Unknown'
            }
        
        valid_samples = [s for s in self.samples if 'error' not in s]
        
        if not valid_samples:
            return {
                'error': 'All samples had errors',
                'duration_actual_sec': round(elapsed_sec, 2),
                'stop_reason': self.stop_reason or 'Unknown'
            }
        
        def calc_stats(key: str) -> Dict[str, float]:
            values = [s.get(key, 0) for s in valid_samples]
            return {
                'min': round(min(values), 2),
                'max': round(max(values), 2),
                'avg': round(sum(values) / len(values), 2),
            }
        
        avg_iter_time = sum(self.iteration_times) / len(self.iteration_times) if self.iteration_times else 0
        
        results = {
            'duration_actual_sec': round(elapsed_sec, 2),
            'samples_collected': len(valid_samples),
            'stop_reason': self.stop_reason,
            'completed_full': self.completed_full,
            'workload_type': self.stress_worker.workload_type,
            'benchmark_type': self.config.benchmark_type,
            'iterations_completed': self.stress_worker.iterations,
            'avg_iteration_time_ms': round(avg_iter_time, 2),
            'iterations_per_second': round(1000 / avg_iter_time, 2) if avg_iter_time > 0 else 0,
            'utilization': calc_stats('utilization'),
            'memory_used_mb': calc_stats('memory_used_mb'),
            'temperature_c': calc_stats('temperature_c'),
            'power_w': calc_stats('power_w'),
        }
        
        perf_stats = self.stress_worker.get_performance_stats(elapsed_sec)
        results['performance'] = perf_stats
        
        # Calculate scores
        temp_range = results['temperature_c']['max'] - results['temperature_c']['min']
        stability_score = max(0, 100 - int(temp_range * 5))
        thermal_score = max(0, min(100, int((90 - results['temperature_c']['max']) * 5)))
        
        if self.config.benchmark_type == 'gemm':
            tflops = perf_stats.get('tflops', 0)
            perf_score = min(100, int(tflops * 10))
        elif self.config.benchmark_type == 'particle':
            sps = perf_stats.get('steps_per_second', 0)
            perf_score = min(100, int(sps / 100000))
        else:
            perf_score = min(100, int(results['iterations_completed'] / 10))
        
        results['scores'] = {
            'stability': stability_score,
            'thermal': thermal_score,
            'performance': perf_score,
            'overall': int((stability_score + thermal_score + perf_score) / 3)
        }
        
        # Add web UI compatible format
        self._add_webui_format(results)
        
        return results
    
    def _add_webui_format(self, results: Dict[str, Any]):
        """Add fields expected by web UI."""
        # Web UI expects flat fields like avg_temperature, peak_temperature
        results['avg_temperature'] = results.get('temperature_c', {}).get('avg', 0)
        results['peak_temperature'] = results.get('temperature_c', {}).get('max', 0)
        results['avg_gpu_utilization'] = results.get('utilization', {}).get('avg', 0)
        results['avg_memory_usage'] = results.get('memory_used_mb', {}).get('avg', 0)
        results['avg_power_draw'] = results.get('power_w', {}).get('avg', 0)
        results['duration'] = results.get('duration_actual_sec', 0)
        results['total_iterations'] = results.get('iterations_completed', 0)
        
        # Add performance metrics based on benchmark type
        if results.get('benchmark_type') == 'particle':
            perf = results.get('performance', {})
            results['avg_steps_per_sec'] = perf.get('steps_per_second', 0)
            results['peak_steps_per_sec'] = perf.get('peak_steps_per_second', perf.get('steps_per_second', 0))
        elif results.get('benchmark_type') == 'gemm':
            perf = results.get('performance', {})
            results['avg_tflops'] = perf.get('tflops', 0)
            results['peak_tflops'] = perf.get('peak_tflops', perf.get('tflops', 0))
    
    def run(self, config: BenchmarkConfig, visualize: bool = False) -> Dict[str, Any]:
        """Run complete benchmark with configuration."""
        self.config = config
        self.samples = []
        self.iteration_times = []
        self.should_stop = False
        self.completed_full = False
        self.running = True
        self.progress = 0
        self.stop_reason = None
        
        # Initialize stress worker
        self.stress_worker = GPUStressWorker(
            benchmark_type=config.benchmark_type,
            config=config,
            visualize=visualize
        )
        
        try:
            gpu_info = self.get_gpu_info()
            
            self.results = {
                'timestamp': datetime.now().isoformat(),
                'config': {
                    'mode': config.mode,
                    'benchmark_type': config.benchmark_type,
                    'duration_seconds': config.duration_seconds,
                    'temp_limit_c': config.temp_limit_c,
                    'power_limit_w': config.power_limit_w,
                    'memory_limit_mb': config.memory_limit_mb,
                    'matrix_size': config.matrix_size if config.benchmark_type == 'gemm' else None,
                    'num_particles': config.num_particles if config.benchmark_type == 'particle' else None,
                },
                'gpu_info': gpu_info,
                'status': 'running',
            }
            
            # Get baseline
            run_mode = 'simulation' if visualize else 'benchmark'
            if 'name' in gpu_info:
                baseline = self.baseline_storage.get_baseline(gpu_info['name'], config.benchmark_type, run_mode)
                if baseline:
                    self.results['baseline'] = baseline
            
            results = self.run_stress_benchmark(visualize=visualize)
            self.results.update(results)
            self.results['status'] = 'completed'
            self.results['run_mode'] = run_mode
            
            # Save as baseline if completed
            if self.completed_full and 'name' in gpu_info:
                self.baseline_storage.save_baseline(gpu_info['name'], config.benchmark_type, self.results, run_mode)
                self.results['saved_as_baseline'] = True
            
        except KeyboardInterrupt:
            self.results['status'] = 'interrupted'
            self.results['error'] = 'Benchmark interrupted by user'
            self.stop_reason = 'User interrupted'
        except Exception as e:
            self.results['status'] = 'failed'
            self.results['error'] = str(e)
        finally:
            # Stop background metrics thread
            self.metrics_sampler.stop()
            
            # Ensure cleanup happens
            if self.stress_worker:
                try:
                    self.stress_worker.cleanup()
                except Exception:
                    pass
            self.running = False
            self.progress = 100
        
        return self.results
    
    def start(self, config: BenchmarkConfig, visualize: bool = False) -> None:
        """Start benchmark (alias for run() for backward compatibility)."""
        self.run(config, visualize)


# Global instance
_benchmark: Optional[GPUBenchmark] = None

def get_benchmark_instance() -> GPUBenchmark:
    """Get or create global benchmark instance."""
    global _benchmark
    if _benchmark is None:
        _benchmark = GPUBenchmark()
    return _benchmark
