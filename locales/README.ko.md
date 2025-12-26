<div align="center">
  <a href="../README.md">🇺🇸 영어</a> |
  <a href="../locales/README.de.md">🇩🇪 독일어</a> |
  <a href="../locales/README.fr.md">🇫🇷 프랑스어</a> |
  <a href="../locales/README.es.md">🇪🇸 스페인어</a> |
  <a href="../locales/README.ja.md">🇯🇵 일본어</a> |
  <a href="../locales/README.zh.md">🇨🇳 중국어</a> |
  <a href="../locales/README.pt.md">🇵🇹 포르투갈어</a> |
  <a href="../locales/README.ko.md">🇰🇷 한국어</a> |
  <a href="../locales/README.hi.md">🇮🇳 힌디어</a>
</div>

<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU 로고"/>
</div>

> *MyGPU: 경량 GPU 관리 도구: 컴팩트한 `nvidia-smi` 래핑과 우아한 웹 대시보드.*

<!-- 다음의 shields.io 배지 섹션은 그대로 두세요. -->

![라이선스](https://img.shields.io/badge/라이선스-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![버전](https://img.shields.io/badge/버전-1.2.3-blue)
![플랫폼](https://img.shields.io/badge/플랫폼-Windows-lightgrey)
![CUDA 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## 갤러리

<details>
  <summary>웹 대시보드</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- 첫 번째 이미지 측면 비율 1624x675로 사용; 다른 이미지들은 object-fit:contain으로 맞춤 -->
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

### 왜 이 도구를 사용해야 할까요?

- **가볍다**: 최소한의 리소스 발자국.
- **유연하다**: CLI 도구 또는 완전한 웹 대시보드로 실행 가능.
- **관리자 중심**: VRAM 제한(정책) 및 감시 기능과 같은 기능이 포함됩니다.
- **개발자 친화적**: 스트레스 테스트 및 입자 물리학 시뮬레이션과 같은 벤치마크 도구를 내장하고 있습니다.

---

## 기능

- **실시간 모니터링**:
  - GPU 메트릭(사용률, VRAM, 전력, 온도).
  - 시스템 메트릭(CPU, RAM 등).

- **관리자 및 집행 기능**:
  - **VRAM 제한**: GPU당 VRAM 사용량에 대한 하드 한도 설정.
  - **자동 종료**: VRAM 정책을 위반하는 프로세스를 자동으로 종료(관리자 전용).
  - **감시 목록**: 특정 PID 또는 프로세스 이름을 모니터링합니다.

- **벤치마크 및 시뮬레이션**:
  - **스트레스 테스트**: GEMM 워크로드를 구성하여 열 스로틀링 및 시스템 안정성을 테스트합니다.
  - **시뮬레이션**: 상호작용 3D 입자 물리학 시뮬레이션을 통해 GPU 부하를 시각화합니다.

---

## 로드맵 및 미래 작업

기여는 환영합니다! 주요 미래 포인트는 다음과 같습니다.

- **멀티 GPU 지원**: 다중 카드 설정 및 NVLink 토폴로지에 대한 향상된 처리.
- **컨테이너화**: 공식 Docker 지원을 통해 컨테이너화된 환경에서 쉽게 배포.
- **원격 액세스**: SSH 터널링 통합 및 안전한 원격 관리를 위한 보안 설정.
- **플랫폼 간 지원**:
  - [ ] Linux 지원(Ubuntu/Debian에 초점).
  - [ ] Apple Silicon을 위한 macOS 지원.
- **하드웨어 독립성**:
  - [ ] AMD ROCm 지원.
  - [ ] Intel Arc 지원.
- ~~**다국어 문서화**: GitHub에서 가장 인기 있는 언어를 지원.~~

[CONTRIBUTING.md](../CONTRIBUTING.md)를 참조하세요.

---

## 요구 사항

- **OS**: Windows 10/11
- **Python**: 3.10+
- **하드웨어**: NVIDIA GPU 및 설치 드라이버.
- **CUDA**: 12.x (스트레스 테스트 및 시뮬레이션 기능 사용 시 필수).

---

## 설치

도구는 모듈식 설치를 지원하여 사용자의 요구에 맞게 설치할 수 있습니다.

### 1. 최소(CLI만)

서버에 헤드리스로 설치하거나 백그라운드 모니터링에 최적화.

- 명령줄 인터페이스만 제공.
- 기본 시스템/GPU 메트릭 제공.

### 2. 표준(CLI + 웹 UI)

대부분의 사용자에게 적합.

- 웹 대시보드 포함.
- REST API 엔드포인트.
- 실시간 차트.
- 하지만 시뮬레이션 또는 벤치마크 기능은 없습니다.

### 3. 풀(표준 + 시각화)

개발 및 스트레스 테스트에 적합.

- 시뮬레이션 기능 포함.
- PyTorch/CuPy 의존성(벤치마크 기능 사용 시)

### 빠른 시작

1. **다운로드** 최신 릴리스 또는 저장소를 복제.
2. **설정 실행**:

  ```powershell
  .\setup.ps1
  ```

3. **시작**:

```powershell
# 웹 대시보드 시작(표준/풀)
python health_monitor.py web

# CLI 시작
python health_monitor.py cli
```