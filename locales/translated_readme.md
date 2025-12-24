# MyGPU — Ein leichtgewichtiges GPU-Verwaltungstool: Ein kompakter Wrapper für `nvidia-smi` mit einer sauberen Web-Dashboard-Schnittstelle

![Lizenz](https://img.shields.io/badge/Lizenz-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Version](https://img.shields.io/badge/Version-1.2.3-blue)
![Plattform](https://img.shields.io/badge/Plattform-Windows-lightgrey)
![CUDA 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galerie

### Web-Dashboard

<details>
  <summary>Web-Dashboard</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Verwenden Sie das erste Bild mit einem Seitenverhältnis von 1624x675 für den Folienrahmen; die Bilder passen sich mit `object-fit: contain` innerhalb an -->
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

### CLI

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
  </div>
</details>

### Warum diese Nutzung?

- **Leichtgewichtig**: Minimaler Ressourcenbedarf.
- **Flexibel**: Als CLI-Tool, Hintergrunddienst oder voll ausgestattetes Web-Dashboard ausführbar.
- **admin-zentriert**: Enthält Funktionen wie **VRAM-Enforcement** (Automatische Beendigung von Prozessen, die Grenzwerte überschreiten) und **Watchlists**.
- **entwicklerfreundlich**: Integrierte Benchmarking- und Stresstest-Tools (GEMM, Teilchenphysik) zur Validierung der Systemstabilität.

---

## Funktionen

- **Echtzeit-Überwachung**:
  - Detaillierte GPU-Metriken (Nutzung, VRAM, Leistung, Temperatur).
  - Systemmetriken (CPU, RAM usw.).

- **Admin- und Durchsetzungsfunktionen**:
  - **VRAM-Grenzen**: Legen Sie harte Grenzen für die VRAM-Nutzung pro GPU fest.
  - **Automatische Beendigung**: Automatisch Prozesse beenden, die VRAM-Richtlinien verletzen (nur für Administratoren).
  - **Watchlists**: Überwachen Sie bestimmte PIDs oder Prozessnamen.

- **Benchmarking und Simulation**:
  - **Stresstest**: Konfigurierbare GEMM-Lasten zur Tests der thermischen Throtting und Stabilität.
  - **Visuelle Simulation**: Interaktive 3D-Teilchenphysik-Simulation zur Visualisierung der GPU-Last.

---

## Roadmap und zukünftige Arbeit

Beiträge sind willkommen! Die Hauptpunkte, die in der Zukunft abgedeckt werden sollen, sind:

- **Multi-GPU-Unterstützung**: Verbesserte Handhabung für Multi-Karten-Setups und NVLink-Topologien.
- **Containerisierung**: Offizielle Docker-Unterstützung für eine einfache Bereitstellung in Containerumgebungen.
- **Remote-Zugriff**: SSH-Tunnel-Integration und sicherer Remote-Management.
- **Plattformübergreifend**:
  - [ ] Linux-Unterstützung (Ubuntu/Debian-Fokus).
  - [ ] macOS-Unterstützung (Apple Silicon-Überwachung).
- **Hardware-agnostisch**:
  - [ ] AMD ROCm-Unterstützung.
  - [ ] Intel Arc-Unterstützung.

Siehe [CONTRIBUTING.md](../CONTRIBUTING.md) für Hinweise zum Einbringen.

---

## Anforderungen

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: NVIDIA-GPU mit installierten Treibern.
- **CUDA**: Toolkit 12.x (Streng erforderlich für Benchmarking/Simulation-Funktionen).
  - *Hinweis: Wenn CUDA 12.x nicht erkannt wird, werden GPU-spezifische Benchmarking-Funktionen deaktiviert.*

---

## Installation

Das Tool unterstützt eine modulare Installation, um Ihren Bedürfnissen gerecht zu werden:

### 1. Minimale Installation (CLI nur)

Am besten für Headless-Server oder Hintergrundüberwachung geeignet.

- Befehlszeileninterface.
- Grundlegende System-/GPU-Metriken.

### 2. Standardinstallation (CLI + Web-UI)

Am besten für die meisten Benutzer geeignet.

- Enthält Web-Dashboard.
- REST-API-Endpunkte.
- Echtzeit-Diagramme.

### 3. Vollständige Installation (Standard + Visualisierung)

Am besten für Entwicklung und Stresstest geeignet.

- Enthält Teilchenphysik-Simulation.
- Abhängigkeiten für PyTorch/CuPy-Benchmarking.

### Schnelle Einrichtung

1. **