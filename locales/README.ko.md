# MyGPU: GPU 관리 도구

MyGPU는 NVIDIA `nvidia-smi`의 컴팩트한 랩어웨어로, 우아한 웹 대시보드를 갖춘 가벼운 GPU 관리 유틸리티입니다.

![라이선스](https://img.shields.io/badge/라이선스-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![버전](https://img.shields.io/badge/버전-1.2.3-blue)
![플랫폼](https://img.shields.io/badge/플랫폼-Windows-lightgrey)
![CUDA 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## 갤러리

### 웹 대시보드

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

- **가볍다**: 리소스 사용량이 적음.
- **유연하다**: CLI 도구 또는 웹 대시보드로 실행 가능.
- **관리자 중심**: VRAM 강제 제한 및 감시 기능 등 포함.
- **개발자 친화적**: GEMM, 입자 물리학 시뮬레이션 등 시스템 안정성을 검증하는 내장 벤치마크 및 스트레스 테스트 도구 제공.

---

## 기능

- **실시간 모니터링**:
  - GPU 및 시스템 메트릭(사용률, VRAM, 전력, 온도) 제공.
- **관리 및 강제 실행**:
  - VRAM 제한 설정(GPU당).
  - VRAM 정책 위반 시 자동 종료(관리자 전용).
  - 특정 PID 또는 프로세스 이름 감시.
- **벤치마크 및 시뮬레이션**:
  - GEMM 워크로드 테스트를 통한 열 분산 및 안정성 테스트.
  - 3D 입자 물리학 시뮬레이션을 통한 GPU 부하 시각화.

---

## 로드맵 및 미래 작업

기여 환영! 향후 주요 포인트는 다음과 같습니다.

- 다중 GPU 지원: NVLink 토폴로지 등 다중 카드 설정 향상.
- 컨테이너화: Docker 공식 지원으로 컨테이너 환경에서 쉽게 배포.
- 원격 액세스: SSH 터널링 통합 및 보안 원격 관리.
- 플랫폼 간 지원:
  - [ ] Linux(Ubuntu/Debian 중점).
  - [ ] Apple Silicon 모니터링.
- 하드웨어 독립:
  - [ ] AMD ROCm 지원.
  - [ ] Intel Arc 지원.
- 다국어 문서: GitHub에서 가장 인기 있는 언어로 문서 지원.

[CONTRIBUTING.md](../CONTRIBUTING.md)를 참조하세요.

---

## 요구 사항

- OS: Windows 10/11
- Python: 3.10 이상
- 하드웨어: NVIDIA GPU 및 설치 드라이버
- CUDA: 12.x (벤치마크 및 시뮬레이션 기능 사용 시 필수).
  - *참고: CUDA 12.x 미탐지 시, GPU 관련 벤치마크 기능이 비활성화됩니다.*

---

## 설치

도구는 사용 요구 사항에 맞게 모듈식 설치가 가능합니다.

### 1. 최소(CLI 전용)

헤드리스 서버 또는 백그라운드 모니터링에 적합합니다.

- 명령줄 인터페이스만 제공.
- 기본 시스템 및 GPU 메트릭 제공.

### 2. 표준(CLI + 웹 UI)

대부분 사용자에게 적합합니다.

- 웹 대시보드 포함.
- REST API 엔드포인트.
- 실시간 차트.
- 하지만 시뮬레이션 또는 벤치마크는 없음.

### 3. 풀(표준 + 시각화)

개발 및 스트레스 테스트에 적합합니다.

- 시뮬레이션 포함.
- PyTorch/CuPy 의존성(벤치마크용).

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