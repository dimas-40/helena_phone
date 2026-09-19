---
date: 2026-09-12
agent: Claude Code (출판부 · 양산 · 폰 워크센터 공장장)
mark: _Claude
type: session-note
status: active
related:
  - session-2026-08-22_quota-channel-map_Claude.md
  - session-2026-08-22_youtube-oauth_Claude.md
  - 108-content-semiconductor-architecture_Claude.md
  - 109-content-fab-implementation-plan_Claude.md
---

# 신개념 잡지 루프 + 유튜브 채널 리네임 수습 + SSOT 단일화 결론 (_Claude · 2026-09-12)

> **Boss 지시 흐름:** parksy-webzine(신개념 잡지) → 유튜브/티스토리 연결 확인 → 채널 리네임 발견·수습 → "공통 SSOT 하나 + 역할 분리" 확정 → 세션 저장.
> **핵심 성과:** @justino-fashion→@Parksy-webzine 반쪽 리네임을 폰·파피루스 양쪽 SSOT에서 수습. 유튜브 레인은 GCP OAuth 수동 발급만 남음.

---

## 1. 한 줄

parksy-webzine = **신개념 잡지** (웹진=눕다 → YouTube=세우다 → 티스토리=루프 → 다시 웹진).  
이번 세션에서 **유튜브 채널이 @justino-fashion → @Parksy-webzine 로 리네임된 것(동일 채널 ID)을 발견**했고, 반쪽 리네임(레포만 바뀌고 핸들 미반영)을 폰 ecosystem.json + 파피루스 SSOT 양쪽에서 수습했다.  
결론적으로 **유튜브 레인은 GCP OAuth 클라이언트 ID/시크릿 발급 1회만 남았다.**

## 2. 핵심 발견 — 유튜브 채널 리네임 (반쪽 리네임)

- **채널 ID `UCRJsaNvt9tQtOJ1tZ-_T3Yg`** = 예전 `@justino-fashion`, 지금 `@Parksy-webzine` (핸들만 바뀜, ID 동일 — 실측).
- 파피루스 SSOT는 최근 2커밋(`73348f5`/`226cb2e`)으로 **레포명 justino→parksy-webzine만** 갱신하고, **채널 handle은 `@justino-fashion` 그대로** 남겨둔 반쪽 리네임 상태였음.
- 폰 ecosystem.json도 같은 패턴: key만 "parksy-webzine"으로 바꾸고 handle/topic은 저스틴(쇼핑몰·크리에이터) 그대로.

## 3. 수습한 것 (SSOT 정합 — 양쪽 다)

### 폰 /root/work (helena_phone)
- `configs/ecosystem.json` — `identity.sameAs`·`channels.handle(@Parksy-webzine)+topic(잡지·웹진)`·`repos.channel` 3곳 교정.
- `tistory-naver/apply_geold.py` — `kr-merit-aggro → ("parksy 편집강박", "parksy-webzine", "@Parksy-webzine")` + sameAs.
- `tistory-naver/accounts.json.template` — `unit: justino → parksy-webzine`.
- `CONSTITUTION.md` — YouTube 6 목록 `@justino-fashion → @Parksy-webzine`.
- 180개 `*.html` — `build_webzine.py` 재생성 → GEO 스탬프 전부 @Parksy-webzine.
- 검증: `load_ecosystem.py --check` → **✅ 정합** (`parksy-webzine → kr-merit-aggro → @Parksy-webzine`).

### 파피루스 SSOT (/root/papyrus)
- `@justino-fashion → @Parksy-webzine` 핸들 일괄 (활성 SSOT/config 10파일): `hq/config/channel-repo-map.json`(+draft)·`hq/TISTORY-ENDPRODUCT-MAPPING`·`tools/youtube/accounts/channels.json`·`tools/mcp_distributor/channel_map.json`·`configs/ecosystem.json.template`·`CLAUDE.md`·`youtube-data.json`×2·`channel-repo-map.html`.
- 커밋 **`af5d063`** → push (226cb2e..af5d063).
- 히스토리 문서(docs/dev-logs·infra-history·mcp-semicon 등 11개)는 날짜 기록이라 보존.

## 4. 채널 키 stale 수습 (PC 세션 SSH로 완결 — 내 실측 컨펌)

- `yt_upload.py`: `--channel` 기본값 `main`→`branch`, `CHANNELS['main']`→`CHANNELS["branch"]` (3곳) + docstring/주석 정리.
- `yt_geo_origin.py`: `main/phone`→`list(Y.CHANNELS.keys())` (14/107/113줄), `--channel all`이 6채널 전부 순회.
- 검증: `main/phone` 잔재 0건, `--help`에 6채널 키(branch·phoneparis·alexandria·artrew·parksy-webzine·espiritu) 정상 노출, 두 파일 `ast.parse` 문법 OK.
- **미커밋 상태** (워킹트리만, ` M yt_upload.py / yt_geo_origin.py`).

## 5. 신개념 잡지 루프 (parksy-webzine)

- **루프:** 웹진(눕다) → YouTube(세우다) → 티스토리(루프) → 다시 웹진. + 웹툰(곁, 자산 맞을 때).
- 랜딩: 16타이틀×4호=**64권** 캐러셀 + 히어로 영상. 이번 세션에서 **다크그린+썩은나무 테마** 적용, **선반 판 88px→30px** 축소.
- **Content FAB**(`mcp__content-fab__*`): 5 Division(memory/logic/analog/discrete/power) × 4 Product — `publishing`=implemented(BOM+RECIPE-001), `video`=**빈 BOM·레시피**, `audio`/`education`=planned.
  - publishing RECIPE-001: build_webzine → check_webpages → publish_route → publishing_metrics → publish.py tistory.
- **남은 루프 완성 = Content FAB `video` 제품 등록** (유튜브 레인이 공장에 안 들어옴) — 다음 단계.

## 6. 출판 생태계 인벤토리 (실측 컨펌)

- **2계층 런타임:** Termux 네이티브(상시: sshd/crond/boot) + proot Ubuntu(무거운 파이프라인).
- proot: Python 3.14.4 · torch 2.14.0+cpu · googleapiclient/google-auth-oauthlib/playwright 설치됨.
- Termux:Boot **8종** · 위젯 13개(.shortcuts/) · crond 상시.
- `scripts/` **84개** · `mcp-servers/` **5종**(parksy_scm/rawmat/law + eae_platform/writer) · `tistory-naver/` 38개(2레인 완성) · `/root/work` 845M.
- **온디바이스 AI(GB급):** parksy_tts_phone 1.7G · hf_chatterbox 912M · parksy_int8 810M · parksy_genie_onnx 324M · rvc-webui 537M · GPT_SoVITS 471M · libonnxruntime_qnn.so(NPU 흔적).

## 7. OAuth 구조 (검증 완료)

- **3층위:** GCP 프로젝트+OAuth클라이언트(앱) / 구글계정(로그인) / 유튜브채널(브랜드계정).
- ecosystem.json `youtube.accounts` = **dtslib1979@gmail.com 1개만** (b계정). 6채널 전부 이 계정 밑 브랜드.
- **클라이언트 ID 1개**, 계정별 승인만 따로(테스트유저 최대 100명, 앱 검수 불요).
- **⚠️ 쿼터 = 프로젝트 단위 공유** (계정 단위 아님): 기본 10,000유닛/일, `videos.insert`=1,600유닛 → **업로드 ~6개/일 합산**. 계정별 독립 쿼터 원하면 계정마다 별도 GCP 프로젝트.

## 8. 결론 — SSOT 단일화 + 역할 분리 (Boss 확정)

> **"전체 로드맵 하나를 갖고, 서로 엉키지 않게 공통 환경 세팅 후 역할 배정."**

- **공통 환경(셋이 똑같이 참조):** SSOT 하나(dtslib-papyrus) + 스크립트 인터페이스 규약 + git 신원.
- **역할 분리:** 폰=proot 실제 실행(퍼블리싱·크롤링·온디바이스 TTS·24/7) / WSL=코드 개발·다레포 광역 / 미니PC=딥시크 담당.
- **오늘 사고 원인:** papyrus SSOT ↔ 폰 ecosystem.json SSOT가 **따로 놀아서** 채널키 불일치 발생. SSOT를 한 레포로 단일화하고 폰/WSL이 git pull로 참조하면 구조적으로 재발 없음.
- **내 역할 = 폰 워크센터 공장장** (실행·양산·SSOT 정합 감시).

## 9. 남은 갭 / 다음 액션

| # | 항목 | 상태 | 담당 |
|---|------|------|------|
| 1 | GCP OAuth 클라이언트 ID/시크릿 발급 | ❌ 유일한 병목 (`.secrets.env` YOUTUBE_* 전부 `""`) | Boss 수동 1회 |
| 2 | yt_upload/yt_geo 채널키 수정 커밋 | ⚠️ 워킹트리만 (미커밋) | Claude |
| 3 | Content FAB `video` 제품 BOM+레시피 등록 | ⬜ 루프 완성 조건 | Claude |
| 4 | parksy-webzine 레포 정리(justino/obokzip 잔재) + LOOP.md | ⬜ 승인된 플랜 (중단됨) | Claude |
| 5 | SSOT 단일화(papyrus) + 폰/WSL git pull 참조 구조 | ⬜ 구조 개편 | Boss+Claude |

## 10. 참조

- parksy-webzine: `00_TRUTH/HOUSE.md`(원장) · `FACTORY.json` · `/root/work/parksy-webzine/`
- SSOT: papyrus `hq/config/channel-repo-map.json` · `hq/TISTORY-ENDPRODUCT-MAPPING-2026-08-22.md`
- 폰 SSOT: `configs/ecosystem.json`(gitignore 로컬) + `configs/ecosystem.json.template`

*agent mark `_Claude` · 2026-09-12*
