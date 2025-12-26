<div align="center">
  <a href="../README.md">🇺🇸 English</a> |
  <a href="README.de.md">🇩🇪 Deutsch</a> |
  <a href="README.fr.md">🇫🇷 Français</a> |
  <a href="README.es.md">🇪🇸 Español</a> |
  <a href="README.ja.md">🇯🇵 日本語</a> |
  <a href="README.zh.md">🇨🇳 中文</a> |
  <a href="README.pt.md">🇵🇹 Português</a> |
  <a href="README.ko.md">🇰🇷 한국어</a>
</div>

<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU 로고"/>
</div>

> *MyGPU: 가벼운 GPU 관리 유틸리티: NVIDIA smi의 간결한 랩핑과 우아한 웹 대시보드가 결합된 도구.*

![라이선스](https://img.shields.io/badge/라이선스-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![버전](https://img.shields.io/badge/버전-1.2.3-blue)
![플랫폼](https://img.shields.io/badge/플랫폼-Windows-lightgrey)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## 갤러리

<details>
  <summary>웹 대시보드</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- 첫 번째 이미지를 1624x675 비율로 사용하여 슬라이드 프레임으로 설정하고, 다른 이미지들은 'object-fit: contain'을 사용하여 내부에서 채우기 -->
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

### 사용 이유

- **가볍다**: 자원 사용량이 적음.
- **유연하다**: CLI 도구 또는 웹 대시보드로 실행 가능.
- **관리자 중심**: VRAM 제한(정책 준수 시 자동 종료) 및 감시 기능 포함.
- **개발자 친화적**: GEMM, 입자 물리학 시뮬레이션 등 다양한 시각적 도구를 통한 시스템 안정성 테스트.

---

## 기능

- **실시간 모니터링**:
  - GPU 메트릭(사용률, VRAM, 전력, 온도).
  - 시스템 메트릭(CPU, RAM 등).

- **관리자 및 집행 기능**:
  - **VRAM 제한**: GPU당 VRAM 사용량에 대한 제한 설정.
  - **자동 종료**: VRAM 정책을 위반하는 프로세스를 자동 종료(관리자 전용).
  - **감시 목록**: 특정 PID 또는 프로세스 이름을 모니터링.

- **벤치마킹 및 시뮬레이션**:
  - **스트레스 테스트**: GEMM 워크로드를 사용하여 열 분산 및 안정성을 테스트.
  - **시각화 시뮬레이션**: GPU 부하를 시각화하는 입자 물리학 시뮬레이션.

---

## 로드맵 및 미래 작업

기여는 환영합니다! 앞으로 다룰 주요 사항은 다음과 같습니다.

- **다중 GPU 지원**: 다중 카드 설정 및 NVLink 토폴로지에 대한 향상된 처리.
- **컨테이너화**: Docker 공식 지원을 통해 컨테이너 환경에서 쉽게 배포.
- **원격 액세스**: SSH 터널링 통합 및 안전한 원격 관리.
- **플랫폼 확장**:
  - [ ] Linux 지원(Ubuntu/Debian 집중).
  - [ ] Apple Silicon을 위한 macOS 지원.
- **하드웨어 무관성**:
  - [ ] AMD ROCm 지원.
  - [ ] Intel Arc 지원.
- ~~**다국어 문서화**: GitHub에서 가장 인기 있는 언어로 문서화.~~

기여 방법은 [CONTRIBUTING.md](../CONTRIBUTING.md)를 참조하세요.

---

## 요구 사항

- **OS**: Windows 10/11
- **Python**: 3.10+
- **하드웨어**: NVIDIA GPU 및 설치 드라이버.
- **CUDA**: 12.x 툴킷(벤치마킹/시뮬레이션 기능 사용 시 필수).
  - *참고: CUDA 12.x가 감지되지 않으면 GPU 관련 벤치마킹 기능이 비활성화됩니다.*

---

## 설치

도구는 모듈식 설치를 지원하여 사용자의 요구에 맞게 설치할 수 있습니다.

### 1. 최소(CLI만)

서버나 백그라운드 모니터링에 적합합니다.

- 명령줄 인터페이스만 제공.
- 기본 시스템/GPU 메트릭 제공.

### 2. 표준(CLI + 웹 UI)

대부분의 사용자에게 적합합니다.

- 웹 대시보드 포함.
- REST API 엔드포인트.
- 실시간 차트.

### 3. 풀(표준 + 시각화)

개발 및 스트레스 테스트에 적합합니다.

- 입자 시뮬레이션 포함.
- PyTorch/CuPy 의존성(벤치마킹용).

### 빠른 시작

1. **다운로드** 최신 릴리스 또는 저장소를 복제하세요.
2. **설정 실행**:

  ```powershell
  .\setup.ps1
  ```

3. **실행**:

```powershell
# 웹 대시보드 시작(표준/풀)
python health_monitor.py web

# CLI 시작
python health_monitor.py cli
```