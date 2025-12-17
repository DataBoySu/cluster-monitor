# Contributing to Cluster Health Monitor

First off, thanks for taking the time to contribute! 🎉

This project started as a personal tool for local monitoring and testing of AI models. It has grown into a lightweight, "nvidia-smi wrapper on steroids" that aims to simplify GPU management for developers and researchers.

We welcome contributions of all kinds—bug fixes, new features, documentation improvements, and more.

## Getting Started

### Prerequisites
- **OS**: Windows 10/11 (currently the primary target, though Linux/Mac support is on the roadmap).
- **Python**: 3.8+
- **CUDA**: Toolkit 12.x (required for GPU benchmarking features).

### Setting Up the Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/cluster-health-monitor.git
   cd cluster-health-monitor
   ```

2. **Create a virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```powershell
   # Run the web server
   python health_monitor.py web
   ```

## Project Structure

- `monitor/`: Core package source.
  - `api/`: FastAPI server and static assets (frontend).
  - `collectors/`: System and GPU metric collectors.
  - `benchmark/`: GPU stress testing and particle simulation logic.
  - `alerting/`: Notification logic (Windows toasts).
- `health_monitor.py`: Main entry point.

## Roadmap & Future Work

We are actively looking for help with:
- **Multi-GPU Support**: robust handling of multi-card setups.
- **Cross-Platform Support**: Porting to Linux and macOS.
- **Containerization**: Docker support for easy deployment.
- **Remote Access**: SSH tunneling or secure remote monitoring capabilities.
- **Hardware Support**: AMD (ROCm) and Intel (Arc) GPU support.

## Submitting Changes

1. **Fork the repo** and create your branch from `main`.
2. **Make your changes**. Ensure code is clean and commented where necessary.
3. **Test your changes**. Run the monitor in both CLI and Web modes to ensure no regressions.
4. **Submit a Pull Request**. Describe your changes in detail and link to any relevant issues.

## Code Style

- **Python**: Follow PEP 8. We use type hints where possible.
- **JavaScript**: Keep it vanilla and simple. We avoid heavy frontend frameworks to keep the project lightweight.

## Community

If you have questions or want to discuss ideas, please open a [Discussion](https://github.com/yourusername/cluster-health-monitor/discussions) or an Issue.

Happy coding! 🚀
