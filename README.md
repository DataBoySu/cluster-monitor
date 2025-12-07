# GPU Health Monitor

Professional GPU monitoring and stress testing tool with real-time visualization and performance baselines.

## Features

- **Real-time Monitoring**: GPU utilization, memory, temperature, power, and system metrics
- **Web Dashboard**: Interactive charts with live updates and historical data (optional)
- **GPU Stress Testing**: Particle simulation with auto-scaling backend load
- **Performance Baselines**: Track and compare GPU performance over time
- **Visualization**: Real-time particle physics simulation with interactive controls (optional)
- **Multiple Test Modes**: Quick, Standard, Extended, Stress Test, and Custom configurations
- **Modular Installation**: Install only what you need (CLI-only, with Web UI, or Full)

## Requirements

- Python 3.8+
- NVIDIA GPU with drivers (optional - for GPU benchmarking)
- CUDA Toolkit 12.0+ (optional - for GPU acceleration)
- Windows 10/11 or Linux

## Installation Options

The tool supports three installation types:

### 1. MINIMAL (CLI only)

- Command-line interface with rich output
- Basic monitoring (click, rich, psutil)
- Smallest installation (~10 MB)
- **Use case**: Headless servers, minimal footprint

### 2. STANDARD (CLI + Web UI)

- Everything in Minimal
- Web dashboard with real-time charts
- REST API endpoints
- **Use case**: Remote monitoring, multiple users

### 3. FULL (Standard + Visualization + GPU)

- Everything in Standard
- Particle simulation visualization
- GPU benchmarking support
- **Use case**: Full-featured installation, development

## Quick Start

### Installation

1. **Download** the latest release from [Releases](https://github.com/DataBoySu/cluster-monitor/releases)

2. **Extract** and run setup:

   ```powershell
   Expand-Archive cluster-health-monitor.zip -DestinationPath C:\Tools\
   cd C:\Tools\cluster-health-monitor
   .\setup.ps1
   ```

3. **Select** installation type (1=Minimal, 2=Standard, 3=Full)

4. **Launch**:

   ```powershell
   # For MINIMAL or STANDARD:
   python health_monitor.py cli
   
   # For STANDARD or FULL:
   python health_monitor.py web
   ```

### Usage

**Web Dashboard** (Standard/Full installations)

```powershell
python health_monitor.py web
```

Access at: <http://localhost:8090>

**Terminal Interface** (All installations)

```powershell
python health_monitor.py cli
```

**Command-Line Benchmark** (Full installation with GPU libraries)

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

nvidia-smi not found

- Install NVIDIA drivers: <https://www.nvidia.com/download/index.aspx>

CUDA not detected

- Download CUDA Toolkit: <https://developer.nvidia.com/cuda-downloads>
- Re-run `setup.ps1` after installation

Benchmark disabled / Simulation button grayed out

- GPU compute libraries not installed or not detected
- Solution 1: Run `python health_monitor.py refresh` to update detection cache
- Solution 2: Re-run `setup.ps1` and install CuPy or PyTorch

CuPy installation fails on CUDA 13.0

- Use: `pip install "cupy-cuda12x>=13.0.0"`
- CuPy 13.x supports CUDA 12.x and 13.0

Port already in use

- Change port: `python health_monitor.py web --port 3000`

## License

MIT License - See LICENSE file
