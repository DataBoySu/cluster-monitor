[PROTECTADO_BLOQUE_0]

[PROTECTADO_BLOQUE_1]

> *MyGPU: Utilidad de gestión de GPU ligera: un envoltorio compacto de `nvidia-smi` con un elegante panel web.*

[PROTECTADO_BLOQUE_2]
[PROTECTADO_BLOQUE_3]
[PROTECTADO_BLOQUE_4]
[PROTECTADO_BLOQUE_5]
[PROTECTADO_BLOQUE_6]

## Galería

<details>
  <summary>Panel Web</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Utilice la primera imagen con relación de aspecto 1624x675 para el marco de diapositiva; las imágenes se ajustan automáticamente usando object-fit:contain -->
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
- **Versátil**: Funciona como herramienta de línea de comandos o como un panel web completo.
- **Orientado a la administración**: Incluye características como **restricción de VRAM** (terminación automática de procesos que superen los límites) y **listas de vigilancia**.
- **Amigable con el desarrollador**: Herramientas integradas de prueba de estrés y simulación (GEMM, Física de Partículas) para validar la estabilidad del sistema.

---

## Características

- **Monitoreo en tiempo real**:
  - Métricas detalladas de GPU (utilización, VRAM, potencia, temperatura).
  - Métricas del sistema (CPU, RAM, etc.).

- **Administración y aplicación de políticas**:
  - **Límites de VRAM**: Establezca límites duros en el uso de VRAM por GPU.
  - **Terminación automática**: Termine automáticamente los procesos que violen las políticas de VRAM (solo para administradores).
  - **Listas de vigilancia**: Monitoree procesos específicos o nombres de procesos.

- **Pruebas y simulación**:
  - **Pruebas de estrés**: Configure cargas de trabajo GEMM configurables para probar el throtting térmico y la estabilidad.
  - **Simulación visual**: Simulación interactiva de física de partículas para visualizar la carga de GPU.

---

## Roadmap y trabajo futuro

Las contribuciones son bienvenidas. Los puntos principales a cubrir serían:

- **Soporte multi-GPU**: Manejo mejorado para configuraciones multi-tarjeta y topologías NVLink.
- **Contenedorización**: Soporte oficial para Docker para un despliegue fácil en entornos contenedorizados.
- **Acceso remoto**: Integración de túneles SSH y gestión remota segura.
- **Plataforma cruzada**:
  - [ ] Soporte para Linux (foco en Ubuntu/Debian).
  - [ ] Soporte para Apple Silicon para monitoreo.
- **Independiente de hardware**:
  - [ ] Soporte para AMD ROCm.
  - [ ] Soporte para Intel Arc.
- **Documentación en múltiples idiomas**: Apoyo a los lenguajes más populares de GitHub.

Consulte [CONTRIBUTING.md](../CONTRIBUTING.md) para saber cómo involucrarse.

---

## Requisitos

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: GPU NVIDIA con controladores instalados.
- **CUDA**: Toolkit 12.x (requerido estrictamente para las características de prueba y simulación).
  - *Nota: Si CUDA 12.x no se detecta, las características de prueba y simulación se desactivarán.*

---

## Instalación

La herramienta admite una instalación modular para adaptarse a sus necesidades:

### 1. Mínimo (solo CLI)

Ideal para servidores sin cabeza o monitoreo en segundo plano.

- Interfaz de línea de comandos.
- Métricas básicas del sistema y la GPU.

### 2. Estándar (CLI + Panel web)

Ideal para la mayoría de los usuarios.

- Incluye el panel web.
- Puntos finales de API REST.
- Gráficos en tiempo real.

### 3. Completo (Estándar + Visualización)

Ideal para desarrollo y pruebas de estrés.

- Incluye simulación de partículas.
- Dependencias de PyTorch/CuPy para pruebas de rendimiento.

### Inicio rápido

1. **Descargue** la última versión o clone el repositorio.
2. **Ejecute el script de configuración**:

  ```powershell
  .\setup.ps1
  ```

3. **Inicie**:

```powershell
# Inicie el panel web (Estándar/Completo)
python health_monitor.py web

# Inicie la CLI
python health_monitor.py cli
```

---

## Licencia

Licencia MIT. Consulte [LICENSE](../LICENSE) para más detalles.