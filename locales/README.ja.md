# MyGPU: Leichte GPU-Verwaltungstool: Ein kompakter Wrapper für `nvidia-smi` mit sauberem Web-Dashboard

> *MyGPU ist ein leichtgewichtiges Tool zur Verwaltung von GPUs, das als kompakter Wrapper für `nvidia-smi` fungiert und über ein sauberes Web-Dashboard verfügt.*

![Lizenz](https://img.shields.io/badge/lizenz-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-1.2.3-blue)
![Plattform](https://img.shields.io/badge/Plattform-Windows-lightgrey)
![CUDA 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galerie

### Web-Dashboard

<details>
  <summary>Web-Dashboard</summary>
  <div style="display: flex; overflow-x: auto; gap: 10px; padding: 12px 0; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch;">
    <!-- Bilder mit 16:9-Aspektratio (1624x675) verwenden, um gleichmäßige Rahmenbreite zu gewährleisten -->
    <div style="flex: 0 0 100%; scroll-snap-align: center; aspect-ratio: 1624/675; display: flex; align-items: center; justify-content: center;">
      <img src="../monitor/api/static/web1.png" style="width: 100%; height: 100%; object-fit: contain;" />
    </div>
    <div style="flex: 0 0 100%; scroll-snap-align: center; aspect-ratio: 1624/675; display: flex; align-items: center; justify-content: center;">
      <img src="../monitor/api/static/web2.png" style="width: 100%; height: 100%; object-fit: contain;" />
    </div>
    <div style="flex: 0 0 100%; scroll-snap-align: center; aspect-ratio: 1624/675; display: flex; align-items: center; justify-content: center;">
      <img src="../monitor/api/static/web3.png" style="width: 100%; height: 100%; object-fit: contain;" />
    </div>
    <div style="flex: 0 0 100%; scroll-snap-align: center; aspect-ratio: 1624/675; display: flex; align-items: center; justify-content: center;">
      <img src="../monitor/api/static/web4.png" style="width: 100%; height: 100%; object-fit: contain;" />
    </div>
  </div>
</details>

<details>
  <summary>CLI</summary>
  <div style="display: flex; overflow-x: auto; gap: 10px; padding: 12px 0; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch;">
    <div style="flex: 0 0 100%; scroll-snap-align: center; aspect-ratio: 1624/675; display: flex; align-items: center; justify-content: center;">
      <img src="../monitor/api/static/cli1.png" style="width: 100%; height: 100%; object-fit: contain;" />
    </div>
    <!-- Weitere CLI-Bilder hier einfügen -->
  </div>
</details>

### Warum MyGPU?

- **Leichtgewichtig**: Geringer Ressourcenbedarf.
- **Flexibel**: Als CLI-Tool, Hintergrunddienst oder voll ausgestattetes Web-Dashboard einsetzbar.
- **admin-zentriert**: Enthält Funktionen wie **VRAM-Enforcement** (Automatische Beendigung von Prozessen, die die VRAM-Grenzen überschreiten) und **Watchlists**.
- **Entwicklerfreundlich**: Integrierte Benchmarking- und Stresstest-Tools (GEMM, Teilchenphysik) zur Überprüfung der Systemstabilität.

---

## Funktionen

- **Echtzeitüberwachung**:
  - Detaillierte GPU-Metriken (Nutzung, VRAM, Temperatur).
  - Systemmetriken (CPU, RAM usw.).

- **Admin- und Enforcement-Funktionen**:
  - **VRAM-Grenzen**: Festlegen von VRAM-Nutzungsgrenzen pro GPU.
  - **Automatische Beendigung**: Automatische Beendigung von Prozessen, die VRAM-Richtlinien verletzen (nur für Administratoren).
  - **Watchlists**: Überwachen spezifischer PIDs oder Prozessnamen.

- **Benchmarking und Simulation**:
  - **Stresstest**: Konfigurierbare GEMM-Lasten für die Überprüfung der thermischen Throttling und Stabilität.
  - **Visuelle Simulation**: Interaktive 3D-Teilchenphysiksimulation zur Visualisierung der GPU-Last.

---

## Roadmap und zukünftige Arbeiten

Beiträge sind willkommen! Die wichtigsten zukünftigen Punkte umfassen:

- **Multi-GPU-Unterstützung**: Verbesserte Handhabung von Multi-Card-Setups und NVLink-Topologien.
- **Containerisierung**: Offizielle Docker-Unterstützung für eine einfache Bereitstellung in Containerumgebungen.
- **Remote-Zugriff**: SSH-Tunnel-Integration und sichere Remoteverwaltung.
- **Plattformübergreifend**:
  - [ ] Linux-Unterstützung (Ubuntu/Debian-Fokus).
  - [ ] macOS-Unterstützung (Apple Silicon-Überwachung).
- **Hardware-agnostisch**:
  - [ ] AMD ROCm-Unterstützung.
  - [ ] Intel Arc-Unterstützung.
- ~~**Mehrsprachige Dokumentation**: Unterstützung der meistgenutzten GitHub-Sprachen.~~

Siehe [CONTRIBUTING.md](../CONTRIBUTING.md) für Informationen zur Mitwirkung.

---

## Anforderungen

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: NVIDIA-GPU mit installierten Treibern.
- **CUDA**: Toolkit 12.x (Streng erforderlich für Benchmarking/Simulation-Funktionen).
  - *Hinweis: Wenn CUDA 12.x nicht erkannt wird, werden GPU-spezifische Benchmarking-Funktionen deaktiviert.*

---

## Installation

Das Tool bietet verschiedene Installationsoptionen:

### 1. Minimal (CLI nur)

Am besten für Headless-Server oder Hintergrundüberwachung geeignet.

- Befehlszeileninterface.
- Grundlegende System- und GPU-Metriken.

### 2. Standard (CLI + Web-UI)

Am besten für die meisten Benutzer geeignet.

- Enthält Web-Dashboard.
- REST-API-Endpunkte.
- Echtzeitdiagramme.

### 3. Vollständig (Standard + Visualisierung)

Am besten für Entwicklung und Stresstest geeignet.

- Enthält Teilchenphysik-Simulation.
- Abhängigkeiten für PyTorch/CuPy-Benchmarking.

### Schnelle Startanleitung

1. **Herunterladen** oder Klonen des Repositories.
2. **Einrichten**:

   ```powershell
   .\setup.ps1
   ```

3. **Starten**:

```powershell
# Starten des Web-Dashboards (Standard/Vollständig)
python health_monitor.py web

# Starten der CLI
python health_monitor.py cli
```