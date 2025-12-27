<!-- HTML_BLOCK:1... -->
<div align="center">
  <a href="../README.md">🇺🇸 英语</a> |
  <a href="../locales/README.de.md">🇩🇪 德语</a> |
  <a href="../locales/README.fr.md">🇫🇷 法语</a> |
  <a href="../locales/README.es.md">🇪🇸 西班牙语</a> |
  <a href="../locales/README.ja.md">🇯🇵 日语</a> |
  <a href="../locales/README.zh.md">🇨🇳 中文</a> |
  <a href="../locales/README.pt.md">🇵🇹 葡萄牙语</a> |
  <a href="../locales/README.ko.md">🇰🇷 韩语</a> |
  <a href="../locales/README.hi.md">🇮🇳 印地语</a>
</div>
<!-- HTML_BLOCK:2... -->
<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU logo"/>
</div>
<!-- HTML_BLOCK:... -->

> *MyGPU: 轻量级 GPU 管理工具：一个紧凑的 `nvidia-smi` 包装器，配有优雅的网络仪表板。*

## 画廊

<details>
  <summary>网络仪表板</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- 使用第一张图片的宽高比 1624x675 为幻灯片框架；使用 `object-fit:contain` 使图片在内部填充 -->
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
- **灵活**：作为命令行工具、网络仪表板或全功能 Web 仪表板运行。
- **管理员友好**：包括 VRAM 限制（自动终止超出限制的进程）和监控列表等功能。
- **开发人员友好**：内置用于验证系统稳定性的基准测试和粒子物理模拟。

---

## 功能

- **实时监控**：
  - GPU 和系统指标（利用率、VRAM、功耗、温度）。
  - 系统指标（CPU、内存等）。

- **管理与执行**：
  - **VRAM限制**：为每个 GPU 设置 VRAM 使用量上限。
  - **自动终止**（仅管理员权限）：如果检测到超出 VRAM 限制的进程，则自动终止该进程。
  - **监控列表**：监控特定 PID 或过程名称。

- **基准测试与模拟**：
  - **压力测试**：配置可配置的 GEMM 工作负载以测试系统稳定性。
  - **粒子物理模拟**：交互式 3D 粒子物理模拟，用于可视化 GPU 加载。

---

## 路线图和未来工作

欢迎贡献！主要未来要点包括：

- **多 GPU 支持**：增强对单卡和 NVLink 拓扑的处理能力。
- **容器化**：官方 Docker 支持，方便在容器环境中部署。
- **远程访问**：SSH 隧道集成和安全远程管理。
- **跨平台**：
  - [ ] Linux 支持（Ubuntu/Debian 重点）。
  - [ ] macOS 支持（Apple Silicon 监控）。
- **硬件无缝集成**：
  - [ ] AMD ROCm 支持。
  - [ ] Intel Arc 支持。
- ~~**多语言文档**：支持 GitHub 上最受欢迎的语言。~~

查看 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解如何参与。

---

## 要求

- **操作系统**：Windows 10/11
- **Python**：3.10+
- **硬件**：NVIDIA GPU，并安装驱动程序。
- **CUDA**：12.x（用于基准测试和模拟功能）。
  - *注意：如果未检测到 CUDA 12.x，则 GPU 特定基准功能将被禁用*。

---

## 安装

工具支持模块化安装以适应您的需求：

### 1. 最小（仅命令行界面）

适合无头服务器或后台监控。

- 命令行界面。
- 基本系统和 GPU 指标。

### 2. 标准（命令行 + Web UI）

适合大多数用户。

- 包括网络仪表板。
- REST API 端点。
- 实时图表。
- 无模拟或基准测试功能。

### 3. 完整（标准 + 可视化）

适合开发和压力测试。

- 包括模拟。
- PyTorch/CuPy 依赖用于基准测试。

---

## 许可证

MIT 许可证。请参阅 [LICENSE](../LICENSE) 了解详细信息。