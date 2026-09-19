# 동영상 자동화 4-MCP 통합 기술백서
## 딥페이크 · 빅테크튜토리얼 · 판서튜토리얼 · 박씨티칭
### 작성 2026-09-12 · Claude Sonnet 5 (WSL 세션) · 레포 `~/parksy-image/tools/`

> 이 문서는 4개 MCP의 실제 코드/DEVLOG/WHITEPAPER를 직접 읽고 종합한 것이다.
> raw 근거(커밋 해시, 실측 수치, 파일 경로)는 각 섹션에 그대로 남긴다.

---

## 0. 트릴로지 개념도 — "누가 수행하나"

| | ① 딥페이크 강의 | ② 빅테크 튜토리얼 | ③ 판서 튜토리얼 | ④ 박씨 티칭 |
|---|---|---|---|---|
| MCP 등록명 | `po-deepfake` | `bigtech-tutorial` | `po-tutorial` | `parksy-teaching` |
| PO 번호 | PO-250825-01 | (등록명 개명, 구 `tutor`) | (트랙B) | PO-250901-01 |
| 코드 위치 | `tools/mcp_deepfake/` | `tools/mcp_tutor/` | `tools/mcp_tutorial/` | `tools/mcp_teaching/` |
| 수행자 | 합성 인간 (Grok 딥페이크 영상 + RVC 음색교체) | 기계 (화면+터미널 자동 캡처) | 기계 (판서 컴포지터) | **실제 인간 (교육자 라이브)** |
| 편집 비중 | 100% 후반 | 100% 후반 | 100% 후반 | **~0% (live-to-tape)** |
| 최근 실효 상태 | 미니PC 도커 E2E 완주(2026-09-07) | L10/90점(2026-09-04) | V25F8 완성(2026-08-31), 태블릿 실황 진행중 | 아키텍처 9/10, 실기기 게이트 대기(2026-09-07) |

한 줄: **① 합성 인간 수행 → ② 기계 수행 → ③(트랙B) 기계 수행(판서 특화) → ④ 실제 인간 수행**, 스펙트럼 전체를 한 레포가 덮는 구조.

---

## 1. 딥페이크 (`po-deepfake`, PO-250825-01)

### 1.1 파이프라인 (G0~G6.5)
```
G0 사전 → G1 플랜(45~55음절/10초) → G2 Grok 생성(CAI, 사진1장+대사) →
G3 RVC 음색교체(parksy_rvc_v3) → G3.9 blackramp(암전연결) → G4 concat →
G5 QA(sim≥0.70) → G6 텔레그램 전송 → G6.5 썸네일
```
MCP 툴 2개(감옥원칙): `po_deepfake_make`(실행) / `po_deepfake_status`(탈출구, gates/sim/숏 숫자 보고).

### 1.2 최근 개발 이력 — 미니PC 도커 이식 (2026-09-07, §15)

**문제**: 미니PC(Win7 임베디드, 딥시크 담당)에서 po-deepfake 도커 컨테이너를 돌리는데
빌드머신(WSL, `HOME=/home/dtsli`)과 컨테이너(`HOME=/app`) 경로 불일치로 게이트마다 지뢰.

| 게이트 | 지뢰 | 조치 | 커밋 |
|---|---|---|---|
| G2 | `chrome_cdp.sh`에 `--remote-allow-origins=*` 누락 → CDP WebSocket 403 | 플래그 추가 + Chrome 재기동 | `f521a12` |
| G2 | `one_shot.sh`가 track=pc를 "powershell.exe 유무"로 판정 → 리눅스 미니PC는 강제 headless(봇탐지 걸림) | 판정을 "CDP `/json/version` 응답 여부"로 교체 | `a980773` |
| G3 | `assets/weights/parksy_rvc_v3.pth` 심링크가 `/home/dtsli/...` 가리켜 컨테이너에서 dangling | `rvc_convert.py`가 실제 마운트 경로로 재심링크 | `76f-` |
| G3 | `.index` 파일을 첫 루프에서 못 찾아 index_rate 무효(잠재 버그, laptop도 동일) | `_sibling_index()` 항상 반환 + `RVC_INDEX` env 우선 | — |
| G6.5 | 썸네일 폰트 `/usr/share/fonts/.../NotoSerifCJK-Bold.ttc` 하드코딩, 컨테이너에 없음 | `_resolve_font()` 후보탐색+fc-match | — |

**결과 (2026-09-07 06:35~)**: `OrbitPrompt_Promo` 프로젝트로 미니PC 도커 **G0~G6.5 전 게이트 최초 완주**.
```
G2 ✅ 6컷(track=pc, 미니PC 리눅스 Chrome CDP) 각 10.04s
G3 ✅ RVC best-of-4, sim 0.79~0.82 → QA-A 0.8072/QA-B 0.8074 pass
G4 ✅ concat 28.4MB / 59.6s / 880x1040
G5 ✅ sim=0.8495
G6 ✅ 텔레그램 전송
```
이후 스톱갭들을 Dockerfile에 정식 반영해 **새 이미지 `d6ef486c26ea`(6.78GB)** 리빌드,
미니PC↔랩탑 양방향 배포 완료(md5 동일성 실측 확인).

### 1.3 RVC 화자 정합 사고 (2026-09-08, §16)
- 증상: 딥페이크와 튜토리얼(po-tutorial) 나레이션이 같은 박씨 목소린데 다른 사람처럼 들림.
- 원인: 전부 동일 설정인데 `pipeline_config.json`의 `rvc.key`만 딥페이크=`0`, 튜토리얼=`-6`으로 어긋나 있었음.
  (v1→v3 모델 전환 시 key를 안 고침 — v3는 key=0이 여성/경계, -6이라야 박씨 남성대역 F0 124Hz 안착)
- 수정: `pipeline_config.json` key 0→-6 (v1.1→v1.2). 호출마다 파일 재로드라 MCP reconnect 불필요.
- 한계: 운율·억양(Grok AI 보이스 vs edge-tts InJoon 교사톤)까지는 RVC로 못 지움 — key 정합까지가 현실 범위.

---

## 2. 빅테크 튜토리얼 (`bigtech-tutorial`, 구 `tutor`)

### 2.1 설계 배경 (2026-08-29 착수)
- 기존 `po_tutorial_make`(딥시크/에이더 제작) 평가 62/100 — 스마트줌/클릭리플/커서글라이드 등
  "빅테크 프리미엄 3요소" 전무. → **완전 독립 신규 MCP**로 분리(po-deepfake 코드는 안 건드림).
- 핵심 설계원칙: **템플릿=정적자산(LLM 런타임 생성 금지, 편차 방지) / 메타레이어(커서·리플·펀치인)는 compositor.py에 영구 분리**.

### 2.2 BIGTECH_PARITY_SPEC — 파리티 사다리 L1~L13
자가채점을 금지하고 자동 게이트(L1~L13, 각 칸 통과/실패 수치 판정)로 대체. 낮은 칸부터 순서대로 통과.
| 레벨 | 내용 | 게이트 |
|---|---|---|
| L1~L2 | 레터박스 없음 / 3회 캡처 재현성(SSIM) | gate_l1, gate_l2 |
| L3 | 카메라 프레임 여백(px) | gate_l3 |
| L4 | 자막 규율(이중라벨 금지) | gate_l4 |
| L5 | 카메라 앵커(줌 윈도우 실제 좌표 연동) | gate_l5 |
| L6 | 모션(이징) | gate_l6 |
| L7 | 실행면(터미널) 진본성 — 가짜 스킨 리터럴 금지 or 실캡처 판정 | gate_l7 |
| L8 | 이음새(ΔE 색상 그레이드 통일) | gate_l8 |
| L9 | 러프니스(loudnorm -14 LUFS) | gate_l9 |
| L10 | 무음 구간 검출(3초 윈도우별) | gate_l10 |
| L11 | 실기기 캡처 진본(exec_surface.py, PC 실화면) | gate_l11 |
| L12~L13 | 실제 워크플로 / 블라인드 5인 패널 | 수동 |

### 2.3 버전 이력 (요약, 전체 V1~V32)
- **V1~V18** (2026-08-29~08-31): 뼈대(compositor.py/tutor.py/tutor_mcp.py) → E2E 통과했으나 박씨 판정 **NG**(자가채점 인플레 사고, `feedback_self_score_inflation_video_quality` 발생). V18에 태블릿 실화면 캡처 레이어 커밋만 되고 미배선.
- **V19** (09-02): `bt_append` 무음 버그 근본수정 — `amix duration=first`가 짧은 오디오 기준으로 잘라 **V14~V18 전 산출물의 터미널 이어붙이기 구간이 전부 무음**이었음. `duration=longest`로 수정. BIGTECH_PARITY_SPEC.md 신설, 실측 레벨 L2~L3(자동게이트 바닥은 10점).
- **V20~V21** (09-02): 엔진↔페이지 계약 디커플(`window.__tutor` v2), `qa_gate.py` 신설 + `.qa_ledger.json` 회귀 래칫. V19 실측 = **10/100 전송차단**(L3/L7/L9/L10 전부 FAIL).
- **V22~V23** (09-02): L3 레이아웃 정착, L4 자막 폐기, L9 loudnorm, `cc_skin.py`(실제 Claude Code TUI 스킨 렌더러) 신설 — L7 PASS.
- **V24** (09-02): Grok Imagine 개념컷 인라인 합성(`concept_cut.py`) — PC WSL2 Chrome 직접 로그인 트랙, 태블릿 ADB/CDP 배제(헌법 "죽은 패턴" 준수).
- **V25** (09-03): `exec_surface.py` 신설 — WSL→Windows PowerShell 화면캡처(`.NET CopyFromScreen`)로 **실제 PC 화면 캡처**. cc_skin은 폴백으로 강등. 실측: 현재 PC가 TV 복제 720p라 L11 조건 미충족(진단만).
- **V26** (09-03): 엔진 렌더프레임 L3 근본해결(webm 인코딩 드리프트 보정 ×1.067~1.069, base_z 바닥줌, 앵커 세로클램프) — gate_l3/l1 PASS.
- **V27~V27d** (09-03): STEP5 재정의(딥시크=입력면/클로드코드=실행면), 랜딩크레딧 폐기(gate_l9/l10 원인 제거), L2 재현성(SSIM 0.9992), L4. **V27d = l1·l2·l3·l4·l7·l9·l10·common 전부 PASS, qa 54/100, 실효레벨 L4, 전송 승인.**
- **V28~V32** (09-04): 아이콘 계약(이모지 폐기, 인라인 SVG 17종), gate_l5(카메라)/l6(모션)/l8(이음새 ΔE) 신설. **V32 = 90/100, L10, 전송 승인** (l1~l10+icons+common 전부 PASS, l11만 SKIP).

### 2.4 남은 천장
L11~L13(하드웨어 게이트: PC 네이티브 해상도 출력 + 실제 Claude Code 세션을 Windows Terminal 창에 띄움) — 코드로는 더 못 올림, 박씨의 물리적 환경 조치 필요.

---

## 3. 판서 튜토리얼 (`po-tutorial`, 트랙 B, `mcp_tutorial/`)

### 3.1 V25 시리즈 — 라이트릭/필름스트립 버그 사냥 (2026-08-30~31)
- **V25F1**: 결정론 스크롤 기반 전환(Playwright 실시간 스크롤 + 웨이포인트 카메라 + 왈츠 숨쉬기 ±8px)
- **V25F2**: 상단 베젤(30px 다크+골드 핀스트라이프+카메라노치) 고정 레이어
- **V25F3**: 필름 스트립 스크롤 애니메이션(톱니구멍+골드엣지)
- **V25F4**: 마이크로 파즈(정보밀도 높은 구간에 150ms 무음 삽입, 꼬리 회수로 총길이 불변)
- **V25F5**: **근본원인 발견** — PIL `ImageDraw.line`이 RGBA에서 블렌딩이 아니라 SET이라 반투명 라이트릭이 필름스트립/골드엣지를 통째로 덮음. 별도 레이어+`alpha_composite()`로 수정.
- **V25F6~F7**: 우측 엣지만 100↔147로 깜빡이는 잔류버그, 2차례 끝점 보정 시도 실패
- **V25F8 (★최종해결)**: **ffmpeg bilinear 재현이 원인** — 다운스케일 좌표가 정수가 아니라 x=512.75를 샘플링해 엣지 옆 버퍼 픽셀이 리크에 절반 가중으로 섞임. 끝점을 2px 더 밀어(511) 버퍼+엣지 모두 보호. 8구간 실측 전부 상수값 확인, 최종 완성.

**V25F8 스펙**: square 1080×1080·25fps·49.2s, edge-tts InJoon→humanizer→RVC parksy_rvc_v3 key -6, 마이크로파즈 3곳, 스텝배지+판서9개(Excalifont)+상단베젤+라이트릭.

### 3.2 다음 방향 — 태블릙 실황 도입 (2026-08-31~)
박씨 지시: 모의 그래픽은 아무리 다듬어도 "합성 티" — 태블릿 실제 화면(Native screenrecord)이 "압도적 신뢰도의 진짜 시연". 트랙B는 실 브라우저의 CSS 3D/모달/터치리플/관성스크롤을 네이티브로 담고, 더빙 쉼표+클릭 foley를 실 프레임 타임코드에 연동.
- 자체 판정(2026-08-31): V25F8 = 75/100 (컴파일95·나레이션85·연출75·**진정성40**)
- 실행 상태: 태블릿 Stage 확인(100.86.15.50:5900, 1600×2560, Termux+Chrome 설치 확인) 완료.
  `tut_tabcast.py`(트랙B 전용, bigtech v18_tabcast와 자산 공유 금지) 미착수 — **다음 세션 시작점**.

---

## 4. 박씨 티칭 (`parksy-teaching`, PO-250901-01, 트랙 C)

### 4.1 핵심 명제
> 비개발자 교육자(교사·은퇴 시니어)가 태블릿 1대 + ₩3만 블루투스 클리커로, URL 페이지 보며
> 오른손 S Pen 판서 + 왼손 클리커로 방송효과를 라이브로 치며 강의를 녹화하면, 그 파일이 곧 완성본.
> PC·서버·편집SW·설치앱 없음. 강의 제작을 "후반작업 스킬(관문)" → "라이브 퍼포먼스 스킬(누구나 오후 한나절)"로 이동.

### 4.2 아키텍처 — "단판(單板)" 패턴
```
[3] Parksy Axis(방송효과 FSM, :8492 소켓) ─┐
[2] Parksy Pen(S Pen 판서 오버레이)        ├─ 태블릿 윈도우 컴포지터가 합성
[1] Chrome(teaching-stage.html, __bcast)  ─┘
    ↓
삼성 네이티브 레코더 → take.mp4 (외부장비 0)
```
컨트롤 평면 = OS 프리미티브만(`/dev/input` getevent + `am` broadcast + localhost 소켓) — 설치앱·접근성서비스·root 불필요.

**순수 신규 컴포넌트 3개만**(나머지는 기존 6개 엔진 재조립): ① 온디바이스 getevent 디스패처(`teach_dispatch.sh`) ② 큐마커 스키마 ③ `__bcast` 실시간 인포그래픽 엔진(서버 없이 NodeCG/Singular 패턴 — 개표막대·차트·지도·결과판·라이브데이터피드).

### 4.3 버전 이력
- **V0**: 스캐폴드(툴 2개, recipe.schema, 문서 10종) — MCP 등록 완료
- **V1**: `teach_dispatch.sh` 코딩 완료, TabMate 절전으로 실측 대기
- **V1.2**: `assemble.py`(P2크롭~P5loudnorm) 합성테이크 E2E 통과
- **V2.0**: `__bcast` 엔진(23KB) 발행 완료, APK 터미널 제어 배선
- **V3.2 (09-06)**: Docker 패키징(3 OS/3레이어 어디서든 같은 이미지 지향) — Dockerfile+entrypoint+compose. WSL에 docker 미설치라 문법검증(`py_compile`/`bash -n`)까지만, 최초 빌드는 미니PC 대기.
- **V3.3 (09-06/07)**: 자율주행 사이클 —
  - "칠판=변수" 실증: `dummy_take.py --url <임의URL>` 경로 추가, 레시피 없이 홈페이지 자체를 런타임 변수로 주입 가능
  - `--snap`(캡처 전후 스크린샷)으로 **에이전트 비전 검증 루프** 구축, 실제로 무대 로드 확인
  - **APK 통합 블로커 2건 발견**: ① `kr.parksy.axis`의 :8492 소켓이 "방송모드 진입시에만" 열리는 구조로 추정(MainActivity 상태에선 LISTEN 안함) ② `com.dtslib.laser_pen_overlay/.OverlayService`가 `exported=false`라 `adb shell am start-service`가 Permission Denial — **박씨가 만든 APK 쪽 수정 필요**(exported=true+액션가드 또는 자동화 전용 리시버).

### 4.4 자가채점 (V5 기준)
아키텍처 9/10 (개념독창성9·재사용레버리지9·트랙경계/감옥원칙9·ADB오케스트레이션9·live-to-tape정합9). 코드는 전부 존재, 실기기 게이트 4개(TabMate키맵/Axis소켓/삼성레코더캡처/오버레이5분안정성) 미측정 — 전부 폴백 있어 사망경로 없음.

### 4.5 남은 액션
1. (박씨, 물리) 태블릿 충전+화면ON+TabMate 깨우기
2. (박씨) Pen OverlayService exported 처리 또는 자동화 리시버 결정
3. Axis 방송모드 진입 조건(어떤 intent가 :8492를 여는지) 파악
4. 오버레이 스택 5분 안정성 게이트

---

## 5. 크로스 MCP 공통 인프라

| 항목 | 값 | 비고 |
|---|---|---|
| RVC 모델 | `parksy_rvc_v3` | key: deepfake=-6(2026-09-08 수정 전 0), tutorial=-6, teaching=실음성(RVC 미적용) |
| f0_method | rmvpe / index_rate 0.6 / protect 0.33 / rms_mix_rate 0.25 | 전체 통일 |
| 감옥 원칙 | MCP당 툴 2개(액션+탈출구), 3개째 금지 | 4개 MCP 전부 준수 |
| 헌법 준수 | ADB 체인/headless 우회 죽은 패턴 금지, ADB는 하드웨어 접근 전용 | V24 Grok 개념컷에서 실제 준수 확인 |
| loudnorm 목표 | I=-14 LUFS, TP=-1dBTP (빅테크는 -13.7/-2.0) | — |

---

*작성: Claude Sonnet 5 · 2026-09-12 · 소스: 각 MCP DEVLOG.md/WHITEPAPER.md 원문 직접 열람, 커밋해시·실측수치 원문 그대로 인용*
