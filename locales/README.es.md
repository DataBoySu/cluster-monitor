# MyGPU: Herramienta de gestión de GPU ligera: un envoltorio compacto de `nvidia-smi` con un elegante tablero web.

![Licencia](https://img.shields.io/badge/licencia-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Versión](https://img.shields.io/badge/versión-1.2.3-blue)
![Plataforma](https://img.shields.io/badge/plataforma-Windows-lightgrey)
![CUDA 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galería

<details>
  <summary>Tablero web</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Utilizar la primera imagen con relación de aspecto 1624x675 para el marco de diapositiva; las imágenes se ajustan automáticamente con `object-fit: contain` -->
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

### ¿Por qué usar esto?

- **Ligero**: Pie de contacto mínimo con los recursos.
- **Flexible**: Funciona como una herramienta de línea de comandos o un tablero web completo.
- **Orientado a la administración**: Incluye características como **límites de VRAM** (terminación automática de procesos que superen los límites) y **listas de vigilancia**.
- **Amigable con el desarrollador**: Herramientas integradas de prueba y simulación (GEMM, Física de partículas) para validar la estabilidad del sistema.

---

## Características

- **Monitoreo en tiempo real**:
  - Métricas detalladas de GPU (Utilización, VRAM, Potencia, Temperatura).
  - Métricas del sistema (CPU, RAM, etc.).

- **Administración y aplicación de políticas**:
  - **Límites de VRAM**: Establecer límites duros en el uso de VRAM por GPU.
  - **Terminación automática**: Terminar automáticamente los procesos que violen las políticas de VRAM (solo para administradores).
  - **Listas de vigilancia**: Monitorear PIDs o nombres de procesos específicos.

- **Pruebas y simulación**:
  - **Pruebas de estrés**: Cargas de trabajo GEMM configurables para probar el throtting térmico y la estabilidad.
  - **Simulación visual**: Simulación interactiva de física de partículas para visualizar la carga de GPU.

---

## Roadmap y trabajo futuro

¡Las contribuciones son bienvenidas! Los puntos principales a cubrir serían:

- **Soporte multi-GPU**: Manejo mejorado para configuraciones multi-tarjeta y topologías NVLink.
- **Contenedorización**: Soporte oficial para Docker para un despliegue fácil en entornos contenedorizados.
- **Acceso remoto**: Integración de túneles SSH y gestión remota segura.
- **Plataforma cruzada**:
  - [ ] Soporte para Ubuntu/Debian (enfocado en la gestión de hardware).
  - [ ] Soporte para Apple Silicon (monitoreo).
- **Independencia de hardware**:
  - [ ] Soporte para AMD ROCm.
  - [ ] Soporte para Intel Arc.
- ~~**Documentación multilingüe**: Apoyo a los lenguajes más populares de GitHub.~~

Consulte [CONTRIBUTING.md](../CONTRIBUTING.md) para saber cómo involucrarse.

---

## Requisitos

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: GPU NVIDIA con controladores instalados.
- **CUDA**: Toolkit 12.x (Requerido estrictamente para las características de prueba y simulación).
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
- Dependencias de PyTorch/CuPy para pruebas.

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