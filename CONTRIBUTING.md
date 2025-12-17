# Contributing to Cluster Health Monitor

First off, thanks for taking the time to go through my project!

This project started as a personal tool for monitoring my local GPU setup, while I play with the AI models. It has grown into a lightweight, "nvidia-smi wrapper on steroids" that makes it easy to manage GPUs, for developers and researchers.

All contributions are welcome, bug fixes, new features, documentation improvements, and more.

## Getting Started

### Prerequisites

- **OS**: Windows 10/11
- **Python**: 3.10+
- **CUDA**: Toolkit 12.x (required for GPU benchmarking features).

### Setting Up the Development Environment

1. **Clone the repository**:

   ```bash
   git clone https://github.com/DataBoySu/Local-GPUMonitor.git
   # Contributing to GPU Health Monitor

   Thank you for taking an interest in contributing. This document describes how to get the repository locally, coding and commit guidelines, and the process for submitting changes.

   Repository: https://github.com/DataBoySu/Local-GPUMonitor

   ## Quick Start (clone & run)

   1. Fork the repository on GitHub and clone your fork:

   ```bash
   git clone https://github.com/DataBoySu/Local-GPUMonitor.git
   cd Local-GPUMonitor
   ```

   2. Create and activate a Python virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

   4. Run the application (web dashboard):

   ```powershell
   python health_monitor.py web
   ```

   Or run the CLI mode:

   ```powershell
   python health_monitor.py cli
   ```

   ## Branching & Commit Guidelines

   - Branch from `main` for new work: `git checkout -b feat/short-description` or `fix/short-description`.
   - Keep commits small and focused. Use clear commit messages (imperative present tense):

     `Add VRAM cap enforcement for per-process watchlist`

   - Rebase or squash when appropriate before opening a PR to keep history tidy.

   ## Pull Requests

   1. Push your branch to your fork and open a Pull Request against `DataBoySu/Local-GPUMonitor:main`.
   2. In the PR description include:
      - A short summary of the change/with images if possible.
      - Motivation and any relevant issue links.
      - Testing steps to reproduce or verify the change.
   3. Ensure CI (if any) passes and address review comments promptly.

   ## Code Style & Tests

   - Python: follow PEP 8 and use type hints where appropriate. We prefer readable, explicit code.
   - JavaScript: keep vanilla JS simple and modular. Follow consistent indentation and naming.
   - Add tests where appropriate (unit tests for collectors, integration tests for API endpoints). If you add tests, include instructions to run them in your PR.

   ## Running Locally (developer tips)

   - To run the web server with auto-reload during development, use your editor's Python run configuration or run with `watchdog`/`honcho` if you add it.
   - For debugging GPU collectors on non-GPU machines, mock or stub out GPU calls (see `monitor/collectors` for structure).

   ## Communication, Reporting Issues & Security

   - Use GitHub Discussions for general conversation and design proposals: <https://github.com/DataBoySu/Local-GPUMonitor/discussions/9>
   - Open issues for bugs, feature requests, and design discussions
   - For sensitive security issues, please contact the repository owner directly instead of opening a public issue.

   ## License

   This project is distributed under the MIT License. See `LICENSE` for details.

   With your help, I would like to keeps this project useful and evolving.
