[보호된 블록 0]

[보호된 블록 1]

> *MyGPU: GPU 관리 유틸리티: NVIDIA smi의 컴팩트한 랩핑과 우아한 웹 대시보드.*

[보호된 블록 2] [보호된 블록 3] [보호된 블록 4] [보호된 블록 5] [보호된 블록 6]

## 갤러리

<details>
  <summary>웹 대시보드</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- 첫 번째 이미지 측면 비율 1624x675로 슬라이드 프레임 사용; 이미지는 object-fit:contain로 내부에서 맞춰짐 -->
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

### 사용 이유

- **가볍다**: 최소한의 리소스 사용.
- **유연하다**: CLI 도구, 또는 웹 대시보드로 실행 가능.
- **관리자 중심**: VRAM 강제 실행(한도 초과 시 자동 종료) 및 감시 기능 포함.
- **개발자 친화적**: GEMM, 입자 물리학 시뮬레이션 등 시스템 안정성을 검증하기 위한 내장 벤치마크 및 스트레스 테스트 도구 제공.

---

## 기능

- **실시간 모니터링**:
  - GPU 메트릭(사용률, VRAM, 전력, 온도).
  - 시스템 메트릭(CPU, RAM 등).

- **관리 및 강제 실행**:
  - **VRAM 한도**: 각 GPU의 VRAM 사용량에 대한 하드 한도 설정.
  - **자동 종료**: 관리자만 VRAM 정책을 위반하는 프로세스를 자동 종료할 수 있음.
  - **감시 목록**: 특정 PID 또는 프로세스 이름을 감시.

- **벤치마크 및 시뮬레이션**:
  - **스트레스 테스트**: GEMM 워크로드를 사용하여 열 스로틀링 및 안정성을 테스트.
  - **시각화 시뮬레이션**: GPU 부하를 시각화하기 위한 상호형 3D 입자 물리학 시뮬레이션.

---

## 로드맵 및 미래 작업

기여 환영! 주요 미래 작업은 다음과 같습니다.

- **다중 GPU 지원**: 다중 카드 설정 및 NVLink 토폴로지에 대한 향상된 처리.
- **컨테이너화**: Docker 공식 지원을 통해 컨테이너 환경에서 쉽게 배포.
- **원격 액세스**: SSH 터널링 통합 및 안전한 원격 관리.
- **플랫폼 간 지원**:
  - [ ] Windows 10/11
  - [ ] macOS (Apple Silicon 모니터링)
- **하드웨어 간 지원**:
  - [ ] AMD ROCm 지원.
  - [ ] Intel Arc 지원.
- ~~[ ] 다국어 문서: GitHub에서 가장 인기 있는 언어로 문서화.~~

[CONTRIBUTING.md](../CONTRIBUTING.md)를 참조하세요.

---

## 요구 사항

- **OS**: Windows 10/11
- **Python**: 3.10+
- **하드웨어**: NVIDIA GPU 및 설치 드라이버.
- **CUDA**: 12.x 툴킷(벤치마크 및 시뮬레이션 기능 사용 시 필수).
  - *참고: CUDA 12.x가 감지되지 않으면 GPU 관련 벤치마크 기능이 비활성화됩니다.*

---

## 설치

도구는 모듈식 설치를 지원하여 사용자의 요구에 맞게 설치할 수 있습니다.

### 1. 최소(CLI만)

서버에 헤드리스로 설치하거나 백그라운드 모니터링에 적합합니다.

- 명령줄 인터페이스만 제공.
- 기본 시스템 및 GPU 메트릭 제공.

### 2. 표준(CLI + 웹 UI)

대부분의 사용자에게 적합합니다.

- 웹 대시보드 포함.
- REST API 엔드포인트.
- 실시간 차트 제공.

### 3. 풀(표준 + 시각화)

개발 및 스트레스 테스트에 적합합니다.

- 입자 시뮬레이션 포함.
- PyTorch/CuPy 의존성(벤치마크용).

### 빠른 시작

1. **최신 버전 다운로드 또는 저장소 복제**.
2. **설정 스크립트 실행**:

  ```powershell
  .\setup.ps1
  ```

3. **실행**:

```powershell
# 웹 대시보드(표준/풀) 시작
python health_monitor.py web

# CLI 시작
python health_monitor.py cli
```