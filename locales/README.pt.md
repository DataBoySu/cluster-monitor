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

> *MyGPU: Uma Utilidade de Gerenciamento de GPU Leve: um envolto compacto do `nvidia-smi` com um dashboard web elegante.*

## Galeria

<details>

  <summary>
  Dashboard Web
  </summary>

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

### Por que usar isso?

- **Leveza**: Pés no chão em termos de uso de recursos.
- **Flexibilidade**: Funciona como uma ferramenta CLI, ou um dashboard web completo.
- **Orientado a Administrador**: Inclui recursos como **Limites de VRAM** (desabilitação automática de processos que excedem políticas) e **Listas de Observação**.
- **Amigável ao Desenvolvedor**: Inclui ferramentas de teste de desempenho integradas (GEMM, Física de Partículas) para validar a estabilidade do sistema.

---

### Recursos

- **Monitoramento em Tempo Real**:
  - Métricas detalhadas da GPU (Utilização, VRAM, Potência, Temperatura).
  - Métricas do sistema (CPU, RAM, etc.).

- **Admin e Aplicação de Políticas**:
  - **Limites de VRAM**: Defina limites rígidos de uso de VRAM por GPU.
  - **Desabilitação Automática**: Termine automaticamente processos que violem políticas de VRAM (apenas para administradores).
  - **Listas de Observação**: Monitore PIDs ou nomes de processos específicos.

- **Testes e Simulação**:
  - **Testes de Estresse**: Configure cargas de trabalho GEMM configuráveis para testar o throttling térmico e a estabilidade.
  - **Simulação Interativa**: Visualize a carga de trabalho da GPU usando uma simulação de física de partículas 3D.

---

### Roadmap e Trabalho Futuro

Contribuições são bem-vindas! Os principais pontos futuros a serem abordados seriam:

- **Suporte Multi-GPU**: Melhor suporte para configurações multi-card e topologias NVLink.
- **Containerização**: Suporte oficial do Docker para implantação fácil em ambientes de contêiner.
- **Acesso Remoto**: Integração de túnel SSH e gerenciamento remoto seguro.
- **Plataforma Cruzada**:
  - [ ] Suporte a Linux (foco em Ubuntu/Debian).
  - [ ] Suporte a Apple Silicon para monitoramento.
- **Hardware Agnóstico**:
  - [ ] Suporte AMD ROCm.
  - [ ] Suporte Intel Arc.
- **Documentação Multilíngue**: Suporte aos idiomas mais populares do GitHub.

Veja [CONTRIBUTING.md](../CONTRIBUTING.md) para saber como contribuir.

---

### Requisitos

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: GPU NVIDIA com drivers instalados.
- **CUDA**: Versão 12.x (estritamente necessária para recursos de teste de desempenho/simulação).
  - *Observação: Se a CUDA 12.x não for detectada, os recursos de teste de desempenho serão desabilitados.*

---

### Instalação

A ferramenta suporta instalação modular para atender às suas necessidades:

### 1. Instalação Mínima (CLI apenas)

Ideal para servidores sem cabeça ou monitoramento em segundo plano.

- Interface de linha de comando.
- Monitoramento básico do sistema e da GPU.

### 2. Instalação Padrão (CLI + Dashboard Web)

Ideal para a maioria dos usuários.

- Inclui o Dashboard Web.
- Endpoints de API REST.
- Gráficos em tempo real.
- Mas sem recursos de simulação ou teste de desempenho.

### 3. Instalação Completa (Padrão + Simulação)

Ideal para desenvolvimento e testes de estresse.

- Inclui Simulação.
- Dependências do PyTorch/CuPy para testes de desempenho.

### Início Rápido

1. **Baixe** a versão mais recente ou clone o repositório.
2. **Execute o Setup**:

  ```powershell
  .\setup.ps1
  ```

3. **Inicie**:

```powershell
# Inicie o Dashboard Web (Padrão/Completa)
python health_monitor.py web

# Inicie o CLI
python health_monitor.py cli
```