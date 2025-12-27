<!-- HTML_BLOCK:1... -->
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
<!-- HTML_BLOCK:2... -->
<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU 로고"/>
</div>
<!-- HTML_BLOCK:... -->

> *MyGPU: 가벼운 GPU 관리 유틸리티: 컴팩트한 `nvidia-smi` 래핑과 우아한 웹 대시보드.*

## 갤러리

<details>
  <summary>웹 대시보드</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- 첫 번째 이미지의 측비 1624x675로 슬라이드 프레임 사용; 이미지 `object-fit: contain`으로 맞춤 -->
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

### 사용 이유?

- **가볍다**: 최소한의 리소스 발자국.
- **유연하다**: CLI 도구, 또는 완전한 웹 대시보드 형태로 제공.
- **관리자 중심**: VRAM 제한(초과 시 자동 종료) 및 감시 기능 포함.
- **개발자 친화적**: 벤치마킹 및 스트레스 테스트 도구(GEMM, 입자 물리학)를 내장하여 시스템 안정성 검증.

---

## 기능

- **실시간 모니터링**:
  - GPU 메트릭(사용률, VRAM, 전력, 온도).
  - 시스템 메트릭(CPU, RAM 등).

- **관리 및 집행**:
  - **VRAM 제한**: 각 GPU에 대해 VRAM 사용량 제한 설정.
  - **자동 종료**: VRAM 정책을 위반하는 프로세스를 자동으로 종료(관리자 전용).
  - **감시 목록**: 특정 PID 또는 프로세스 이름을 감시.

- **벤치마킹 및 시뮬레이션**:
  - **스트레스 테스트**: 구성 가능한 GEMM 워크로드를 사용하여 열 분산 및 안정성 테스트.
  - **입자 물리학 시각화**: GPU 부하를 시각화하기 위한 상호형 3D 입자 물리학 시뮬레이션.

---

## 로드맵 및 미래 작업

기여는 환영합니다! 주요 향후 개발 사항은 다음과 같습니다.

- **다중 GPU 지원**: 다중 카드 설정 및 NVLink 토폴로지에 대한 향상된 처리.
- **컨테이너화**: 공식 Docker 지원을 통해 컨테이너화된 환경에서 쉽게 배포.
- **원격 액세스**: SSH 터널링 통합 및 안전한 원격 관리.
- **플랫폼 간 지원**:
  - [ ] Linux 지원(Ubuntu/Debian 중점).
  - [ ] Apple Silicon을 위한 macOS 지원 추가.
- **하드웨어 무관성**:
  - [ ] AMD ROCm 지원.
  - [ ] Intel Arc 지원.
- ~~**다국어 문서화**: GitHub에서 가장 인기 있는 언어로 지원.~~

[CONTRIBUTING.md](../CONTRIBUTING.md)를 참조하여 참여 방법 알아보기.

---

## 요구 사항

- **OS**: Windows 10/11
- **Python**: 3.10 이상
- **하드웨어**: NVIDIA GPU 및 설치 드라이버.
- **CUDA**: 12.x 툴킷(벤치마킹/시뮬레이션 기능 사용 시 필수).
  - *참고: CUDA 12.x가 감지되지 않으면 GPU 관련 벤치마킹 기능이 비활성화됩니다.*

---

## 설치

도구는 모듈식 설치를 지원하여 요구 사항에 맞게 조정할 수 있습니다.

### 1. 최소(CLI 전용)

헤드리스 서버 또는 백그라운드 모니터링에 적합합니다.

- 명령줄 인터페이스만 제공.
- 기본 시스템/GPU 메트릭 제공.

### 2. 표준(CLI + 웹 UI)

가장 일반적인 사용자를 위한 옵션입니다.

- 웹 대시보드 포함.
- REST API 엔드포인트.
- 실시간 차트.
- 하지만 시뮬레이션 또는 벤치마킹 기능은 없습니다.

### 3. 전체(표준 + 시각화)

개발 및 스트레스 테스트에 적합합니다.

- 시뮬레이션 기능 포함.
- PyTorch/CuPy 의존성(벤치마킹용).

---

## 라이선스

MIT 라이선스. 자세한 내용은 [LICENSE](../LICENSE)을 참조하세요.