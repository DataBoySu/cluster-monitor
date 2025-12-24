```markdown
<div style="text-align:center; margin:18px 0;">
  <img src="monitor/api/static/logo.png" alt="MyGPU logo"/>
</div>

> *MyGPU — Ein leichtgewichtiges GPU-Verwaltungsskript: ein einfaches `nvidia-smi`-Wrapper mit einem klaren Web-Dashboard.*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-1.2.3-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galerie

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

### Warum verwenden Sie dies?

- **Leichtgewichtig**: Minimaler Ressourcenbedarf. Sie bleibt aus Ihrem Weg.
- **Flexibel**: Lauffert als CLI-Tool, als Hintergrunddienst oder als vollständiger Web-Dashboard.
- **Admin-Centric**: Inklusive Funktionen wie **VRAM-Begrenzung** (automatisches Beenden von Prozessen übersteigender Grenzen) und **Watchlisten**.
- **Entwicklerfreundlich**: Inklusive Benchmark- und Simulationstools (GEMM, Teilphysisik) zur Überprüfung der Systemstabilität.

---

## Funktionen

- **Real-time Monitoring**:
  - Details über GPU-Metriken (Verwendung, VRAM, Leistung, Temperatur).
  - System-Metriken (CPU, RAM, usw.).

- **Admin & Enforcement**:
  - **VRAM-Caps**: Festlegliche Grenzen für VRAM-Verwendung pro GPU.
  - **Auto-Termination**: Automatisches Beenden von Prozessen, die übersteigern Grenzen (Admins nur).
  - **Watchlists**: Überwachen bestimmter Prozess IDs oder Prozessnamen.

- **Benchmarking & Simulation**:
  - **Stress Testing**: Konfigurierbare GEMM-Workloads zur Überprüfung der thermischen Stoppungen und Stabilität.
  - **Visual Simulation**: Interaktive 3D Teilphysisik-Simulation zur Visualisierung der GPU-Leistung.

---

## Roadmap & Zukunftsponts

Beiträge sind herzlich willkommen! Hauptfuture Punkte, die zu übernehmen sind, sind:

- **Multi-GPU Unterstützung**: Erhöhtes Verständnis für mehr-Karte-Setups und NVLink-Topologien.
- **Containerisierung**: Offizielle Docker-Unterstützung für einfache Deployment in Containerisierten Umgebungen.
- **Remote-Zugriff**: SSH-Tunneling-Integration und sichere Remote-Management.
- **Cross-Plattform**:
  - [ ] Linux-Support (Ubuntu/Debian-Fokus).
  - [ ] macOS-Support (Apple Silicon-Verwaltung).
- **Hardware-Agnostisch**:
  - [ ] AMD ROCm-Support.
  - [ ] Intel Arc-Support.

Sie finden [CONTRIBUTING.md](CONTRIBUTING.md) für weitere Informationen.

---

## Voraussetzungen

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: NVIDIA GPU mit installierten Treiber.
- **CUDA**: Toolkit 12.x (Strittig required für Benchmarking/Simulation-Funktionen).
  - *Hinweis: Wenn CUDA 12.x nicht detektiert wird, werden GPU-specific Benchmarking-Funktionen deaktiviert.*

---

## Installation

Das Tool unterstützt modular Installation, um Ihre Bedürfnisse anzupassen:

### 1. Minimal (CLI-Only)

Best für Headless Server oder Hintergrundmonitoring.

- Kommandozeileninterface.
- Basische System/GPU-Metriken.

### 2. Standard (CLI + Web UI)

Best für die meisten Benutzer.

- Inklusive Web-Dashboard.
- REST-API-Endpunkte.
- Real-time-Platten.

### 3. Voll (Standard + Visualization)

Best für Entwicklung und Stresstestung.

- Inklusive Teilphysisik-Simulation.
- PyTorch/CuPy-Abhängigkeiten für Benchmarking.

### Schnelle Start

1. **Herunterladen** der aktuellen Version oder clonen des Repositories.
2. **Setup**:

  ```powershell
  .\setup.ps1
  ```

3. **Starten**:

```powershell
# Starte den Web-Dashboard (Standard/Full)
python health_monitor.py web

# Starte den CLI
python health_monitor.py cli
```

---

## Lizenz

MIT-Lizenz. Sie finden [LICENSE](LICENSE) für weitere Informationen.
```