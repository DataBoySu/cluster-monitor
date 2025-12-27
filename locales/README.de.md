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

> *MyGPU: Ein leichtgewichtiges GPU-Verwaltungstool: ein kompakter `nvidia-smi`-Wrapper mit einer eleganten Web-Dashboard-Schnittstelle.*

## Galerie

<details>

  <summary>
  Web-Dashboard
  </summary>

  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Verwenden Sie das erste Bild mit einem Seitenverhältnis von 1624x675 für den Slide-Rahmen; Bilder passen sich mit object-fit:contain innerhalb an -->
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
  </div>
</details>

### Warum diese Nutzung?

- **Leichtgewichtig**: Minimale Ressourcenbelastung.
- **Flexibel**: Als CLI-Tool, oder als vollständige Web-Dashboard-Schnittstelle verfügbar.
- **Admin-zentriert**: Enthält Funktionen wie **VRAM-Enforcement** (Automatische Beendigung von Prozessen, die VRAM-Richtlinien verletzen) und **Watchlists**.
- **Entwicklerfreundlich**: Integrierte Benchmarking- und Stresstest-Tools (GEMM, Teilchenphysik) zur Validierung der Systemstabilität.

---

### Warum MyGPU?

- **Echtzeit-Überwachung**:
  - Detaillierte GPU-Metriken (Nutzung, VRAM, Temperatur).
  - Systemmetriken (CPU, RAM, usw.).

- **Admin- und Durchsetzungsfunktionen**:
  - **VRAM-Limits**: Legen Sie harte Grenzen für die VRAM-Nutzung pro GPU fest.
  - **Automatische Beendigung**: Automatisch beenden Sie Prozesse, die VRAM-Richtlinien verletzen (nur für Administratoren).
  - **Watchlists**: Überwachen Sie spezifische PIDs oder Prozessnamen.

- **Benchmarking & Simulation**:
  - **Stresstest**: Konfigurierbare GEMM-Lasten zum Testen der thermischen Throttling und Stabilität.
  - **Visuelle Simulation**: Interaktive 3D-Teilchenphysik-Simulation zur Visualisierung der GPU-Last.

---

## Roadmap & zukünftige Arbeiten

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
- ~~**Mehrsprachige Dokumentation**: Unterstützung der beliebtesten GitHub-Sprachen.~~

Siehe [CONTRIBUTING.md](../CONTRIBUTING.md), um herauszufinden, wie du dich einbringen kannst.

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

### 1. Minimale Installation (nur CLI)

Am besten für Headless-Server oder Hintergrundüberwachung geeignet.

- Befehlszeileninterface.
- Grundlegende System-/GPU-Metriken.

### 2. Standardinstallation (CLI + Web-UI)

Am besten für die meisten Benutzer geeignet.

- Enthält Web-Dashboard.
- REST-API-Endpunkte.
- Echtzeit-Diagramme.
- Aber keine Simulation oder Benchmarking.

### 3. Vollständige Installation (Standard + Visualisierung)

Am besten für Entwicklung und Stresstest geeignet.

- Enthält Simulation.
- Abhängigkeiten für PyTorch/CuPy für Benchmarking.

### Schnelle Startanleitung

1. **Laden** Sie die neueste Version herunter oder klonen Sie das Repository.
2. **Führen Sie die Setup-Skript aus**:

  ```powershell
  .\setup.ps1
  ```

3. **Starten** Sie:

```powershell
# Starten Sie das Web-Dashboard (Standard/Vollständig)
python health_monitor.py web

# Starten Sie die CLI
python health_monitor.py cli
```

---

## Lizenz

MIT-Lizenz. Siehe [LICENSE](../LICENSE) für Details.