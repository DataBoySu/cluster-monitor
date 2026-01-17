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

> *MyGPU: Utilitário de Gerenciamento de GPU Leve: um compactador de `nvidia-smi` com um elegante painel web.*

<!-- HTML_BLOCK: no change to url; output entire as it is... -->
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-pink)
![Version](https://img.shields.io/badge/version-1.3.0-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galeria

<details>

  <summary>
  Painel Web
  </summary>

  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Utilize a primeira imagem com proporção 1624x675 como quadro da apresentação; as imagens se ajustam usando object-fit:contain -->
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

### Por que usá-lo?

- **Leve**: Pegada de recursos mínima.
- **Flexível**: Funciona como uma ferramenta de linha de comando (CLI) ou um painel web completo.
- **Focado no administrador**: Inclui recursos como **aplicação de políticas de VRAM** (desligar processos que excedam limites automaticamente) e **listas de observação**.
- **Amigável para desenvolvedores**: Ferramentas de benchmarking e teste de estresse embutidas (GEMM, Física de Partículas) para validar a estabilidade do sistema.

## Recursos

- **Monitoramento em Tempo Real**:
  - Métricas detalhadas de GPU (Utilização, VRAM, Potência, Temperatura).
  - Métricas do sistema (CPU, RAM, etc.).

- **Administração e Aplicação de Políticas**:
  - **Limites de VRAM**: Defina limites rígidos no uso de VRAM por GPU.
  - **Terminação Automática**: Termine automaticamente processos que violarem as políticas de VRAM (apenas administrador).
  - **Listas de Observação**: Monitore PIDs ou nomes de processos específicos.

- **Benchmarking e Simulação**:
  - **Testes de Estresse**: Carga de trabalho configurável de GEMM para testar o throttling térmico e a estabilidade.
  - **Simulação Visual**: Simulação interativa de física de partículas 3D para visualizar a carga na GPU.

## Roadmap & Trabalhos Futuros

Contribuições são bem-vindas! Os principais pontos futuros a serem abordados incluem:

- **Suporte Multi-GPU**: Melhoria no manuseio de configurações multi-cartão e topologias NVLink.
- **Containerização**: Suporte oficial para Docker para implantação fácil em ambientes containerizados.
- **Acesso Remoto**: Integração de túnel SSH e gerenciamento remoto seguro.
- **Cross-Platform**:

  - [x] Suporte a Linux (foco em Ubuntu/Debian).
  - [x] Suporte a macOS (monitoramento de Apple Silicon).

- **Agnóstico de Hardware**:

  - [ ] Suporte a AMD ROCm.
  - [ ] Suporte a Intel Arc.

- **Documentação Multi-Linguagem**: (Removido da lista)

Consulte o [CONTRIBUTING.md](../CONTRIBUTING.md) para saber como participar.

## Requisitos

- **Sistema Operacional**: Windows 10/11, Linux, macOS
- **Python**: 3.10+
- **Hardware**: GPU NVIDIA (todos os sistemas), Apple Silicon (macOS) ou apenas CPU.
- **CUDA**: Toolkit 12.x (Recomendado para Benchmarking/Simulação em NVIDIA).
  - *Observação: Se CUDA/MPS não for detectado, algumas funcionalidades de benchmarking podem estar desabilitadas.*

## Instalação

A ferramenta suporta instalação modular para atender às suas necessidades:

### 1. Mínimo (Interface de Linha de Comando Apenas)

Ideal para servidores sem interface gráfica ou monitoramento em segundo plano.

- Interface de linha de comando.
- Métricas básicas de sistema/GPU.

### 2. Padrão (CLI + Interface Web)

O ideal para a maioria dos usuários.

- Inclui Dashboard Web.
- Pontos finais de API REST.
- Gráficos em tempo real.
- Sem Simulação ou benchmarking.

### 3. Completo (Padrão + Visualização)

Ideal para desenvolvimento e testes de estresse.

- Inclui Simulação.
- Dependências PyTorch/CuPy para benchmarking.

### Início Rápido

1. **Baixe** ou clone o repositório.
2. **Execute a Configuração**:

   **Windows**:

```powershell
   .\setup.ps1
   ```

**Linux/macOS:**

```bash
  chmod +x setup.sh
  ./setup.sh
```

**Lançamento:**

```bash
# Inicie o painel web (Padrão/Completo)
python health_monitor.py web

# Inicie o modo CLI
python health_monitor.py cli
```

## Licença

Consulte [LICENSE](../LICENSE) para detalhes.

