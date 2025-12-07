# GPU Health Monitor

Professional GPU monitoring and stress testing tool with real-time visualization and performance baselines.

## Features

- **Real-time Monitoring**: GPU utilization, memory, temperature, power, and system metrics
- **Web Dashboard**: Interactive charts with live updates and historical data
- **GPU Stress Testing**: Particle simulation with auto-scaling backend load
- **Performance Baselines**: Track and compare GPU performance over time
- **Visualization**: Real-time particle physics simulation with interactive controls
- **Multiple Test Modes**: Quick, Standard, Extended, Stress Test, and Custom configurations

## Requirements

- Python 3.8+
- NVIDIA GPU with drivers
- CUDA Toolkit 12.0+ (for GPU benchmarking)
- Windows 10/11 or Linux

## Quick Start

### Installation

1. **Download** the latest release from [Releases](https://github.com/DataBoySu/cluster-monitor/releases)

2. **Extract** and run setup:

   ```powershell
   Expand-Archive cluster-health-monitor.zip -DestinationPath C:\Tools\
   cd C:\Tools\cluster-health-monitor
   .\setup.ps1
   ```

3. **Launch** web dashboard:

   ```powershell
   python health_monitor.py web
   ```text
   Access at: http://localhost:8090

### Usage

**Web Dashboard (Recommended)**

```powershell
python health_monitor.py web
```

**Terminal Interface**

```powershell
python health_monitor.py cli
```

**Command-Line Benchmark**

```powershell
# Quick 15s test
python health_monitor.py benchmark --mode quick

# Stress test with auto-scaling
python health_monitor.py benchmark --mode stress-test
```

## Benchmark Modes

| Mode | Duration | Description |
|------|----------|-------------|
| **Quick** | 15s | Fast baseline check with fixed workload |
| **Standard** | 60s | Standard benchmark for consistent results |
| **Extended** | 180s | Long-term stability and thermal testing |
| **Stress Test** | 60s | Auto-scaling load targeting 98% GPU utilization |
| **Custom** | Variable | User-defined parameters and limits |

### Stress Test Auto-Scaling

The Stress Test mode dynamically increases backend particle load:

- **Start**: 200,000 backend particles
- **Increment**: +50,000 particles every 5 seconds
- **Maximum**: 500,000 backend particles
- **Target**: 98% GPU utilization
- **Timeout**: 60 seconds

This provides progressive GPU loading while maintaining responsive visualization.

## Visualization

Interactive particle simulation with:

- **Real-time Physics**: GPU-accelerated particle collision and bouncing
- **Interactive Controls**: Gravity, ball speed, splitting behavior
- **Click Spawning**: Add particles dynamically during simulation
- **FPS Overlay**: Monitor render performance
- **GPU Metrics**: Live utilization display

## Configuration

Edit `config.yaml` for custom settings:

```yaml
monitoring:
  interval_seconds: 5
  history_retention_hours: 168

alerts:
  gpu_temperature_warn: 80
  gpu_temperature_critical: 90

web:
  host: 0.0.0.0
  port: 8090
```

## API Reference

REST API endpoints (web mode):

- `GET /` - Web dashboard
- `GET /api/status` - Current GPU metrics
- `GET /api/history` - Historical data
- `POST /api/benchmark/start` - Start benchmark
- `GET /api/benchmark/status` - Benchmark progress
- `POST /api/benchmark/stop` - Stop benchmark
- `GET /api/benchmark/baseline` - Retrieve saved baseline

## Troubleshooting

**nvidia-smi not found**

- Install NVIDIA drivers: <https://www.nvidia.com/download/index.aspx>

**CUDA not detected**

- Download CUDA Toolkit: <https://developer.nvidia.com/cuda-downloads>
- Re-run `setup.ps1` after installation

**Benchmark disabled**

- GPU compute libraries not installed
- Run `setup.ps1` and install CuPy or PyTorch when prompted

**Port already in use**

- Change port: `python health_monitor.py web --port 3000`

## License

MIT License - See LICENSE file
