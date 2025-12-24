<div style="text-align:center; margin:18px 0;">
  <img src="monitor/api/static/logo.png" alt="MyGPU logo"/>
</div>

> *MyGPU — Lightweight GPU Management Utility: a compact `nvidia-smi` wrapper with a clean web dashboard.*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-1.2.3-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Gallery

<details>
  <summary>Web Dashboard</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Use first image aspect ratio 1624x675 for slide frame; images fit inside using object-fit:contain -->
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="monitor/api/static/web1.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="monitor/api/static/web2.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="monitor/api/static/web3.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="monitor/api/static/web4.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
  </div>

</details>
<details>
  <summary>CLI</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">

  <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="monitor/api/static/cli1.png" style="width:100%; height:100%; object-fit:contain;" />
  </div>
  <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="monitor/api/static/cli2.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="monitor/api/static/cli3.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="monitor/api/static/cli4.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="monitor/api/static/cli5.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>

</details>

### Why use this?

- **Lightweight**: Minimal resource footprint.
- **Flexible**: Runs as a CLI tool, a background service, or a full-featured Web Dashboard.
- **Admin-Centric**: Includes features like **VRAM Enforcement** (auto-kill processes exceeding limits) and **Watchlists**.
- **Developer-Friendly**: Built-in benchmarking and stress-testing tools (GEMM, Particle Physics) to validate system stability.

---

## Features

- **Real-time Monitoring**:
  - Detailed GPU metrics (Utilization, VRAM, Power, Temp).
  - System metrics (CPU, RAM, etc.).

- **Admin & Enforcement**:
  - **VRAM Caps**: Set hard limits on VRAM usage per GPU.
  - **Auto-Termination**: Automatically terminate processes that violate VRAM policies (Admin only).
  - **Watchlists**: Monitor specific PIDs or process names.

- **Benchmarking & Simulation**:
  - **Stress Testing**: Configurable GEMM workloads to test thermal throttling and stability.
  - **Visual Simulation**: Interactive 3D particle physics simulation to visualize GPU load.

---

## Roadmap & Future Work

Contributions are welcome! Main future points to cover would be:

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

---

## License

MIT License. See [LICENSE](LICENSE) for details.
