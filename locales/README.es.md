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

> *MyGPU: Utilidad de Gestión de GPU Ligera: un envoltorio compacto de `nvidia-smi` con un elegante panel web.*

<!-- HTML_BLOCK: no change to url; output entire as it is... -->
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-pink)
![Version](https://img.shields.io/badge/version-1.2.3-green)
![Platform](https://img.shields.io/badge/platform-Windows10/11-blue)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galería

<details>

  <summary>
  Tablero Web
  </summary>

  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Utilizar la primera imagen con relación de aspecto 1624x675 para el marco de diapositiva; las imágenes se ajustan dentro usando object-fit:contain -->
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

### ¿Por qué usar esto?

- **Ligero**: Huella de recursos mínima.
- **Versátil**: Se ejecuta como una herramienta de línea de comandos (CLI) o un panel web completo.
- **Centrado en la administración**: Incluye características como **aplicación de límites de VRAM** (detención automática de procesos que superen los límites) y **listas de vigilancia**.
- **Amigable para desarrolladores**: Herramientas integradas de benchmarking y pruebas de estrés (GEMM, Física de Partículas) para validar la estabilidad del sistema.

## Características

- **Monitoreo en tiempo real**:
  - Métricas detalladas de GPU (Utilización, VRAM, Potencia, Temperatura).
  - Métricas del sistema (CPU, RAM, etc.).

- **Administración y aplicación de políticas**:
  - **Límites de VRAM**: Establecer límites rígidos en el uso de VRAM por GPU.
  - **Terminación automática**: Terminar automáticamente procesos que violen las políticas de VRAM (solo para administradores).
  - **Listas de vigilancia**: Monitorear PIDs específicos o nombres de procesos.

- **Benchmarking y simulación**:
  - **Pruebas de estrés**: Cargas de trabajo configurables de GEMM para probar el sobrecalentamiento y la estabilidad.
  - **Simulación visual**: Simulación interactiva de física de partículas en 3D para visualizar la carga de trabajo de la GPU.

## Mapa de Ruta y Trabajo Futuro

¡Las contribuciones son bienvenidas! Los puntos futuros principales a cubrir serían:

- **Soporte Multi-GPU**: Manejo mejorado para configuraciones de múltiples tarjetas y topologías NVLink.
- **Contenedorización**: Soporte oficial para Docker para una fácil implementación en entornos contenedorizados.
- **Acceso Remoto**: Integración de túneles SSH y gestión remota segura.
- **Plataformas Cruzadas**:

  - [ ] Soporte para Linux (foco en Ubuntu/Debian).
  - [ ] Soporte para macOS (monitoreo de Apple Silicon).

- **Agnóstico de Hardware**:

  - [ ] Soporte para AMD ROCm.
  - [ ] Soporte para Intel Arc.

- ~~**Documentación Multi-Idioma**: Apoyo a la mayoría de los lenguajes populares de GitHub.~~

Consulte [CONTRIBUTING.md](../CONTRIBUTING.md) para saber cómo involucrarse.

## Requisitos

- **Sistema Operativo**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: Tarjeta gráfica NVIDIA con controladores instalados.
- **CUDA**: Toolkit 12.x (Requerido estrictamente para las características de Benchmarking/Simulación).
  - *Nota: Si no se detecta CUDA 12.x, se desactivarán las características de benchmarking específicas de la GPU.*

## Instalación

La herramienta admite una instalación modular para adaptarse a tus necesidades:

### 1. Mínimo (solo CLI)

Ideal para servidores sin interfaz gráfica o para monitoreo en segundo plano.

- Interfaz de línea de comandos.
- Métricas básicas de sistema/GPU.

### 2. Estándar (CLI + Interfaz Web)

Ideal para la mayoría de los usuarios.

- Incluye Tablero Web.
- Puntos finales de API REST.
- Gráficos en tiempo real.
- Pero sin Simulación ni Benchmarking.

### 3. Completa (Estándar + Visualización)

Ideal para desarrollo y pruebas de estrés.

- Incluye Simulación.
- Dependencias PyTorch/CuPy para benchmarking.

### Inicio Rápido

1. **Descargar** la última versión o clonar el repositorio.
2. **Ejecutar Configuración**:

```powershell
  .\setup.ps1
  ```

3. **Lanzamiento**:

```powershell
# Iniciar el panel web (Estándar/Completo)
python health_monitor.py web

# Iniciar la interfaz de línea de comandos (CLI)
python health_monitor.py cli
```

## Licencia

Consulte [LICENSE](../LICENSE) para más detalles.

