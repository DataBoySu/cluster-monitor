<div align="center">
  <a href="../README.md">🇺🇸 Português</a> |
  <a href="../README.de.md">🇩🇪 Alemão</a> |
  <a href="../README.fr.md">🇫🇷 Francês</a> |
  <a href="../README.es.md">🇪🇸 Espanhol</a> |
  <a href="../README.ja.md">🇯🇵 Japonês</a> |
  <a href="../README.zh.md">🇨🇳 Chinês</a> |
  <a href="../README.pt.md">🇵🇹 Português</a> |
  <a href="../README.ko.md">🇰🇷 Coreano</a> |
  <a href="../README.hi.md">🇮🇳 Hindi</a>
</div>

<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="Logotipo do MyGPU"/>
</div>

> *MyGPU: Utilitário de gerenciamento de GPU leve: um wrapper compacto para `nvidia-smi` com um dashboard web limpo.*

![Licença](https://img.shields.io/badge/licença-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Versão](https://img.shields.io/badge/versão-1.2.3-blue)
![Plataforma](https://img.shields.io/badge/plataforma-Windows-lightgrey)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

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

### Por que usar isso?

- **Leveza**: Pés no chão em termos de uso de recursos.
- **Flexibilidade**: Funciona como uma ferramenta CLI, um serviço em segundo plano ou um dashboard web completo.
- **Foco no administrador**: Inclui recursos como **restrição de VRAM** (encerramento automático de processos que excedem os limites de VRAM) e **listas de observação**.
- **Amigável ao desenvolvedor**: Ferramentas de teste de estabilidade e simulação (GEMM, Física de Partículas) integradas para validar o sistema.

---

### Recursos

- **Monitoramento em tempo real**:
  - Métricas detalhadas de GPU (Utilização, VRAM, Potência, Temperatura).
  - Métricas do sistema (CPU, RAM, etc.).

- **Admin e Restrição**:
  - **Limites de VRAM**: Defina limites rígidos de uso de VRAM por GPU.
  - **Encerramento automático**: Termine automaticamente processos que violem as políticas de VRAM (apenas para administradores).
  - **Listas de observação**: Monitore PIDs ou nomes de processos específicos.

- **Testes e Simulação**:
  - **Testes de estresse**: Configure cargas de trabalho GEMM configuráveis para testar o throttling térmico e a estabilidade.
  - **Simulação visual**: Simulação interativa de física de partículas para visualizar a carga de GPU.

---

### Roadmap e Trabalho Futuro

Contribuições são bem-vindas! Os principais pontos a serem abordados seriam:

- **Suporte Multi-GPU**: Melhor suporte para configurações multi-cartão e topologias NVLink.
- **Containerização**: Suporte oficial para Docker para implantação fácil em ambientes contêinerizados.
- **Acesso remoto**: Integração de túnel SSH e gerenciamento remoto seguro.
- **Plataformas cruzadas**:
  - [ ] Suporte a Linux (foco em Ubuntu/Debian).
  - [ ] Suporte a Apple Silicon para monitoramento.
- **Hardware independente**:
  - [ ] Suporte AMD ROCm.
  - [ ] Suporte Intel Arc.
- ~~**Documentação em vários idiomas**: Suporte para os principais idiomas do GitHub.~~

Consulte [CONTRIBUTING.md](../CONTRIBUTING.md) para saber como contribuir.

---

### Requisitos

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Hardware**: GPU NVIDIA com drivers instalados.
- **CUDA**: Versão 12.x (estritamente necessária para recursos de teste/simulação).
  - *Observação: Se a CUDA 12.x não for detectada, os recursos de teste/simulação serão desabilitados.*

---

### Instalação

A ferramenta suporta instalação modular para atender às suas necessidades:

### 1. Instalação Mínima (apenas CLI)

Ideal para servidores sem cabeça ou monitoramento em segundo plano.

- Interface de linha de comando.
- Monitoramento básico do sistema e da GPU.

### 2. Instalação Padrão (CLI + Dashboard Web)

Ideal para a maioria dos usuários.

- Inclui Dashboard Web.
- Endpoints de API REST.
- Gráficos em tempo real.

### 3. Instalação Completa (Padrão + Simulação)

Ideal para desenvolvimento e testes de estresse.

- Inclui Simulação de Física de Partículas.
- Dependências do PyTorch/CuPy para testes de benchmark.

### Início rápido

1. **Baixe** a versão mais recente ou clone o repositório.
2. **Execute o script de configuração**:

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