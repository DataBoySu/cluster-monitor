# Cluster Health Monitor

Real-time GPU and system monitoring with web dashboard and CLI interface. Features intelligent GPU stress testing with auto-scaling workloads and performance baselines.

## Features

### Monitoring

- Real-time GPU metrics (utilization, memory, temperature, power)
- System metrics (CPU, memory, disk I/O)
- Web dashboard with live charts
- Terminal interface with auto-refresh
- Historical data storage and alerting

### GPU Benchmarking

- GEMM (matrix multiplication) stress test
- Particle simulation workload
- Auto-scaling stress test (dynamically increases load to 98% GPU utilization)
- Performance baseline tracking per GPU and benchmark type
- Multiple test modes: Quick (15s), Standard (60s), Extended (180s), Stress Test, Custom

## Requirements

- Python 3.8+
- NVIDIA GPU with drivers installed
- CUDA Toolkit 12.0+ (for benchmarking)

## Installation

### 1. Download

Download the latest release ZIP from [Releases](https://github.com/DataBoySu/cluster-monitor/releases).

Extract to your desired location:

```powershell
Expand-Archive cluster-health-monitor-v1.0.0.zip -DestinationPath C:\Tools\
cd C:\Tools\cluster-health-monitor
```

### 2. Run Setup

```powershell
.\setup.ps1
```

The setup script will:

- Check for NVIDIA drivers and CUDA
- Create Python virtual environment
- Install required dependencies
- Prompt for optional GPU benchmark libraries (CuPy or PyTorch)
- Verify installation

### 3. Verify

```powershell
.\venv\Scripts\Activate.ps1
python health_monitor.py --help
```

## Usage

### Web Dashboard (Default)

```powershell
python health_monitor.py
# Change port: python health_monitor.py --port 3000
```

Access at: http://localhost:8090

Features:

- Real-time GPU/system metrics
- Interactive benchmark controls
- Live performance charts
- Historical data visualization
- In-dashboard updates

### Terminal Dashboard

```powershell
python health_monitor.py cli
```

Displays live metrics in terminal with auto-refresh.

### CLI Benchmark

```powershell
# Quick 15-second test
python health_monitor.py benchmark --mode quick

# Standard 60-second test  
python health_monitor.py benchmark --mode standard

# Stress test with auto-scaling (pushes GPU to 98% util)
python health_monitor.py benchmark --mode stress-test --type particle

# Extended 180-second burn-in
python health_monitor.py benchmark --mode extended

# Custom configuration
python health_monitor.py benchmark --mode custom --duration 120 --temp-limit 85
```

## Benchmark Modes

| Mode | Duration | Workload | Auto-Scale | Use Case |
|------|----------|----------|------------|----------|
| Quick | 15s | Fixed | No | Quick baseline check |
| Standard | 60s | Fixed | No | Standard benchmark |
| Extended | 180s | Fixed | No | Long-term stability |
| Stress Test | 60s | Dynamic | Yes | Maximum GPU load testing |
| Custom | Variable | Fixed | Optional | User-defined parameters |

### Auto-Scaling Stress Test

The Stress Test mode automatically increases workload intensity:

1. Starts with baseline workload (2048x2048 GEMM or 100K particles)
2. Every 2 seconds, checks GPU utilization
3. Scales workload aggressively if GPU util < target:
   - `<70% util`: 2.0x scaling
   - `70-85% util`: 1.5x scaling  
   - `85-93% util`: 1.2x scaling
   - `>93% util`: Target reached
4. Continues scaling up to 15 times or until 98% GPU utilization achieved

Example progression:

```text
100K particles → 200K → 400K → 800K → 1.2M → 1.8M → 2.2M → 2.6M (94% GPU util)
```

## Benchmark Types

### GEMM (Matrix Multiplication)

Dense matrix multiplication for maximum compute stress. Measures TFLOPS.

```bash
python health_monitor.py benchmark --type gemm --mode stress-test
```

### Particle Simulation

Vectorized particle physics simulation with collision detection. Measures steps/second.

```bash
python health_monitor.py benchmark --type particle --mode stress-test
```

## Configuration

Edit `config.yaml`:

```yaml
monitoring:
  interval_seconds: 5
  history_retention_hours: 168

alerts:
  gpu_temperature_warn: 80
  gpu_temperature_critical: 90
  gpu_memory_usage_warn: 90

web:
  host: 0.0.0.0
  port: 8090

storage:
  path: ./metrics.db
```

## API Endpoints

When running web server (`--web`):

- `GET /` - Web dashboard
- `GET /api/status` - Current metrics
- `GET /api/history` - Historical data
- `POST /api/benchmark/start` - Start benchmark
- `GET /api/benchmark/status` - Benchmark progress
- `POST /api/benchmark/stop` - Stop benchmark

## Updates

### CLI

```powershell
python health_monitor.py --update
```

### Web Dashboard

Click the "Check for Updates" button in the dashboard.

## Troubleshooting

### "nvidia-smi not found"
Install NVIDIA drivers from https://www.nvidia.com/download/index.aspx

### "No CUDA Toolkit found"
Download CUDA from https://developer.nvidia.com/cuda-downloads
Re-run `.\setup.ps1` after installation.

### Web dashboard not loading data
- Check port 8090 is available
- Try: `http://127.0.0.1:8090`
- Check firewall settings

### Benchmark features grayed out

GPU benchmark libraries not installed. Run setup script and select CuPy or PyTorch installation.

## License

MIT License - See LICENSE file

## Acknowledgments

- Built with FastAPI, Rich, Chart.js
- GPU compute via CuPy and PyTorch
- Inspired by nvidia-smi and GPU monitoring tools

## Support

GitHub: https://github.com/DataBoySu/cluster-monitor
