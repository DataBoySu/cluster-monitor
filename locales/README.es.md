<!-- HTML_BLOCK:1... -->
<div align="center">
  <a href="../README.md">🇺🇸 Inglés</a> |
  <a href="../locales/README.de.md">🇩🇪 Alemán</a> |
  <a href="../locales/README.fr.md">🇫🇷 Francés</a> |
  <a href="../locales/README.es.md">🇪🇸 Español</a> |
  <a href="../locales/README.ja.md">🇯🇵 Japonés</a> |
  <a href="../locales/README.zh.md">🇨🇳 Chino</a> |
  <a href="../locales/README.pt.md">🇵🇹 Portugués</a> |
  <a href="../locales/README.ko.md">🇰🇷 Coreano</a> |
  <a href="../locales/README.hi.md">🇮🇳 Hindi</a>
</div>
<!-- HTML_BLOCK:2... -->
<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU logo"/>
</div>
<!-- HTML_BLOCK:... -->

> *MyGPU: Utilidad de gestión de GPU ligera: un envoltorio compacto para `nvidia-smi` con un elegante tablero web.*

![Licencia](https://img.shields.io/badge/licencia-MIT-azul.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-azul)
![Versión](https://img.shields.io/badge/versión-1.2.3-azul)
![Plataforma](https://img.shields.io/badge/plataforma-Windows-gris)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galería

<details>
  <summary>Tablero web</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Utilizar la relación de aspecto 1624x675 para el marco de la diapositiva; las imágenes se ajustan automáticamente con object-fit:contain -->
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

### ¿Por qué usar esto?

- **Ligero**: Pie de planta con un uso mínimo de recursos.
- **Versátil**: Funciona como una herramienta CLI o un tablero web completo.
- **Orientado a la administración**: Incluye características como **límites de VRAM** (auto-cierre de procesos que superen los límites) y **listas de vigilancia**.
- **Amigable con el desarrollador**: Herramientas integradas para probar la estabilidad del sistema (GEMM, física de partículas).

---

## Características

- **Monitoreo en tiempo real**:
  - Métricas detalladas de GPU (utilización, VRAM, potencia, temperatura).
  - Métricas del sistema (CPU, RAM, etc.).

- **Administración y aplicación de políticas**:
  - **Límites de VRAM**: Establezca límites duros en el uso de VRAM por GPU.
  - **Cierre automático**: Automatice el cierre de procesos que violen las políticas de VRAM (solo para administradores).
  - **Listas de vigilancia**: Monitoree PIDs o nombres de procesos específicos.

- **Simulación y pruebas de estrés**:
  - **Pruebas de estrés**: Configure cargas de trabajo GEMM configurables para probar el rendimiento térmico y la estabilidad.
  - **Simulación visual**: Simulación interactiva de física de partículas 3D para visualizar la carga de GPU.

---

## Plan de desarrollo

Las contribuciones son bienvenidas. Los puntos futuros a cubrir serían:

- **Soporte multi-GPU**: Manejo mejorado para configuraciones multi-tarjeta y topologías NVLink.
- **Contenedorización**: Soporte oficial para Docker para una fácil implementación en entornos contenedorizados.
- **Acceso remoto**: Integración de túneles SSH y gestión segura remota.
- **Plataforma cruzada**:
  - [ ] Soporte para macOS (enfocado en la monitorización de Apple Silicon).
  - [ ] Soporte para AMD ROCm.
  - [ ] Soporte para Intel Arc.
- ~~**Documentación multilingüe**: Apoyo a los lenguajes más populares de GitHub.~~

Consulte [CONTRIBUTING.md](../CONTRIBUTING.md) para saber cómo involucrarse.

---

## Requisitos

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: GPU NVIDIA con controladores instalados.
- **CUDA**: Versión 12.x (requerida estrictamente para las características de simulación y benchmarking).
  - *Nota: Si CUDA 12.x no se detecta, las características de benchmarking se desactivarán.*

---

## Instalación

La herramienta admite una instalación modular para adaptarse a sus necesidades:

### 1. Mínimo (solo CLI)

Ideal para servidores sin cabeza o monitoreo en segundo plano.

- Interfaz de línea de comandos.
- Métricas básicas del sistema y la GPU.

### 2. Estándar (CLI + Tablero web)

Ideal para la mayoría de los usuarios.

- Incluye el tablero web.
- Puntos finales de API REST.
- Gráficos en tiempo real.
- Pero sin simulación ni benchmarking.

### 3. Completo (Estándar + Visualización)

Ideal para desarrollo y pruebas de estrés.

- Incluye la simulación.
- Dependencias de PyTorch/CuPy para las características de benchmarking.

### Inicio rápido

1. **Descargar** la última versión o clonar el repositorio.
2. **Ejecutar configuración**:

  ```powershell
  .\setup.ps1
  ```

3. **Iniciar**:

```powershell
# Iniciar el tablero web (Estándar/Completo)
python health_monitor.py web

# Iniciar CLI
python health_monitor.py cli
```