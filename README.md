# Cluster Health Monitor

**A lightweight, admin-focused GPU monitoring and management utility.**

> *Essentially an `nvidia-smi` wrapper built for varying levels of complexity.*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

## Gallery

```markdown
<!-- Web dashboard demo GIF -->
![Web Dashboard Demo](assets/gallery/web-dashboard-demo.gif)

<!-- CLI mode screenshot -->
![CLI Mode](assets/gallery/cli-mode.png)
```

---

## Overview

**Cluster Health Monitor** started as a personal project for local monitoring and testing while working with AI models. It has evolved into a versatile utility that bridges the gap between simple command-line tools and complex enterprise monitoring solutions.

Whether you are a researcher fine-tuning LLMs, a developer testing CUDA kernels, or an admin managing a local compute cluster, this tool provides the visibility and control you need without the overhead.

### Why use this?

- **Lightweight**: Minimal resource footprint. It gets out of your way.
- **Flexible**: Runs as a CLI tool, a background service, or a full-featured Web Dashboard.
- **Admin-Centric**: Includes features like **VRAM Enforcement** (auto-kill processes exceeding limits) and **Watchlists**.
- **Developer-Friendly**: Built-in benchmarking and stress-testing tools (GEMM, Particle Physics) to validate system stability.

---
 
## Features

- **Real-time Monitoring**:
  - Detailed GPU metrics (Utilization, VRAM, Power, Temp, Fan Speed).
  - System metrics (CPU, RAM, Disk I/O).
  - Per-process VRAM usage tracking.

- **Admin & Enforcement**:
  - **VRAM Caps**: Set hard limits on VRAM usage per GPU.
  - **Auto-Termination**: Automatically terminate processes that violate VRAM policies (Admin only).
  - **Watchlists**: Monitor specific PIDs or process names.

- **Benchmarking & Simulation**:
  - **Stress Testing**: Configurable GEMM workloads to test thermal throttling and stability.
  - **Visual Simulation**: Interactive 3D particle physics simulation to visualize GPU load.
  - **TFLOPS Estimation**: Real-time performance estimation during simulations.

---

## Roadmap & Future Work

We are actively working on expanding the capabilities of Cluster Health Monitor. Contributions are welcome!

- **Multi-GPU Support**: Enhanced handling for multi-card setups and NVLink topologies.
- **Containerization**: Official Docker support for easy deployment in containerized environments.
- **Remote Access**: SSH tunneling integration and secure remote management.
- **Cross-Platform**:
  - [ ] Linux Support (Ubuntu/Debian focus).
  - [ ] macOS Support (Apple Silicon monitoring).
- **Hardware Agnostic**:
  - [ ] AMD ROCm support.
  - [ ] Intel Arc support.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get involved.

---

## Requirements

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: NVIDIA GPU with installed drivers.
- **CUDA**: Toolkit 12.x (Strictly required for Benchmarking/Simulation features).
  - *Note: If CUDA 12.x is not detected, GPU-specific benchmarking features will be disabled.*

---

## Installation

The tool supports modular installation to fit your needs:

### 1. Minimal (CLI Only)

Best for headless servers or background monitoring.

- Command-line interface.
- Basic system/GPU metrics.

### 2. Standard (CLI + Web UI)

Best for most users.

- Includes Web Dashboard.
- REST API endpoints.
- Real-time charts.

### 3. Full (Standard + Visualization)

Best for development and stress testing.

- Includes Particle Simulation.
- PyTorch/CuPy dependencies for benchmarking.

### Quick Start

1. **Download** the latest release or clone the repo.
2. **Run Setup**:
  ```powershell
  .\setup.ps1
  ```

3. **Launch**:

```powershell
# Start the web dashboard (Standard/Full)
python health_monitor.py web

# Start the CLI
python health_monitor.py cli
```

Access the dashboard at `http://localhost:8090` when running in web mode.
---

## License

MIT License. See [LICENSE](LICENSE) for details.

## Detailed Modes

### Web Dashboard

The web dashboard runs a FastAPI server that serves a lightweight frontend (vanilla JS). It provides real-time charts, per-process details, and desktop notifications on Windows.

Start the web dashboard with:

```powershell
python health_monitor.py web
```

By default the dashboard is available at `http://localhost:8090`.

### CLI Mode

The CLI mode is intended for quick checks and scripted workflows. It provides concise, human-friendly output suitable for headless machines and automation.

Start the CLI with:

```powershell
python health_monitor.py cli
```

Use the CLI for cron jobs, automation, or running on machines without a browser.
