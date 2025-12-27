<!-- HTML_BLOCK:1... -->
<div align="center">
  <a href="../README.md">🇺🇸 English</a> |
  <a href="../locales/README.de.md">🇩🇪 Deutsch</a> |
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

> *MyGPU: Ein leichtgewichtiges GPU-Verwaltungstool: ein kompakter `nvidia-smi`-Wrapper mit einer eleganten Web-Dashboard.*

## Galerie

<details>
  <summary>Web-Dashboard</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Verwenden Sie das erste Bild mit einem Seitenverhältnis von 1624x675 für den Slide-Rahmen; Bilder passen sich mithilfe von `object-fit:contain` innerhalb an. -->
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

## Warum diese Nutzung?

- **Leichtgewichtig**: Minimale Ressourcenbelastung.
- **Flexibel**: Als CLI-Tool oder als vollständiges Web-Dashboard einsetzbar.
- **Admin-zentriert**: Enthält Funktionen wie **VRAM-Enforcement** (Automatische Beendigung von Prozessen, die VRAM-Richtlinien verletzen) und **Watchlists**.
- **Entwicklerfreundlich**: Integrierte Benchmarking- und Stresstestwerkzeuge (GEMM, Teilchenphysik) zur Validierung der Systemstabilität.

---

## Funktionen

- **Echtzeitüberwachung**:
  - Detaillierte GPU-Metriken (Auslastung, VRAM, Leistung, Temperatur).
  - Systemmetriken (CPU, RAM usw.).

- **Admin- und Durchsetzungsfunktionen**:
  - **VRAM-Grenzen**: Legen Sie harte Grenzen für die VRAM-Nutzung pro GPU fest.
  - **Automatische Beendigung**: Automatisch beenden Sie Prozesse, die VRAM-Richtlinien verletzen (nur für Administratoren).
  - **Watchlists**: Überwachen Sie bestimmte PIDs oder Prozessnamen.

- **Benchmarking und Simulation**:
  - **Stresstest**: Konfigurierbare GEMM-Lastarbeiten zur Tests der thermischen Throttling und Stabilität.
  - **Visuelle Simulation**: Interaktive 3D-Teilchenphysiksimulation zur Visualisierung der GPU-Belastung.

---

## Roadmap & zukünftige Arbeiten

Beiträge sind willkommen! Die Hauptpunkte, die in Zukunft abgedeckt werden sollen, wären:

- **Multi-GPU-Unterstützung**: Verbesserte Handhabung für Multi-Karten-Einrichtungen und NVLink-Topologien.
- **Containerisierung**: Offizielle Docker-Unterstützung für eine einfache Bereitstellung in Containerumgebungen.
- **Remotezugriff**: SSH-Tunneling-Integration und sichere Remoteverwaltung.
- **Plattformübergreifend**:
  - [ ] Linux-Unterstützung (Ubuntu/Debian-Fokus).
  - [ ] macOS-Unterstützung (Apple Silicon-Überwachung).
- **Hardware-agnostisch**:
  - [ ] AMD ROCm-Unterstützung.
  - [ ] Intel Arc-Unterstützung.
- ~~**Mehrsprachige Dokumentation**: Unterstützung der beliebtesten GitHub-Sprachen.~~

Siehe [CONTRIBUTING.md](../CONTRIBUTING.md), um herauszufinden, wie du dich einbringen kannst.

---

## Anforderungen

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: NVIDIA-GPU mit installierten Treibern.
- **CUDA**: Toolkit 12.x (Streng erforderlich für Benchmarking-/Simulationsfunktionen).
  - *Hinweis: Wenn CUDA 12.x nicht erkannt wird, werden GPU-spezifische Benchmarkingfunktionen deaktiviert.*

---

## Installation

Das Tool unterstützt modulare Installationen, um Ihren Bedürfnissen gerecht zu werden:

### 1. Minimal (CLI nur)

Am besten für Headless-Server oder Hintergrundüberwachung geeignet.

- Befehlszeileninterface.
- Grundlegende System-/GPU-Metriken.

### 2. Standard (CLI + Web-UI)

Am besten für die meisten Benutzer geeignet.

- Enthält Web-Dashboard.
- REST-API-Endpunkte.
- Echtzeitdiagramme.
- Aber keine Simulation oder Benchmarking.

### 3. Vollständig (Standard + Visualisierung)

Am besten für Entwicklung und Stresstest geeignet.

- Enthält Simulation.
- Abhängigkeiten für PyTorch/CuPy für Benchmarking.

### Schnelle Startanleitung

1. **Laden** Sie die neueste Version herunter oder klonen Sie das Repository.
2. **Einrichten**:

  ```powershell
  .\setup.ps1
  ```

3. **Starten**:

```powershell
# Starten Sie das Web-Dashboard (Standard/Vollständig)
python health_monitor.py web

# Starten Sie die CLI
python health_monitor.py cli
```