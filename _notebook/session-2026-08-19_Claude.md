---
date: 2026-08-19
agent: Claude Code (출판부 · 상주)
mark: _Claude
type: session
status: active
related:
  - session-2026-08-18_Claude.md
  - tablet-broadcast-studio_Claude.md
  - 83-momentum-2026-08-14_Grok.md
  - 102-tablet-hw-parse_Grok.md
---

# 세션 회의록 — 판의 전환 · 오버레이 키트 + 런타임 후보정 (2026-08-19)

> 오늘 대화의 핵심을 한 장으로. 두 트랙 웹페이지의 원본.
> 인터랙티브 관계도: [`session-2026-08-19-graph.html`](../notebook/session-2026-08-19-graph.html)

---

## 0. 한 줄

```
옛날: 사람이 GUI 앱(APK/PWA)을 클릭해서 수작업 → 매끈한 자동화는 오히려 기계 같음
지금: AI 디렉터(Claude Code + Grok)가 CLI에서 판을 짜고, APK를 "사람 손"처럼 조작
목표: "AI를 쓰되 AI 같지 않은" 연출 — 진짜 사람이 실수하면서 만든 것처럼
```

오늘 대화는 **판(보드)이 뒤집히는 전환점**이었다. 이전까지 태블릿의 영상 일은 "숏폼 공장(eae-video)" 하나로 봤는데, 오늘 Boss가 그 아래 깔린 **진짜 그림**을 꺼냈다.

---

## 1. 시간순 흐름

### ① 업무 수첩 리마인더 — 우리 어디까지
태블릿(Tab S9 · dimas-40) = **교육방송 스튜디오**. 5개 EAE 레포 생성 완료, Claude(상주 $0)=공장 80% / Grok($30)=천장 20% 분담이 `STUDIO.md`에 **잠금** 상태. 다음은 D0(스캐폴드 → 자산 이식 → 파일럿 ep01).

### ② 티스토리 자동화 리뷰
티스토리 Open API는 죽었다(2024-02). 그래서 **스킨 자동화**(리버스엔지니어링한 숨은 API `html.json`/`set.json`) + **Paste Pipeline**(사람 복붙)으로 갈랐다. 글 발행은 사람, 포장(스킨)은 로봇.

### ③ bayaba 이식 사고 분석 + 지침 전송
친구(딥시크 에이더)가 카카오 지도 캡차를 OCR/xvfb로 풀려다 막힘. **근본 오판 = "사람 게이트(캡차)를 기계로 뚫으려 함."** 정답은 로그인 1회(사람) → 이후 자동. 만회 지침 `bayaba-tistory-recovery.md` 작성 → 텔레그램 전송.

### ④ 태블릿 전용 보고 봇
`@dtslib_tablet_bot` 생성. 태블릿의 모든 보고는 **이 한 채널로만** (S21의 @S21Phone_Bot과 분리).

### ⑤ eae-video 구조 + 강의 후보정
eae-video는 지금 "설계만 있고 빈 껍데기". 숏폼(한 렌즈 한 무브) 전용이 아니라 **강의 영상 후보정**도 넣어야 한다는 Boss 방향.

### ⑥ 두 레포 파싱 — 오버레이 키트 + 런타임 후보정
- `dtslib-apk-lab` → **오버레이 키트 APK** (parksy-axis · laser-pen-overlay · parksy-studio)
- `dtslib-cloud-appstore` → **런타임 브라우저 후보정** (lecture-long · lecture-shorts)

### ⑦ 판의 전환 (오늘의 핵심)
옛날 이 앱들은 **AI 없이 사람이 GUI를 클릭**하던 시대의 산물. 지금은 CLI에서 AI가 디렉터, Android 브릿지로 장치·저장소 왕복.

### ⑧ 최종 원칙 확정
**"AI를 쓰되 AI 같지 않게."** FFmpeg는 너무 매끈하고 기계 같다. 진짜 사람이 실수하며 움직이는 것처럼 보이려면 오버레이 키트 APK를 터미널에서 조작해야 한다.

---

## 2. 최종 아키텍처 — 3층 (확정)

```
목표 = "AI를 쓰되 AI 같지 않은" 연출 (진정성이 해자)

AI 디렉터 (Claude Code + Grok)
   │  판을 짜고 세 판을 지휘
   ├─ ① APK 오버레이 키트   = "사람 손"   (터미널 조종 → 인간 같은 실시간 움직임)
   ├─ ② 브라우저 런타임      = "빌린 연산"  (공짜 + GPU로 태블릿보다 빠름)
   └─ ③ FFmpeg (proot)      = "접착제"    (이어붙이기·인코딩·자막만)

진짜 육성 녹화 = Boss 직접 (필요할 때 라이브)
```

### 2버킷 (시점으로 분리)

| 버킷 | 시점 | 실행층 | 자산 |
|------|------|--------|------|
| **방송 효과 오버레이 키트** | **녹화 중** | APK (온디바이스) | parksy-axis · laser-pen-overlay · parksy-studio |
| **후보정 (프로 마감)** | **녹화 후** | 런타임 브라우저 (FFmpeg.wasm/WebCodecs) | lecture-long · lecture-shorts |

### 브라우저 런타임의 진짜 이유 (정정)
"ffmpeg 없어서"가 아니라 **공짜 플랫폼 API + 브라우저 GPU(WebCodecs)를 빌려 태블릿 CPU 한도보다 빠르게** 돌리는 전략. 우회가 아니라 **연산 아웃소싱** (Vercel $0).

### APK를 터미널에서 조종하는 근거 (이미 뚫려 있음)
| APK | 에이전트 조종 통로 |
|-----|-------------------|
| parksy-axis | 설정 파일 `/data/data/kr.parksy.axis/files/axis_overlay_config.json` 직접 쓰기 |
| parksy-glot | `PC glot.py (Web Speech) + WebSocket → WebView` |
| laser-pen-overlay | `TouchInjectionService.kt` (터치 주입) |
| 일반 | proot ↔ Android 브릿지 + adb/Shizuku |

---

## 3. 자산 지도 (파싱·이식 완료 → `_import/`)

| 레포 | 자산 | 정체 |
|------|------|------|
| dtslib-apk-lab | `parksy-axis` v11.1 | 방송 단계 오버레이 (FSM, 6테마, 4방향) |
| | `laser-pen-overlay` | S Pen 판서 오버레이 (stylus/finger 패스스루) |
| | `parksy-studio` | **방송 스튜디오 전체 APK** (녹화+카메라오버레이3종+BGM+트리머+cloud-appstore 런처) |
| | `parksy-glot` | 자막 오버레이 (WebSocket) |
| dtslib-cloud-appstore | `lecture-long` v4.0 | 강의 롱폼 후보정 (16분→12분, FFmpeg.wasm) |
| | `lecture-shorts` v2.2 | 강의→숏 (9:16, WebCodecs 10~30x) |

핵심 발견: **`parksy-studio`가 이미 "녹화 → 트림(FFmpeg HW) → cloud-appstore 런처"로 두 버킷을 연결**하고 있었다.

---

## 4. 결론 — 설정이 아니라 실행층이 바뀐다

| | 옛날 | 지금 |
|---|---|---|
| 디렉터 | Boss 손 | **AI 디렉터** |
| 실행층 | APK/PWA GUI | **CLI + FFmpeg 스크립트** |
| 오버레이 조작 | 사람 손가락 | **AI (파일·WebSocket·터치주입)** |
| 후보정 연산 | 태블릿 CPU | **브라우저 GPU 빌려쓰기** |
| 매끈함 | 목표 | **피할 것 — 사람 흉내가 목표** |
| 육성 | 항상 | 필요할 때 Boss 라이브 |

---

## 5. 다음 행동 (팬딩)

- [ ] 에이전트→APK 조종 프로토콜 확정 (axis 설정파일 vs glot WebSocket 표준)
- [ ] 오버레이 키트 APK → 온디바이스 도구 슬롯 (eaekr 또는 별도 tools/)
- [ ] 브라우저 런타임 vs FFmpeg 사용 경계 확정
- [ ] lecture-long/shorts 마감 규격 → eae-video `config/post/` 규격서
- [ ] 태블릿 ffmpeg 설치 (접착제용)

*회의록 · agent mark `_Claude` · 2026-08-19 · 관계도: `session-2026-08-19-graph.html`*
