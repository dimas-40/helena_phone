# 🏭 공장 캐파시티 & IT 능력 인프라 — 재고 조사

> 기준일: **2026-09-05** · `_Claude` · profit-center 저장
> 성격: 공장(IT 베이스라인)의 현재 캐파시티 전수. **설비는 계속 증설 → 기준일 갱신 + 증설 이력 로그 유지.**
> 출처: papyrus `mcp-semicon` 실측(04-17) · `PO-MKT-001-result.md` · `REPOSITORY_TREE.md` · CLAUDE.md

---

## 1. 공장 규모 — 레포 인프라

### 계정별 (실측 2026-09-04)
| 계정 | 레포 수 | 성격 |
|------|--------|------|
| dtslib1979 | 28 | 본사·방송·스튜디오·브랜치 (26 private + 2 public) |
| dimas-40 | 6 | eae-* 교육 계열 + helena_phone |
| helena751107 | 5 | 누나 퍼블리싱 (전부 public) |
| **합계** | **39** | |

### FAB 실측 캐파시티 (2026-04-17, mcp-semicon)
| 자산 | 수치 |
|------|------|
| 데이터 총량 | **140GB** (레포 26.8GB + 외부 에셋 113.3GB) |
| 코드 | 673,861 LOC · 커밋 6,800+ |
| 글 | 3,529,312 단어 (단행본 44~70권 분량) |
| MD 문서 | 12,740개 (parksy-logs 11,699 포함) |
| WAV | 763 · MIDI 1,043 · 이미지 500+ |
| JSONL | 18개 · 82,211줄 |
| AI 모델 | 9버전 · 라이브 도메인 14 · MCP 2(20도구) |

### 레포 캐파시티 상위 (용량·커밋)
| 레포 | 용량 | 커밋 | 역할 |
|------|------|------|------|
| parksy-audio | 986MB | 401~476 | 오디오/MIDI 파이프 (유일 완성형) |
| parksy-image | 863MB | — | 이미지·영상 시드 |
| parksy.kr | — | 1,518 | KR 방송국 (완성형) |
| dtslib-apk-lab | 1.4GB | 923 | APK 18앱 · Play Store 9 |
| dtslib-papyrus | 1GB | 871 | 허브/뇌 (676 md) |
| parksy-logs | 29MB | 725 | 대화 로그/RAG |

### Tier 구조 (REPOSITORY_TREE)
본사HQ 4(papyrus/branch/espiritu/gohsy-fashion) · 미디어 3(parksy.kr/eae.kr/dtslib.kr) · 스튜디오 3(image/audio/tango-magenta) · 브랜치 5(koosy/gohsy/artrew/papafly/lotus) · Tier3 2(hoyadang/gohsy-prod) · 지식관리 3(eae-univ/OrbitPrompt/parksy-logs) · 직영점 4(phoneparis/alexandria/buddies/buckley) · 인프라 4(apk-lab/cloud-appstore/mobile-baptism/playwright)

---

## 2. IT 능력 인프라 (박씨 본인)

### 디바이스
| 디바이스 | 환경 | 용도 |
|----------|------|------|
| S25 Ultra | Termux + proot Ubuntu (aarch64) | 메인 랩 (코딩·추론) |
| S21 (누나) | — | 보급형 양산 기점 |
| 태블릿 | — | 확장 · ADB 통제 |
| 로컬 PC | WSL + WD Passport | 무거운 연산 (46GB parksy-audio 등) |

### AI 두뇌 (에이전트 3종)
| 호출 | 역할 | 비용 |
|------|------|------|
| Claude Code (cc) | 출판부·번역·게이트 | 정책 |
| Grok | 시각·PD(잡지 구도·다큐) | $30/월 |
| Aider (ds) | 작업반장·패치 큐 | DeepSeek |

### 하드웨어 가속 (미확정)
- NPU: Qualcomm Hexagon SM8750 ~45 TOPS (NNAPI 활성화 설계만, S25 실측 0회)
- GPU: Adreno 830 (proot glibc ↔ bionic ABI 불일치로 직통 불가)
- TTS: ParksyTTS local (GPT-SoVITS, CPU 471초/3.5초 — 실시간 135배 느림)
- STT: sherpa-onnx NNAPI (Pixel6 벤치 RTF 0.035 근거, S25 미실측)

### 채널·플랫폼
- Telegram 5봇 · Discord 28채널 · GitHub 5레포→Pages · 티스토리 5 · YouTube 4계정 15채널 · 네이버
- MCP: phone-mcp 18도구(포트3456) · papyrus MCP 19개(배포 ACTIVE 0)

---

## 3. 증설 이력 (설비 변경 로그)

| 날짜 | 변경 | 비고 |
|------|------|------|
| 2026-09-04 | 연결 레포 28 → **39** 확인 | dimas-40의 eae-* 5개 신규 파악 |
| 2026-09-05 | profit-center 신설 | 공장/매출처 개념 분리 |

<!-- 설비 증설 시 위 표에 날짜+내용 추가하고, 상단 기준일 갱신 -->
