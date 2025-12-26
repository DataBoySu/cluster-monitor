# MyGPU: Utilidad de Gestión de GPU Ligera

*"MyGPU: Utilidad de Gestión de GPU Ligera: un envoltorio compacto de `nvidia-smi` con un elegante tablero web."*

## Galería

<details>
  <summary>Tablero Web</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Utiliza la primera imagen con relación de aspecto 1624x675 para el marco de diapositivas; las imágenes se ajustan automáticamente con object-fit:contain -->
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

## ¿Por qué usar esto?

- **Ligero**: Pie de contacto mínimo.
- **Versátil**: Funciona como una herramienta de línea de comandos o un tablero web completo.
- **Orientado a administradores**: Incluye características como **límites de VRAM** (terminación automática de procesos que superen los límites) y **listas de vigilancia**.
- **Amigable con los desarrolladores**: Herramientas integradas de prueba y simulación (GEMM, Física de Partículas) para validar la estabilidad del sistema.

---

## Características

- **Monitoreo en tiempo real**:
  - Métricas detalladas de GPU (utilización, VRAM, potencia, temperatura).
  - Métricas del sistema (CPU, RAM, etc.).

- **Administración y aplicación de políticas**:
  - **Límites de VRAM**: Establezca límites duros en el uso de VRAM por GPU.
  - **Terminación automática**: Termine automáticamente los procesos que violen las políticas de VRAM (solo para administradores).
  - **Listas de vigilancia**: Monitoree PIDs o nombres de procesos específicos.

- **Pruebas y simulación**:
  - **Pruebas de estrés**: Configure cargas de trabajo GEMM configurables para probar el throtting térmico y la estabilidad.
  - **Simulación visual**: Simulación interactiva de física de partículas para visualizar la carga de GPU.

---

## Roadmap y trabajo futuro

¡Las contribuciones son bienvenidas! Los futuros puntos principales a cubrir serían:

- **Soporte multi-GPU**: Manejo mejorado para configuraciones multi-tarjeta y topologías NVLink.
- **Contenedorización**: Soporte oficial de Docker para un despliegue fácil en entornos contenedorizados.
- **Acceso remoto**: Integración de túneles SSH y gestión remota segura.
- **Plataforma cruzada**:
  - [ ] Soporte para Ubuntu/Debian (foco en Linux).
  - [ ] Soporte para Apple Silicon (monitoreo de hardware).
- **Independiente de hardware**:
  - [ ] Soporte para AMD ROCm.
  - [ ] Soporte para Intel Arc.
- ~~**Documentación multilingüe**: Apoyo a los lenguajes de GitHub más populares.~~

Consulte [CONTRIBUTING.md](../CONTRIBUTING.md) para saber cómo involucrarse.

---

## Requisitos

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: GPU NVIDIA con controladores instalados.
- **CUDA**: Toolkit 12.x (Requerido estrictamente para características de prueba y simulación).
  - *Nota: Si CUDA 12.x no se detecta, las características de prueba y simulación se desactivarán.*

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
- Pero sin simulación ni pruebas.

### 3. Completo (Estándar + Visualización)

Ideal para desarrollo y pruebas de estrés.

- Incluye simulación.
- Dependencias de PyTorch/CuPy para pruebas de rendimiento.

### Inicio rápido

1. **Descargue** la última versión o clone el repositorio.
2. **Ejecute el script de configuración**:

  ```powershell
  .\setup.ps1
  ```

3. **Inicie**:

```powershell
# Inicie el tablero web (Estándar/Completo)
python health_monitor.py web

# Inicie la CLI
python health_monitor.py cli
```