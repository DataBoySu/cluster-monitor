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

> *MyGPU: Ein leichtgewichtiges GPU-Verwaltungstool: ein kompakter Wrapper für `nvidia-smi` mit einem eleganten Web-Dashboard.*

<!-- HTML_BLOCK: no change to url; output entire as it is... -->
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-pink)
![Version](https://img.shields.io/badge/version-1.3.0-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galerie

<details>

  <summary>
  Web-Dashboard
  </summary>

  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Verwende das erste Bild mit der Seitenverhältnis 1624x675 als Rahmen für die Folie; Bilder passen sich mit object-fit:contain innerhalb an -->
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

### Warum dies nutzen?

- **Leichtgewichtig**: Minimale Ressourcenanforderungen.
- **Flexibel**: Als CLI-Tool oder als umfassendes Web-Dashboard ausführbar.
- **admin-zentriert**: Enthält Funktionen wie **VRAM-Erzwingung** (Automatische Beendigung von Prozessen, die die Grenzen überschreiten) und **Watchlists**.
- **Entwicklerfreundlich**: Integrierte Leistungsanalyse- und Stress-Test-Tools (GEMM, Teilchenphysik), um die Systemstabilität zu validieren.

## Funktionen

- **Echtzeitüberwachung**:
  - Detaillierte GPU-Metriken (Nutzung, VRAM, Stromverbrauch, Temperatur).
  - Systemmetriken (CPU, RAM usw.).

- **Verwaltung und Durchsetzung**:
  - **VRAM-Begrenzungen**: Setze harte Obergrenzen für den VRAM-Verbrauch pro GPU.
  - **Automatische Beendigung**: Automatisch Prozesse beenden, die VRAM-Richtlinien verletzen (nur für Administratoren).
  - **Watchlisten**: Überwache spezifische PIDs oder Prozessnamen.

- **Leistungsanalyse und Simulation**:
  - **Belastungstests**: Konfigurierbare GEMM-Lasten, um thermische Drosselung und Stabilität zu testen.
  - **Visuelle Simulation**: Interaktive 3D-Teilchenphysik-Simulation zur Visualisierung der GPU-Belastung.

## Roadmap & Zukunftsplanung

Beiträge sind willkommen! Die Hauptpunkte, die in Zukunft angegangen werden sollen, sind:

- **Mehrfach-GPU-Unterstützung**: Verbesserte Handhabung von Mehrkarten-Einrichtungen und NVLink-Topologien.
- **Containerisierung**: Offizielle Docker-Unterstützung für einfache Bereitstellung in Container-Umgebungen.
- **Remote-Zugriff**: Integration von SSH-Tunneln und sicherer Fernverwaltung.
- **Plattformübergreifend**:
  - [x] Linux-Unterstützung (Ubuntu/Debian-Fokus).
  - [x] macOS-Unterstützung (Apple Silicon-Überwachung).
- **Hardwareunabhängig**:
  - [ ] AMD ROCm-Unterstützung.
  - [ ] Intel Arc-Unterstützung.
- ~~**Mehrsprachige Dokumentation**: Unterstützung der beliebtesten GitHub-Sprachen.~~

Siehe [CONTRIBUTING.md](../CONTRIBUTING.md) für Informationen, wie du dich einbringen kannst.

## Anforderungen

- **Betriebssysteme**: Windows 10/11, Linux, macOS
- **Python**: 3.10+
- **Hardware**: NVIDIA-GPU (alle Plattformen), Apple Silicon (macOS) oder CPU-nur.
- **CUDA**: Toolkit 12.x (Empfohlen für Benchmarking/Simulation auf NVIDIA).
  - *Hinweis: Wenn CUDA/MPS nicht erkannt wird, können einige Benchmark-Funktionen deaktiviert sein.*

## Installation

Das Tool unterstützt eine modulare Installation, um deinen Anforderungen gerecht zu werden:

### 1. Minimal (CLI Nur)

Ideal für Headless-Server oder Hintergrundüberwachung.

- Befehlszeileninterface.
- Grundlegende System- und GPU-Metriken.

### 2. Standard (CLI + Web-Benutzeroberfläche)

Am besten für die meisten Benutzer geeignet.

- Enthält Web-Dashboard.
- REST-API-Endpunkte.
- Echtzeit-Diagramme.
- Ohne Simulation oder Benchmark-Tests.

### 3. Vollständig (Standard + Visualisierung)

Am besten für Entwicklung und Stresstests geeignet.

- Enthält Simulation.
- PyTorch/CuPy-Abhängigkeiten für Leistungsanalysen.

### Schnelle Einführung

1. **Repository herunterladen** oder klonen.
2. **Einrichten** ausführen:

   **Windows**: Führe das Einrichtungsskript aus.

```powershell
   .\setup.ps1
   ```

**Linux/macOS:**

```bash
Berechtige die Datei: `chmod +x setup.sh`
Führe die Installation aus: `./setup.sh`
```

**Starten**:

```bash
# Starten Sie die Web-Benutzeroberfläche (Standard/Voll)
python health_monitor.py web

# Starten Sie die CLI-Schnittstelle
python health_monitor.py cli
```

## Lizenz

Siehe [LICENSE](../LICENSE) für Details.

