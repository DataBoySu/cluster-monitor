<!-- HTML_BLOCK:1... -->

<div align="center">
  <a href="../README.md">🇺🇸 English</a> |
  <a href="../locales/README.de.md">🇩🇪 Deutsch</a> |
  <a href="../locales/README.ru.md">🇷🇺 Русский</a> |
  <a href="../locales/README.fr.md">🇫🇷 Français</a> |
  <a href="../locales/README.es.md">🇪🇸 Español</a> |
  <a href="../locales/README.ja.md">🇯🇵 日本語</a> |
  <a href="../locales/README.zh.md">🇨🇳 中文</a> |
  <a href="../locales/README.pt.md">🇵🇹 Português</a> |
  <a href="../locales/README.ko.md">🇰🇷 한국어</a> |
  <a href="../locales/README.hi.md">🇮🇳 हिंदी</a>
</div>

<!-- HTML_BLOCK:2... -->

<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU logo"/>
</div>

<!-- HTML_BLOCK:... -->

> *MyGPU：轻量级GPU管理工具：一个紧凑的`nvidia-smi`包装器，配有一个优雅的网络仪表盘。*

<!-- HTML_BLOCK: no change to url; output entire as it is... -->
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-pink)
![Version](https://img.shields.io/badge/version-1.3.0-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## 画廊

<details>

  <summary>
    网络仪表盘
  </summary>

  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- 使用第一张图片的 1624x675 宽高作为滑块框架；图片使用 `object-fit: contain` 适应框架 -->
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
  <summary>
  CLI
  </summary>
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

### 为什么使用它？

- **轻量级**：资源占用最小。
- **灵活**：可作为命令行工具或功能全面的 Web 仪表盘运行。
- **以管理员为中心的**：包含 **VRAM 强制执行**（自动杀死超出限制的进程）和 **监控列表**等功能。
- **开发人员友好**：内置基准测试和压力测试工具（GEMM、粒子物理），用于验证系统稳定性。

## 功能特性

- **实时监控**：
  - 详细的 GPU 指标（利用率、显存、功率、温度）。
  - 系统指标（CPU、内存等）。

- **管理与强制执行**：
  - **显存上限**：为每个 GPU 设置显存使用量的硬性限制。
  - **自动终止**：（仅管理员可操作）自动终止违反显存策略的进程。
  - **监控列表**：监控特定 PIDs 或进程名称。

- **基准测试与模拟**：
  - **压力测试**：可配置的 GEMM 工作负载用于测试热量限制和稳定性。
  - **可视化模拟**：交互式 3D 粒子物理模拟，用于可视化 GPU 加载。

## 路线图与未来工作

欢迎贡献！主要需要涵盖的未来工作点包括：

- **多GPU支持**：增强多卡设置和 NVLink 拓扑的处理能力。
- **容器化**：官方 Docker 支持，便于在容器化环境中部署。
- **远程访问**：集成 SSH 隧道和安全远程管理。
- **跨平台**：
  - [已完成] Linux 支持（Ubuntu/Debian 重点）。
  - [已完成] macOS 支持（Apple Silicon 监控）。
- **硬件无关**：
  - [待完成] AMD ROCm 支持。
  - [待完成] Intel Arc 支持。
- **多语言文档**（已删除）：支持 GitHub 上最受欢迎的语言。

请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解如何参与进来。

## 要求

- **操作系统**：Windows 10/11、Linux、macOS
- **Python**：3.10+
- **硬件**：NVIDIA GPU（所有平台）、Apple Silicon（macOS）或仅 CPU。
- **CUDA**：12.x 工具包（NVIDIA 平台的基准测试/模拟推荐）。
  - *注意：如果未检测到 CUDA/MPS，某些基准测试功能可能无法启用。*

## 安装

该工具支持模块化安装，以满足您的需求：

### 1. 最小化（仅命令行）

适用于无头服务器或后台监控。

- 命令行界面。
- 基本系统/GPU指标。

### 2. 标准版 (命令行界面 + Web 用户界面)

大多数用户的最佳选择。

- 包含 Web 仪表盘。
- REST API 端点。
- 实时图表。
- 但无模拟或基准测试。

### 3. 完整（标准 + 可视化）

最适合开发和压力测试。

- 包含模拟。
- PyTorch/CuPy 依赖项用于基准测试。

### 快速入门

1. **下载** 或克隆仓库。
2. **运行设置**：

   **Windows**:

```powershell
   .\setup.ps1
   ```

**Linux/macOS**:

```bash
chmod +x setup.sh
./setup.sh
```

**启动**

```bash
# 启动网络仪表盘（标准/完整）
python health_monitor.py web

# 启动命令行界面
python health_monitor.py cli
```

## 许可证

请参阅 [LICENSE](../LICENSE) 了解详细信息。

