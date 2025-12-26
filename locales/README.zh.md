# MyGPU: GPU 管理工具

*MyGPU：一款轻量级的 GPU 管理工具：一个精致的 `nvidia-smi` 封装器，配有一个优雅的网络仪表盘。*

<!-- 以下 shields.io 徽章部分，保持原样 -->
![许可证](https://img.shields.io/badge/许可证-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![版本](https://img.shields.io/badge/版本-1.2.3-blue)
![平台](https://img.shields.io/badge/平台-Windows-lightgrey)
![CUDA 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## 画廊

### 网络仪表盘

<details>
  <summary>网络仪表盘</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- 使用第一张图片的宽高比 1624x675 作为滑动框架；图片使用 `object-fit: contain` 填充 -->
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
<details>
  <summary>命令行界面 (CLI)</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli1.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli2.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli3.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli4.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli5.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
  </div>
</details>

### 为什么使用这个工具？

- **轻量级**：资源占用最小。
- **灵活**：作为命令行工具、网络仪表盘或全功能网络仪表盘运行。
- **管理员友好**：包括 VRAM 限制（自动终止超出限制的进程）和监控列表等功能。
- **开发者友好**：内置基准测试和粒子物理模拟，用于验证系统稳定性。

---

## 功能

- **实时监控**：
  - 详细的 GPU 指标（利用率、VRAM、功耗、温度）。
  - 系统指标（CPU、内存等）。

- **管理员和执行**：
  - **VRAM 限制**：为每个 GPU 设置 VRAM 使用硬限制。
  - **自动终止**：自动终止违反 VRAM 策略的进程（仅管理员）。
  - **监控列表**：监控特定 PID 或进程名称。

- **基准测试和模拟**：
  - **压力测试**：配置可配置的 GEMM 工作负载以测试热量限制和稳定性。
  - **视觉模拟**：交互式 3D 粒子物理模拟以可视化 GPU 加载。

---

## 路线图和未来工作

欢迎贡献！主要未来要点如下：

- **多 GPU 支持**：增强多卡设置和 NVLink 拓扑的处理。
- **容器化**：官方 Docker 支持以方便在容器环境中部署。
- **远程访问**：SSH 隧道集成和安全远程管理。
- **跨平台**：
  - [ ] Linux 支持（Ubuntu/Debian 重点）。
  - [ ] macOS 支持（Apple Silicon 监控）。
- **硬件无关性**：
  - [ ] AMD ROCm 支持。
  - [ ] Intel Arc 支持。
- [ ] 多语言文档（支持 GitHub 社区最流行的语言）。

请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解如何参与。

---

## 要求

- **OS**：Windows 10/11
- **Python**：3.10+
- **硬件**：NVIDIA GPU 和已安装的驱动程序。
- **CUDA**：12.x（严格要求用于基准测试/模拟功能）。
  - *注意：如果未检测到 CUDA 12.x，则 GPU 特定基准功能将被禁用。*

---

## 安装

工具支持模块化安装以适应您的需求：

### 1. 最小（仅命令行界面）

适合无头服务器或后台监控。

- 命令行界面。
- 基本的系统/GPU 指标。

### 2. 标准（命令行 + 网络仪表盘）

适合大多数用户。

- 包括网络仪表盘。
- REST API 端点。
- 实时图表。
- 但无模拟或基准测试。

### 3. 完整（标准 + 视觉化）

适合开发和压力测试。

- 包括模拟。
- PyTorch/CuPy 依赖基准测试。

### 快速开始

1. **下载** 最新版本或克隆仓库。
2. **运行设置**：

   ```powershell
   .\setup.ps1
   ```

3. **启动**：

```powershell
# 启动网络仪表盘（标准/完整）
python health_monitor.py web

# 启动命令行
python health_monitor.py cli
```