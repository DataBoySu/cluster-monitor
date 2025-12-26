<div align="center">
  <a href="../README.md">🇺🇸 English</a> |
  <a href="../README.de.md">🇩🇪 Deutsch</a> |
  <a href="../README.fr.md">🇫🇷 Français</a> |
  <a href="../README.es.md">🇪🇸 Español</a> |
  <a href="../README.ja.md">🇯🇵 日本語</a> |
  <a href="../README.zh.md">🇨🇳 中文</a> |
  <a href="../README.pt.md">🇵🇹 Português</a> |
  <a href="../README.ko.md">🇰🇷 한국어</a> |
  <a href="../README.hi.md">🇮🇳 Hindi</a>
</div>

<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU logo"/>
</div>

> *轻量级GPU管理工具：一个紧凑的`nvidia-smi`包装器，配有一个优雅的网络仪表盘。*

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
  <summary>CLI</summary>
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

</details>

### 为什么使用这个工具？

- **轻量级**：资源占用最小。
- **灵活**：作为命令行工具运行，或全功能网络仪表盘。
- **管理员友好**：包含VRAM限制（自动终止超出限制的进程）和监控列表等功能。
- **开发者友好**：内置基准测试和压力测试工具（GEMM、粒子物理），验证系统稳定性。

---

## 功能

- **实时监控**：
  - GPU指标（利用率、VRAM、功耗、温度）。
  - 系统指标（CPU、内存等）。

- **管理员和执行**：
  - **VRAM限制**：为每个GPU设置VRAM使用硬限制。
  - **自动终止**（仅管理员可操作）：自动终止违反VRAM策略的进程。
  - **监控列表**：监控特定PID或进程名称。

- **基准测试和模拟**：
  - **压力测试**：配置可配置的GEMM工作负载，测试热量限制和稳定性。
  - **可视化模拟**：交互式3D粒子物理模拟，可视化GPU负载。

---

## 路线图和未来工作

欢迎贡献！主要未来要点包括：

- **多GPU支持**：增强多卡设置和NVLink拓扑的处理。
- **容器化**：官方Docker支持，方便在容器环境中部署。
- **远程访问**：SSH隧道集成和安全远程管理。
- **跨平台**：
  - [ ] Linux支持（Ubuntu/Debian重点）。
  - [ ] macOS支持（Apple Silicon监控）。
- **硬件无差异**：
  - [ ] AMD ROCm支持。
  - [ ] Intel Arc支持。
- ~~**多语言文档**：支持GitHub上最受欢迎的语言。~~

参阅[CONTRIBUTING.md](../CONTRIBUTING.md)了解如何参与。

---

## 要求

- **操作系统**：Windows 10/11
- **Python**：3.10+
- **硬件**：NVIDIA GPU及其安装驱动程序。
- **CUDA**：12.x工具包（严格要求基准测试/模拟功能）。
  - *注意：如果未检测到CUDA 12.x，GPU特定基准测试功能将禁用。*

---

## 安装

该工具支持模块化安装，以适应您的需求：

### 1. 最小（仅命令行）

适用于无显示器的服务器或后台监控。

- 命令行界面。
- 基本系统/GPU指标。

### 2. 标准（命令行+网络UI）

适用于大多数用户。

- 包含网络仪表盘。
- REST API端点。
- 实时图表。

### 3. 完整（标准+可视化）

适用于开发和压力测试。

- 包含粒子模拟。
- PyTorch/CuPy依赖基准测试。

### 快速开始

1. **下载**最新版本或克隆仓库。
2. **设置**：

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

---

## 许可证

MIT许可证。详见[LICENSE](../LICENSE)。