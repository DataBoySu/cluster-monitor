<div align="center">
  <a href="../README.md">🇺🇸 English</a> |
  <a href="../README.de.md">🇩🇪 Deutsch</a> |
  <a href="../README.fr.md">🇫🇷 Français</a> |
  <a href="../README.es.md">🇪🇸 Español</a> |
  <a href="../README.ja.md">🇯🇵 日本語</a> |
  <a href="../README.zh.md">🇨🇳 中文</a> |
  <a href="../README.pt.md">🇵🇹 Português</a> |
  <a href="../README.ko.md">🇰🇷 한국어</a> |
  <a href="../README.hi.md">🇮🇳 Hindi</a>
</div>

<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU logo"/>
</div>

> *MyGPU: 가벼운 GPU 관리 유틸리티: 컴팩트한 `nvidia-smi` 래핑과 우아한 웹 대시보드.*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-1.2.3-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Gallery

<details>
  <summary>Web Dashboard</summary>
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

### 왜 이 유틸리티를 사용해야 할까요?

- **가벼운**: 최소한의 리소스 사용.
- **유연한**: CLI 도구 또는 완전한 웹 대시보드로 실행 가능.
- **관리자 중심**: VRAM 강제(자동 과도한 메모리 사용 프로세스 종료) 및 감시 목록과 같은 기능 포함.
- **개발자 친화적**: GEMM, 입자 물리학 등 내장 벤치마크 및 스트레스 테스트 도구를 통해 시스템 안정성 검증.

---

## 기능

- **실시간 모니터링**:
  - 상세한 GPU 메트릭(사용률, VRAM, 전력, 온도).
  - 시스템 메트릭(CPU, RAM 등).

- **관리자 및 강제 기능**:
  - **VRAM 제한**: GPU당 VRAM 사용량에 대한 하드 한계 설정.
  - **자동 종료**: VRAM 정책을 위반하는 프로세스를 자동 종료(관리자만 가능).
  - **감시 목록**: 특정 PID 또는 프로세스 이름을 모니터링.

- **벤치마크 및 시뮬레이션**:
  - **스트레스 테스트**: 열 순환 및 안정성 테스트를 위한 구성 가능한 GEMM 워크로드.
  - **시각적 시뮬레이션**: 상호작용 3D 입자 물리학 시뮬레이션을 통해 GPU 부하 시각화.

---

## 로드맵 및 미래 작업

기여 환영합니다! 주요 미래 포인트는 다음과 같습니다.

- **다중 GPU 지원**: 다중 카드 설정 및 NVLink 토폴로지에 대한 향상된 처리.
- **컨테이너화**: Docker 공식 지원으로 컨테이너 환경에서 쉽게 배포.
- **원격 액세스**: SSH 터널링 통합 및 보안 원격 관리.
- **교차 플랫폼**:
  - [ ] Linux 지원(Ubuntu/Debian 중점).
  - [ ] macOS 지원(Apple Silicon 모니터링).
- **하드웨어 독립**:
  - [ ] AMD ROCm 지원.
  - [ ] Intel Arc 지원.
- ~~**다국어 문서화**: GitHub에서 가장 인기 있는 언어 지원.~~

[CONTRIBUTING.md](../CONTRIBUTING.md)를 참조하세요.

---

## 요구 사항

- **OS**: Windows 10/11
- **Python**: 3.10+
- **하드웨어**: NVIDIA GPU 및 설치 드라이버.
- **CUDA**: 12.x 툴킷(벤치마크/시뮬레이션 기능 사용 시 엄격히 필요).
  - *참고: CUDA 12.x가 감지되지 않으면 GPU 특정 벤치마크 기능이 비활성화됩니다.*

---

## 설치

도구는 사용 요구 사항에 맞게 모듈식 설치가 가능합니다.

### 1. 최소(CLI 전용)

헤드리스 서버 또는 백그라운드 모니터링에 최적.

- 명령줄 인터페이스.
- 기본 시스템/GPU 메트릭.

### 2. 표준(CLI + 웹 UI)

대부분의 사용자에 최적.

- 웹 대시보드 포함.
- REST API 엔드포인트.
- 실시간 차트.

### 3. 전체(표준 + 시각화)

개발 및 스트레스 테스트에 최적.

- 입자 시뮬레이션 포함.
- PyTorch/CuPy 의존성 벤치마크.

### 빠른 시작

1. **다운로드** 최신 릴리스 또는 저장소 복제.
2. **설정 실행**:

  ```powershell
  .\setup.ps1
  ```

3. **시작**:

```powershell
# 웹 대시보드(표준/전체) 시작
python health_monitor.py web

# CLI 시작
python health_monitor.py cli
```

---

## 라이선스

MIT 라이선스. [LICENSE](../LICENSE)을 참조하세요.