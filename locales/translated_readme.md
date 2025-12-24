<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU Logo"/>
</div>

> *MyGPU — Leichtgewichtige GPU-Verwaltung: ein kompakter Wrapper um `nvidia-smi` mit einem sauberen Web-Dashboard.*

![Lizenz](https://img.shields.io/badge/license-MIT-blue.svg)  
![Python](https://img.shields.io/badge/python-3.10%2B-blue)  
![Version](https://img.shields.io/badge/version-1.2.3-blue)  
![Plattform](https://img.shields.io/badge/platform-Windows-lightgrey)  
![CUDA 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galerie

<details>
  <summary>Web-Dashboard</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Verwende den ersten Bildaspektverhältnis 1624x675 für die Slide-Frame; Bilder passen sich an mit object-fit:contain -->
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

### Warum verwenden Sie dieses Tool?

- **Leichtgewichtig**: Minimaler Ressourcenverbrauch. Es stört nicht.
- **Flexibel**: Kann als CLI-Tool, als Hintergrunddienst oder als vollständiges Web-Dashboard verwendet werden.
- **Admin-orientiert**: Umfasst Funktionen wie **VRAM-Enforcement** (Automatische Beendigung von Prozessen, die Grenzwerte überschreiten) und **Watchlisten**.
- **Entwicklerfreundlich**: Integrierte Benchmarking- und Stress-Tests (GEMM, Teilchenphysik) zur Validierung der Systemstabilität.

---

## Funktionen

- **Echtzeitüberwachung**:
  - Ausführliche GPU-Metriken (Ausnutzung, VRAM, Leistung, Temperatur).
  - Systemmetriken (CPU, RAM usw.).

- **Admin- und Kontrollfunktionen**:
  - **VRAM-Begrenzung**: Festlegung harte Grenzen für die VRAM-Nutzung pro GPU.
  - **Automatische Beendigung**: Automatische Beendigung von Prozessen, die VRAM-Richtlinien verletzen (nur für Admin).
  - **Watchlisten**: Überwachung bestimmter PIDs oder Prozessnamen.

- **Benchmarking und Simulation**:
  - **Stress-Testing**: Konfigurierbare GEMM-Aufgaben zur Prüfung von thermischer Drosselung und Stabilität.
  - **Visuelle Simulation**: Interaktive 3D-Teilchenphysik-Simulation zur Visualisierung der GPU-Last.

---

## Roadmap und zukünftige Entwicklungen

Beiträge sind willkommen! Die wichtigsten zukünftigen Entwicklungen sind:

- **Multi-GPU-Unterstützung**: Verbesserte Behandlung von Multi-Karten-Setups und NVLink-Topologien.
- **Containerisierung**: Offizielle Docker-Unterstützung für einfache Bereitstellung in containerisierten Umgebungen.
- **Fernzugriff**: Integration von SSH-Tunneln und sichere Fernverwaltung.
- **Krossplattform**:
  - [ ] Linux-Unterstützung (Ubuntu/Debian-Fokus).
  - [ ] macOS-Unterstützung (Apple Silicon-Überwachung).
- **Hardware-ungesetzte Unterstützung**:
  - [ ] AMD ROCm-Unterstützung.
  - [ ] Intel Arc-Unterstützung.

Weitere Informationen zur Beteiligung finden Sie in [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Anforderungen

- **Betriebssystem**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: NVIDIA-GPU mit installierten Treibern.
- **CUDA**: Toolkit 12.x (für Benchmarking- und Simulationselemente **strikt erforderlich**).
  - *Hinweis: Wenn CUDA 12.x nicht erkannt wird, werden GPU-spezifische Benchmark-Funktionen deaktiviert.*

---

## Installation

Das Tool unterstützt eine modulare Installation, um Ihren Bedarf zu erfüllen:

### 1. Minimal (nur CLI)

Optimal für headless-Server oder Hintergrundüberwachung.

- Befehlszeilenschnittstelle.
- Grundlegende System- und GPU-Metriken.

### 2. Standard (CLI + Web-UI)

Optimal für die meisten Benutzer.

- Enthält Web-Dashboard.
- REST-API-Endpunkte.
- Echtzeit-Karten.

### 3. Vollständig (Standard + Visualisierung)

Optimal für Entwicklung und Stress-Tests.

- Enthält Teilchen-Simulation.
- Abhängigkeiten von PyTorch/CuPy für Benchmarking.

### Schnellstart

1. **Herunterladen** der neuesten Version oder Klonen des Repositories.
2. **Setup ausführen**:

  ```powershell
  .\setup.ps1
  ```

3. **Starten**:

```powershell
# Starte das Web-Dashboard (Standard oder Vollständig)
python health_monitor.py web

# Starte die CLI
python health_monitor.py cli
```

---

## Lizenz

MIT-Lizenz. Weitere Details finden Sie in [LICENSE](../LICENSE).