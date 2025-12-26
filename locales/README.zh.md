# MyGPU: 轻量级 GPU 管理工具

一个紧凑的 `nvidia-smi` 包装器，配有一个干净的网络仪表板。

![许可证](https://img.shields.io/badge/许可证-MIT-蓝色.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-蓝色)
![版本](https://img.shields.io/badge/版本-1.2.3-蓝色)
![平台](https://img.shields.io/badge/平台-Windows-灰色)
![CUDA 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## 画廊

### 网络仪表板

<details>
  <summary>网络仪表板</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web1.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web2.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web3.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web4.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
  </div>
</details>

### 命令行界面 (CLI)

<details>
  <summary>命令行界面 (CLI)</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli1.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <!-- 其他 CLI 图像 -->
  </div>
</details>

### 为什么使用这个工具？

- **轻量级**：资源占用最小。
- **灵活**：作为 CLI 工具、后台服务或全功能网络仪表板运行。
- **管理员友好**：包含 VRAM 限制（自动终止超出限制的进程）和监控列表等功能。
- **开发人员友好**：内置基准测试和粒子物理模拟工具，用于验证系统稳定性。

---

## 功能

- **实时监控**：
  - GPU 指标（利用率、VRAM、功耗、温度）。
  - 系统指标（CPU、内存等）。
- **管理员和执行**：
  - **VRAM 限制**：为每个 GPU 设置 VRAM 使用量硬限制。
  - **自动终止**（仅管理员可操作）：自动终止违反 VRAM 策略的进程。
  - **监控列表**：监控特定 PID 或进程名称。
- **基准测试和模拟**：
  - **压力测试**：配置可配置的 GEMM 工作负载以测试热量限制和稳定性。
  - **视觉模拟**：交互式粒子物理模拟，以可视化 GPU 加载。

---

## 路线图和未来工作

欢迎贡献！未来要覆盖的主要点如下：

- **多 GPU 支持**：增强多卡设置和 NVLink 拓扑的处理。
- **容器化**：官方 Docker 支持，以便在容器环境中轻松部署。
- **远程访问**：SSH 隧道集成和安全远程管理。
- **跨平台**：
  - [ ] Windows 支持（Ubuntu/Debian 重点）。
  - [ ] macOS 支持（Apple Silicon 监控）。
- **硬件独立**：
  - [ ] AMD ROCm 支持。
  - [ ] Intel Arc 支持。
- [ ] 多语言文档（支持 GitHub 上最受欢迎的语言）。

请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解如何参与。

---

## 要求

- **操作系统**：Windows 10/11
- **Python**：3.10+
- **硬件**：NVIDIA GPU 和已安装的驱动程序。
- **CUDA**：12.x 工具包（用于基准测试/模拟功能）。
  - *注意：如果未检测到 CUDA 12.x，则基准测试/模拟功能将被禁用。*

---

## 安装

工具支持模块化安装，以适应您的需求：

### 1. 最小（仅 CLI）

适用于无显示器的服务器或后台监控。

- 命令行界面。
- 基本系统/GPU 指标。

### 2. 标准（CLI + 网络仪表板）

适用于大多数用户。

- 包括网络仪表板。
- REST API 端点。
- 实时图表。

### 3. 完整（标准 + 视觉化）

适用于开发和压力测试。

- 包括粒子模拟。
- 用于基准测试的 PyTorch/CuPy 依赖项。

### 快速入门

1. **下载** 最新版本或克隆仓库。
2. **运行设置**：

   ```powershell
   .\setup.ps1
   ```

3. **启动**：

   ```powershell
   # 启动网络仪表板（标准/完整）
   python health_monitor.py web

   # 启动 CLI
   python health_monitor.py cli
   ```