# Cluster Health Monitor

A lightweight, real-time monitoring tool for NVIDIA GPUs. Track GPU utilization, memory, temperature, and power during ML training or any GPU workload.
A real-time, local-first monitoring tool for GPU and system health, featuring both a terminal dashboard and a web interface.

## System Requirements
![Web UI Screenshot](https://i.imgur.com/CjBgOfJ.png) _(placeholder)_

### Hardware
## Features

- NVIDIA GPU (GeForce, RTX, Quadro, Tesla, etc.)

### Software
## Requirements

- Windows 10/11 or Linux (Ubuntu 18.04+)
- Python 3.8 or higher
- NVIDIA Driver 450.0 or higher
- Python 3.8+
- NVIDIA GPU with drivers installed (for GPU monitoring).
- NVIDIA CUDA Toolkit (for GPU benchmarking features).

### Verify Your Setup
## Quick Setup

Before installing, confirm your GPU is detected:
1.  **Clone the repository:**
    ```sh
    git clone <your-repo-url>
    cd cluster-health-monitor
    ```

2.  **Create a virtual environment (recommended):**
    ```sh
    python -m venv .venv
    ```
    Activate it:
    -   Windows: `.\.venv\Scripts\activate`
    -   macOS/Linux: `source .venv/bin/activate`

3.  **Install dependencies:**
    Install the core dependencies from `requirements.txt`.
    ```sh
    pip install -r requirements.txt
    ```

4.  **Install GPU Benchmarking Libraries (Optional):**
    To enable the GPU benchmark tab, you must install either CuPy or PyTorch compatible with your system's CUDA version.
    ```sh
    # Example for CUDA 13.x
    pip install cupy-cuda13x
    ```

## How to Run

The application is controlled with simple, direct commands.

### Command Overview

| Command                               | Description                                             |
| ------------------------------------- | ------------------------------------------------------- |
| `python health_monitor.py`            | Starts the terminal dashboard (the default action).     |
| `python health_monitor.py term`       | Explicitly starts the terminal dashboard.               |
| `python health_monitor.py web`        | Starts the web interface.                               |
| `python health_monitor.py benchmark`  | Runs a GPU benchmark from the command line.             |
| `python health_monitor.py [cmd] --help` | Shows detailed help for any command.                    |

### Examples

**Launch the Web Dashboard:**
This will start the web server, typically at `http://127.0.0.1:8090`.
```sh
python health_monitor.py web
```

**Launch the Terminal Dashboard:**
This will launch the live-updating terminal interface.
```sh
python health_monitor.py term
```

**Run a GPU Benchmark:**
Execute a benchmark directly from the command line.
```sh
python health_monitor.py benchmark --type gemm --duration 60
```

Press Ctrl+C to exit.

### Single Snapshot

Print GPU info once and exit:

```python
python health_monitor.py --once
For a full list of commands and options, use `--help`:
```sh
python health_monitor.py --help
python health_monitor.py monitor --help
python health_monitor.py benchmark --help
```

### Web Dashboard (Optional)

Start a web server with browser-based dashboard:

```python
python health_monitor.py --web --port 8888
```

Then open <http://localhost:8888> in your browser.

## What You See

The monitor displays:

- GPU utilization (%)
- Memory usage (used/total GB)
- Temperature (C)
- Power draw (W)
- CPU and RAM usage (system)

## Configuration

Edit `config.yaml` to customize:

```yaml
monitoring:
  interval_seconds: 5    # How often to refresh

alerts:
  gpu_temperature_warn: 80     # Warn at 80C
  gpu_temperature_critical: 90 # Critical at 90C
```

## Troubleshooting

### "No NVIDIA GPU detected"

- Run `nvidia-smi` to verify driver is installed
- Make sure you have a discrete NVIDIA GPU (not Intel/AMD integrated)

### "pynvml not found" or "ModuleNotFoundError"

- Make sure virtual environment is activated
- Run: `pip install pynvml`

### "rich not found"

- Run: `pip install rich`

### Web dashboard not loading

- Install web dependencies: `pip install fastapi uvicorn`
- Check if port 8080 is available

### High CPU usage

- Increase refresh interval in config.yaml

## Dependencies

- pynvml - NVIDIA GPU metrics
- psutil - System metrics (CPU, RAM, disk)
- pyyaml - Configuration file parsing
- click - Command line interface
- rich - Terminal UI
- fastapi - REST API
- uvicorn - Web server

## License

MIT License
