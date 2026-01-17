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

> *MyGPU: 가벼운 GPU 관리 유틸리티: 우아한 웹 대시보드를 갖춘 NVIDIA SMI 랩퍼.*

<!-- HTML_BLOCK: no change to url; output entire as it is... -->
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-pink)
![Version](https://img.shields.io/badge/version-1.3.0-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## 갤러리

<details>

  <summary>
  웹 대시보드
  </summary>

  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- 첫 번째 이미지의 측면 비율 1624x675를 사용하여 슬라이드 프레임 설정; 이미지는 object-fit:contain을 사용하여 내부에서 맞춰짐 -->
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

### 왜 이를 사용해야 할까요?

- **가볍다**: 최소한의 리소스 사용.
- **유연하다**: CLI 도구 또는 완전한 기능을 갖춘 웹 대시보드로 실행.
- **관리자 중심**: **VRAM 강제 실행** (한계를 초과하는 프로세스를 자동 종료) 및 **관찰 목록**과 같은 기능 포함.
- **개발자 친화적**: GEMM (기하학적 다중 정확 행렬 곱셈), 입자 물리학 등 내장 벤치마킹 및 스트레스 테스트 도구 (시스템 안정성을 검증하기 위한 것)를 통해 시스템 안정성을 검증.

## 기능

- **실시간 모니터링**:
  - GPU 지표 상세 (사용률, VRAM, 전력, 온도)
  - 시스템 지표 (CPU, RAM 등)

- **관리 및 집행**:
  - **VRAM 제한**: GPU당 VRAM 사용량에 하드 한계 설정
  - **자동 종료**: VRAM 정책을 위반하는 프로세스를 자동 종료 (관리자 전용)
  - **감시 목록**: 특정 PIDs 또는 프로세스 이름을 모니터링

- **벤치마킹 및 시뮬레이션**:
  - **스트레스 테스트**: 열 스로틀링 및 안정성을 테스트하기 위한 구성 가능한 GEMM 워크로드
  - **시각화 시뮬레이션**: 상호작용 3D 입자 물리학 시뮬레이션을 통해 GPU 부하 시각화

## 로드맵 및 미래 작업

기여는 환영합니다! 주요 다가올 포인트는 다음과 같습니다:

- **다중 GPU 지원**: 다중 카드 설정과 NVLink 토폴로지에 대한 향상된 처리.
- **컨테이너화**: 공식 Docker 지원으로 컨테이너 환경에서의 쉬운 배포.
- **원격 액세스**: SSH 터널링 통합 및 안전한 원격 관리.
- **크로스 플랫폼**:
  - [완료] Linux 지원 (Ubuntu/Debian 집중).
  - [완료] macOS 지원 (Apple Silicon 모니터링).
- **하드웨어 무관**:
  - [진행 중] AMD ROCm 지원.
  - [진행 중] Intel Arc 지원.
- **다국어 문서화**: [CONTRIBUTING.md](../CONTRIBUTING.md)를 참조하여 참여 방법 확인.

## 요구 사항

- **운영 체제**: Windows 10/11, Linux, macOS
- **Python**: 3.10 이상
- **하드웨어**: NVIDIA GPU (모든 플랫폼), Apple Silicon (macOS), 또는 CPU 전용.
- **CUDA**: 12.x 툴킷 (NVIDIA에서 벤치마크/시뮬레이션을 위한 권장 사항).
  - *참고: CUDA/MPS가 감지되지 않으면 일부 벤치마크 기능이 비활성화될 수 있습니다.*

## 설치

이 도구는 모듈식 설치를 지원하여 필요에 맞게 맞춤 설정할 수 있습니다:

### 1. 최소한 (CLI 전용)

헤드리스 서버나 백그라운드 모니터링에 가장 적합합니다.

- 명령줄 인터페이스
- 기본 시스템/GPU 지표

### 2. 표준 (CLI + 웹 UI)

대부분의 사용자들에게 최적화.

- 웹 대시보드 포함.
- REST API 엔드포인트.
- 실시간 차트.
- 하지만 시뮬레이션이나 벤치마크 기능은 없음.

### 3. 전체 (표준 + 시각화)

개발 및 스트레스 테스트에 가장 적합합니다.

- 시뮬레이션 포함
- PyTorch/CuPy 벤치마크 의존성

### 빠른 시작

1. **저장소**를 다운로드하거나 클론하십시오.
2. **설정 실행**:

   **윈도우**:

```powershell
   .\setup.ps1
   ```

**Linux/macOS**:

```bash
chmod +x setup.sh
./setup.sh
```

# 실행


```bash
# 웹 대시보드 시작 (표준/완전)
python health_monitor.py web

# CLI 시작
python health_monitor.py cli
```

## 라이선스

<summary>세부 사항</summary>

[라이선스](../LICENSE)를 참조하세요.

