[PROTECTADO_BLOCO_0]

[PROTECTADO_BLOCO_1]

> *MyGPU: Uma utilidade de gerenciamento de GPU leve: um wrapper compacto para `nvidia-smi` com um dashboard web elegante.*

[PROTECTADO_BLOCO_2]
[PROTECTADO_BLOCO_3]
[PROTECTADO_BLOCO_4]
[PROTECTADO_BLOCO_5]
[PROTECTADO_BLOCO_6]

## Galeria

<details>
  <summary>Dashboard Web</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Use first image aspect ratio 1624x675 for slide frame; images fit inside using object-fit:contain -->
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

### Por que usá-lo?

- **Leveza**: Pés no chão em termos de uso de recursos.
- **Flexibilidade**: Funciona como uma ferramenta CLI ou um dashboard web completo.
- **Orientado a Administradores**: Inclui recursos como **Enforcamento de VRAM** (desligar processos que excedem limites) e **Listas de Observação**.
- **Amigável para Desenvolvedores**: Ferramentas de teste e simulação integradas (GEMM, Física de Partículas) para validar a estabilidade do sistema.

---

### Recursos

- **Monitoramento em Tempo Real**:
  - Métricas detalhadas da GPU (Utilização, VRAM, Potência, Temperatura).
  - Métricas do sistema (CPU, RAM, etc.).

- **Admin e Enforcamento**:
  - **Limites de VRAM**: Defina limites rígidos de uso de VRAM por GPU.
  - **Desligamento Automático**: Desligue automaticamente processos que violem as políticas de VRAM (apenas para administradores).
  - **Listas de Observação**: Monitore PIDs ou nomes de processos específicos.

- **Testes e Simulação**:
  - **Testes de Estresse**: Configure cargas de trabalho GEMM configuráveis para testar a sobreaquecimento e estabilidade.
  - **Simulação Visual**: Simulação interativa de física de partículas para visualizar a carga da GPU.

---

### Roadmap e Trabalho Futuro

Contribuições são bem-vindas! Os principais pontos futuros a serem abordados seriam:

- **Suporte Multi-GPU**: Melhoria no manuseio de configurações multi-cartão e topologias NVLink.
- **Containerização**: Suporte oficial para Docker para implantação fácil em ambientes de contêiner.
- **Acesso Remoto**: Integração de túnel SSH e gerenciamento remoto seguro.
- **Plataformas Cruzadas**:
  - [ ] Suporte a Linux (foco em Ubuntu/Debian).
  - [ ] Suporte a Apple Silicon para monitoramento.
- **Hardware Agnóstico**:
  - [ ] Suporte a AMD ROCm.
  - [ ] Suporte a Intel Arc.
- ~~**Documentação Multilíngue**: Suporte aos principais idiomas do GitHub.~~

Consulte [CONTRIBUTING.md](../CONTRIBUTING.md) para saber como contribuir.

---

### Requisitos

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: GPU NVIDIA com drivers instalados.
- **CUDA**: Toolkit 12.x (Requerido estritamente para recursos de teste e simulação).
  - *Observação: Se o CUDA 12.x não for detectado, os recursos de teste e simulação serão desabilitados.*

---

### Instalação

A ferramenta suporta instalação modular para atender às suas necessidades:

### 1. Mínimo (CLI Apenas)

Ideal para servidores sem cabeça ou monitoramento em segundo plano.

- Interface de linha de comando.
- Métricas básicas do sistema e da GPU.

### 2. Padrão (CLI + Dashboard Web)

Ideal para a maioria dos usuários.

- Inclui Dashboard Web.
- Pontos finais de API REST.
- Gráficos em tempo real.

### 3. Completo (Padrão + Visualização)

Ideal para desenvolvimento e testes de estresse.

- Inclui Simulação de Partículas.
- Dependências de PyTorch/CuPy para testes de benchmark.

### Início Rápido

1. **Baixe** a versão mais recente ou clone o repositório.
2. **Execute Configuração**:

  ```powershell
  .\setup.ps1
  ```

3. **Inicie**:

```powershell
# Inicie o dashboard web (Padrão/Completo)
python health_monitor.py web

# Inicie o CLI
python health_monitor.py cli
```

---

### Licença

MIT. Consulte [LICENSE](../LICENSE) para detalhes.