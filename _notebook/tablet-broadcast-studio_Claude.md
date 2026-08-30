---
date: 2026-08-18
agent: Claude Code (출판부 · 번역 수호자)
mark: _Claude
type: plan
status: active
source: dtslib1979/dtslib-papyrus (허브) + _notebook/99-devlog.md:6365~6431 Boss 방향
related:
  - tablet-setup-parksy-method_Claude.md
  - session-2026-08-18_Claude.md
---

# 태블릿 교육방송 스튜디오 — 서플라이 체인 (확정)

> Boss 방향 정리본. 태블릿(Tab S9)의 정체·역할·서플라이 체인을 한 장으로.
> **상태: 계획(planned). 아직 중앙 허브(fork)는 만들지 않음 — 수첩에만 저장.**

---

## 0. 한 줄

**태블릿 = "교육방송 스튜디오".** **proot Ubuntu = 연산센터(렌더·믹스 계산).** Boss가 폰(음성)으로 만든 드래프트를 받아 → 그림·음악 자산을 합성·렌더·믹스 → 교육방송 채널로 최종 업로드하는 방송국.

---

## 1. 태블릿 정체 (확정)

| 항목 | 값 |
|------|-----|
| 디바이스 | Tab S9 · One UI 8.5 · Android 16 (OS 동결) |
| 감각 노드 | 손(SPen/터치/그림) · 11" 화면 |
| 세계 역할 | 확장형 워크센터 = **교육방송 스튜디오** |
| Google/Samsung | `thomas.tj.park@gmail.com` |
| GitHub | `dimas-40` |
| **출력 채널** | `@BeingEduartEngineer-4` (eae.kr) · `@EAE-University` (eae-univ) |
| **GitHub 레포** | `eae.kr` · `eae-univ` (+ 입력 `parksy-audio` · `parksy-image`) |
| 구축 순서 | 노드② "첫 이식(n=1→n=2 증명)" |

---

## 2. 3단계 방송국 로드맵 = 3계정 (이미 정렬돼 있음)

| 단계 | 방송국 | Google 계정 | 실제 채널 (channels.json) |
|------|--------|-------------|---------------------------|
| **1 (지금)** | **교육방송** | **thomas.tj.park** | **@BeingEduartEngineer-4 · @EAE-University** |
| 2 | 아리랑·KR 메리트 | dimas.thomas.sancho | 박씨 5채널 (@blogger/@musician/@visualizer/@technician/@philosopher-parksy) |
| 3 | 경제방송 (친구 비즈니스) | dtslib1979 | 경제방송 6채널 |

> channels.json의 계정 메모가 증거: A="KR 방송 5채널" · B="경제방송 6채널" · C="교육방송 2채널".
> → thomas.tj.park = 교육방송(1단계)이 맞고, 태블릿에서 시작하면 로드맵 1단계와 정확히 일치.

---

## 3. 서플라이 체인 (fork 모델)

```
dtslib1979 (뇌 · 원조/SSOT)
   │  fork (필요한 레포만)
   ▼
dimas-40 (태블릿 스튜디오 = fork들)
   │  렌더 + 믹스 + 업로드
   ▼
thomas.tj.park YouTube (교육방송 채널)
```

**fork = parksy 루프의 GitHub 네이티브 구현:**

| parksy 루프 | fork로 구현 |
|---|---|
| **⑤ 선물** (검증된 것 → 워크센터) | `git pull upstream` (dtslib1979 → dimas-40 fork) |
| **① 미러** (워크센터 실측 → 뇌) | PR (dimas-40 fork → dtslib1979 upstream) |

> "연동" = upstream으로 물려 있는 fork. 선물은 pull, 실측은 PR.

---

## 4. 출판 모델 — 서브 레저(비공개) / 레저(티스토리 투트랙)

> Boss 결정 (2026-08-18): **여기(태블릿)는 출판이 아니다 → GitHub Pages로 홍보할 이유가 없음.**
> **월 ~4000원 계정(GitHub Pro) 결제 → 소스 코드 비공개.**

| 트랙 | 위치 | 개념 | 공개 |
|------|------|------|------|
| **서브 레저** | GitHub (private) | 소스 코드 · 구현 상세 | ❌ 비공개 |
| **레저** | 티스토리 (투트랙) | 교재 · "잘난 척" 쇼오프 웹페이지 | ✅ 공개 |

- **원칙:** 소스는 비공개(서브 레저). 공개는 "교재/쇼오프 페이지"를 만들 때만, 티스토리로(레저).
- **GitHub Pages 배포 안 함** — 태블릿 레포는 홍보 채널이 아님.
- **fork 명령:** `--private` (S21의 `--public`과 반대). GitHub Pro($4/월)로 비공개 + Actions.
- **출판부 게이트(build_webzine/gap_count)는 S21(helena751107) 공개 Pages 전용** — 태블릿은 티스토리 투트랙이라 해당 없음.

---

## 5. fork할 레포 — EAE 5개 (확정 · 2026-08-18)

> 시리즈 이름: **EAE = Edu Art Engineer** (에듀·아트·엔지니어).

| 새 repo (dimas-40) | fork 원본 (dtslib1979) | 역할 | 공개 출력 |
|---|---|---|---|
| **eae-music** | parksy-audio | 음악 스튜디오 | Tistory + Pages (방법론) |
| **eae-image** | parksy-image (2D 분리) | 웹툰/이미지 스튜디오 | Tistory + Pages (방법론) |
| **eae-video** | parksy-image (방송 분리) | 영상 스튜디오 | Tistory + Pages (방법론) |
| **eaekr** | eae.kr (구분자 제거) | 방송 채널 | YouTube @BeingEduartEngineer-4 |
| **eaeuniv** | eae-univ (구분자 제거) | 방송 채널 | YouTube @EAE-University |

- **parksy-image는 "2D 이미지 + 방송"이 섞여 있음 → eae-image / eae-video로 스플릿.**
- **전부 `--private`** (GitHub Pro $4/월).
- **스튜디오 3개**(eae-music·image·video) = 방법론 → Tistory + GitHub Pages **투트랙 페어 공개**.
- **채널 2개**(eaekr·eaeuniv) = YouTube 직접 송출.
- **구분자 제거**(eae.kr→eaekr, eae-univ→eaeuniv) = fork 원본과 헷갈림 방지.
- 뇌(dtslib-papyrus)는 fork 안 함 — upstream 레퍼런스로만 남음.

### 방송국 부서 구조 (확정 · 2026-08-18)

- 5개 repo = **방송국 부서**: 음악(eae-music) · 이미지(eae-image) · 영상(eae-video) · 방송(eaekr) · 사내대학(eaeuniv).
- 각 부서 콘텐츠는 **dtslib1979의 콘텐츠 repo**(parksy-audio·parksy-image)로 연결 — 콘텐츠 생기면 연결 (설정 보류).
- PWA installable (manifest standalone + 파비콘/아이콘) · 서비스워커 없음.

### 티스토리 블로그 매핑 (확정 · 2026-08-18)

| repo | 티스토리 | GitHub Pages |
|---|---|---|
| eae-music | eae-music.tistory.com | dimas-40.github.io/eae-music |
| eae-image | eae-image.tistory.com | dimas-40.github.io/eae-image |
| eae-video | eae-video.tistory.com | dimas-40.github.io/eae-video |
| eaekr | eae-broadcast.tistory.com | dimas-40.github.io/eaekr |
| eaeuniv | eae-kr.tistory.com | dimas-40.github.io/eaeuniv |

> 매핑 확정 (제목 기준): eae-broadcast("broadcast")↔eaekr(교육방송국), eae-kr("univ")↔eaeuniv(사내대학).

### 티스토리 스킨 적용 — 완료 (2026-08-18)

- **정답 흐름:** `renew_sessions.py`(기기 위 headless, 1회 로그인→쿠키 저장) → `batch_apply.py`(저장된 세션으로 스킨 일괄 적용). 쿠키 붙여넣기·헤디드 뷰어(xvfb/VNC) 불필요.
- **함정:** TSSESSION은 세션쿠키(expires=-1) → 재실행 시 유실. `apply_skin.py`/`batch_apply.py`가 expires+7일 보정 내장.
- **결과:** 5개 블로그 전부 pg_Whatever + skin-premium.css + 레이아웃 주입, 검증(마커) 통과.
- **주의:** 로그인은 CI에서 하지 말 것(IP 다름→봇감지). 기기(proot)에서 headless가 정답. captcha 뜨면 그때만 `--headed`.

---

## 6. 입력 2 + 출력 1 구조 (레인이 아니라)

```
입력① 그림 (스케치→Grok)  ─┐
                          ├→ 교육방송 영상 (화면녹화→렌더+믹스) → @BeingEduartEngineer-4
입력② 음악 (MIDI→렌더)    ─┘
콘텐츠 드래프트: Boss가 폰(음성)으로 (웹페이지 등)
```

- 그림·음악은 **채널이 아니라 교육방송의 입력 자산** → 채널은 교육방송 2개뿐.
- 태블릿 = 스튜디오(렌더+믹스+업로드). 드래프트 작성은 Boss 폰 담당.

### 음악 파이프라인 (오프라인 렌더 모델)

| 단계 | 하는 일 | 상태 |
|------|---------|------|
| M0 | 작곡 — 에이전트(DeepSeek)+`mido`로 MIDI 생성 | 신규 |
| M1 | 가상악기 렌더 — FluidSynth/SunVox/ZynAddSubFX → MIDI→WAV | ✅ aarch64 |
| M2 | 가창 — RVC(기존) + DiffSinger(가창 합성) | ⚠️ DiffSinger aarch64 미실측 |
| M3 | 믹스/마스터 — ffmpeg + sox | ✅ S21 증명 |
| M4 | 전달 — tg.sh → 텔레그램 → 네이티브 플레이어 청취 | ✅ |
| M5 | 발행 — 곡 → parksy-audio → 채널 | 재사용 |
| M6 | 공급 — BGM → PD P5 sidechain 입력 | ✅ P5 있음 |

---

## 7. 경계선 (하면 안 되는 것)

| 항목 | 판정 | 이유 |
|------|------|------|
| S21(helena751107) 복제 | ❌ 금지 | 자기 정체로 새 방 (devlog 6431) |
| 로컬 GPU 이미지 생성 | ⏸ 보류 | proot(glibc)↔bionic ABI 벽 — 태블릿도 동일 |
| 실시간 DAW(저지연) | ❌ 안 함 | 오프라인 렌더 + tg 청취로 우회 |
| 이미지 생성 | ☁️ 클라우드(Grok) | CPU 무관 |
| 영상 렌더 | 💻 CPU(ffmpeg) | CPU로 충분 |
| NPU/NNAPI 가속 | ⚠️ 재실측 | Snapdragon Hexagon은 S21(Exynos)과 다른 부품 |

---

## 8. 다음 행동 (팬딩)

- [x] **repo 5개 껍데기 생성** (`--private` + Pages 액션 배포 연결) — eae-music · eae-image · eae-video · eaekr · eaeuniv (✅ 2026-08-18, GitHub Pro 반영)
- [ ] **fork 콘텐츠 pull**: dtslib1979에서 소스·스크립트 가져오기 (parksy-audio→eae-music 등)
- [ ] **parksy-image 스플릿**: 2D 이미지 → eae-image, 방송 → eae-video
- [ ] **SSOT 교체**: owner=dimas-40 · identity=thomas.tj.park · repos=위 5개(비공개) · channels=교육방송 2개 · tistory=eae-kr 등
- [ ] **스모크 테스트**: parksy-audio fork → FluidSynth MIDI 1곡 → WAV 렌더 → tg 전송 (하루 증명)
- [ ] RVC 붙이기 → DiffSinger aarch64 실측은 맨 뒤
- [ ] 앱 동결: S21 검증 Termux APK 사이드로드 (F-Droid 최신 아님)
- [ ] 8/20 보안패치 스킵 확인

## 9. Boss 확인 필요 (정체 값)

- [ ] 태블릿 정체명(person_name/tagline) — "자기 정체로 새 방"이라 Boss 지정 대기
- [ ] "피르트 5분투"(STT 음차) = "첫 5분"(퍼스트 5분)으로 해독 — 태블릿 에이전트가 첫 5분에 읽을 온보딩 카드. 확정 시 본문에 반영.
