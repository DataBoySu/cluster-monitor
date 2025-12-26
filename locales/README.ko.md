<div align="center">
  <a href="../README.md">🇺🇸 영어</a> |
  <a href="../README.de.md">🇩🇪 독일어</a> |
  <a href="../README.fr.md">🇫🇷 Französisch</a> |
  <a href="../README.es.md">🇪🇸 Spanisch</a> |
  <a href="../README.ja.md">🇯🇵 Japanisch</a> |
  <a href="../README.zh.md">🇨🇳 Chinesisch</a> |
  <a href="../README.pt.md">🇵🇹 Portugiesisch</a> |
  <a href="../README.ko.md">🇰🇷 Koreanisch</a> |
  <a href="../README.hi.md">🇮🇳 Hindi</a>
</div>

<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU 로고"/>
</div>

> *MyGPU: GPU 관리 유틸리티: NVIDIA smi의 컴팩트한 래핑으로 청결한 웹 대시보드를 제공합니다.*

![라이선스](https://img.shields.io/badge/라이선스-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![버전](https://img.shields.io/badge/버전-1.2.3-blue)
![플랫폼](https://img.shields.io/badge/플랫폼-Windows-lightgrey)
![CUDA 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## 갤러리

<details>
  <summary>웹 대시보드</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
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
    <!-- 추가 이미지 동일한 형식으로 추가 -->
  </div>
</details>

### 사용 이유

- **가벼움**: 최소한의 리소스 사용.
- **유연성**: CLI 도구, 백그라운드 서비스, 또는 완전한 웹 대시보드로 실행 가능.
- **관리자 중심**: VRAM 강제 제한 및 감시 기능과 같은 기능 포함.
- **개발자 친화적**: GEMM 및 입자 물리학 시뮬레이션과 같은 테스트 도구를 통한 시스템 안정성 검증.

---

## 기능

- **실시간 모니터링**:
  - GPU 및 시스템 메트릭(사용률, VRAM, 전력, 온도) 제공.
- **관리 및 강제 실행**:
  - VRAM 제한 설정(GPU당).
  - 관리자 전용: VRAM 정책 위반 시 자동 종료(강제 종료).
  - 감시 목록: 특정 PID 또는 프로세스 이름으로 감시.
- **벤치마킹 및 시뮬레이션**:
  - GEMM 워크로드(열적 스로틀링 및 안정성 테스트)를 위한 스트레스 테스트.
  - GPU 부하 시각화를 위한 상호형 입자 물리학 시뮬레이션.

---

## 로드맵 및 미래 작업

기여 환영! 주요 향후 개발 사항은 다음과 같습니다.

- **다중 GPU 지원**: 다중 카드 설정 및 NVLink 토폴로지에 대한 향상된 처리.
- **컨테이너화**: Docker 공식 지원으로 컨테이너 환경에서 쉽게 배포.
- **원격 액세스**: SSH 터널링 통합 및 안전한 원격 관리.
- **플랫폼 확장**:
  - [ ] Linux 지원(Ubuntu/Debian 집중).
  - [ ] Apple Silicon을 위한 macOS 지원.
- **하드웨어 독립성**:
  - [ ] AMD ROCm 지원.
  - [ ] Intel Arc 지원.
- ~~[ ] 다국어 문서화: GitHub에서 가장 인기 있는 언어를 지원.~~

[CONTRIBUTING.md](../CONTRIBUTING.md)를 참조하세요.

---

## 요구 사항

- **OS**: Windows 10/11
- **Python**: 3.10 이상
- **하드웨어**: NVIDIA GPU 및 설치 드라이버.
- **CUDA**: 12.x(벤치마킹/시뮬레이션 기능 사용 시 필수).
  - *참고: CUDA 12.x 미탐지 시, 벤치마킹 기능이 비활성화됩니다.*

---

## 설치

모듈식 설치로 요구 사항에 맞게 설치할 수 있습니다.

### 1. 최소(CLI 전용)

서버 또는 백그라운드 모니터링에 적합한 기본 설정.

- 명령줄 인터페이스.
- 기본 시스템/GPU 메트릭 제공.

### 2. 표준(CLI + 웹 UI)

대부분 사용자를 위한 웹 대시보드 및 REST API 엔드포인트 포함.

- 웹 대시보드 실행.
- 실시간 차트 제공.

### 3. 풀(표준 + 시각화)

개발 및 스트레스 테스트에 적합.

- 입자 물리학 시뮬레이션 포함.
- PyTorch/CuPy 의존성(벤치마킹용).

### 빠른 시작

1. **다운로드** 또는 저장소 복제.
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