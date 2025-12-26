# MyGPU: Utilitário de Gerenciamento de GPU Leve: Um Wrapper Compacto para `nvidia-smi` com um Dashboard Web Elegante

> *MyGPU: Um utilitário de gerenciamento de GPU leve, com um wrapper compacto para `nvidia-smi` e um dashboard web elegante.*

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
  </div>

</details>

## Por que usar o MyGPU?

- **Leveza**: Pés no chão em termos de uso de recursos.
- **Flexibilidade**: Funciona como uma ferramenta CLI ou um dashboard web completo.
- **Orientado a Administradores**: Inclui recursos como **limites de VRAM** (auto-encerramento de processos que excedem as políticas) e **listas de observação**.
- **Amigável para Desenvolvedores**: Inclui ferramentas de teste de desempenho (GEMM, Física de Partículas) para validar a estabilidade do sistema.

---

## Recursos

- **Monitoramento em Tempo Real**:
  - Métricas detalhadas da GPU (Utilização, VRAM, Potência, Temperatura).
  - Métricas do sistema (CPU, RAM, etc.).

- **Admin e Aplicação de Políticas**:
  - **Limites de VRAM**: Defina limites rígidos de uso de VRAM por GPU.
  - **Encerramento Automático**: Termine automaticamente processos que violem as políticas de VRAM (apenas para administradores).
  - **Listas de Observação**: Monitore PIDs ou nomes de processos específicos.

- **Testes e Simulação**:
  - **Testes de Estresse**: Configure cargas de trabalho GEMM configuráveis para testar a capacidade de resfriamento térmico e estabilidade.
  - **Simulação Visual**: Simulação interativa de física de partículas para visualizar a carga de trabalho da GPU.

---

## Roadmap e Trabalho Futuro

Contribuições são bem-vindas! Os principais pontos futuros a serem abordados seriam:

- **Suporte Multi-GPU**: Melhor suporte para configurações multi-card e topologias NVLink.
- **Containerização**: Suporte oficial para Docker para implantação fácil em ambientes contêinerizados.
- **Acesso Remoto**: Integração de túnel SSH e gerenciamento remoto seguro.
- **Plataformas Cruzadas**:
  - [ ] Suporte para Linux (foco em Ubuntu/Debian).
  - [ ] Suporte para Apple Silicon (monitoramento).
- **Hardware Agnóstico**:
  - [ ] Suporte para AMD ROCm.
  - [ ] Suporte para Intel Arc.
- ~~**Documentação Multilíngue**: Suporte para as principais linguagens do GitHub.~~

Veja [CONTRIBUTING.md](../CONTRIBUTING.md) para saber como contribuir.

---

## Requisitos

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: GPU NVIDIA com drivers instalados.
- **CUDA**: Versão 12.x (estritamente necessária para recursos de teste de desempenho/simulação).
  - *Observação: Se a CUDA 12.x não for detectada, os recursos de teste de desempenho serão desabilitados.*

---

## Instalação

O utilitário oferece opções de instalação modular para atender às suas necessidades:

### 1. Instalação Mínima (CLI apenas)

Ideal para servidores sem cabeça ou monitoramento em segundo plano.

- Interface de linha de comando.
- Monitoramento básico do sistema e da GPU.

### 2. Instalação Padrão (CLI + Dashboard Web)

Ideal para a maioria dos usuários.

- Inclui o dashboard web.
- Endpoints de API REST.
- Gráficos em tempo real.
- Mas sem recursos de simulação ou teste de desempenho.

### 3. Instalação Completa (Padrão + Visualização)

Ideal para desenvolvimento e testes de desempenho.

- Inclui simulação.
- Dependências de PyTorch/CuPy para testes de desempenho.

### Início Rápido

1. **Baixe** a versão mais recente ou clone o repositório.
2. **Execute o Setup**:

  ```powershell
  .\setup.ps1
  ```

3. **Inicie**:

```powershell
# Inicie o dashboard web (Padrão/Completa)
python health_monitor.py web

# Inicie o CLI
python health_monitor.py cli
```