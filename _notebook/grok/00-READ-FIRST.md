---
date: 2026-08-18
agent: Grok
mark: _Grok
cli: grok
type: desk-card
location: tablet
---

# 여기 = 태블릿. 용병 책상.

이 폴더(`_notebook/grok/`)가 이 단말기에서 Grok이 켜질 때 **먼저 읽는 곳**이다.

```
기기   = Tab S9 계열 (8GB/128GB · 8 Gen 2 · Adreno 740 · S-Pen)
역할   = 용병 천장. 공기+빛 최대 4장 (스케치면 2). 공장 80%는 상주.
상주   = DeepSeek로 도는 Claude Code (`_Claude`). Aider 수첩은 없음.
상주 태블릿 수첩 원본 = **dimas-40/eaekr/_notebook/** (08:54 이식)
이 클론 remote = dimas-40/helena_phone (빈 원격). 여긴 사본·내 책상.
```

## 켤 때 순서

1. 이 파일
2. `BOSS.md` — **말한 것만** (지시 장부)
3. `ROLE.md` · `STUDIO.md` · `RANGE.md`
4. 허브 `eaekr/_notebook/studio-build-final-answer_Claude.md`
5. 일. S21이라고 가정하지 말 것.

## 이 폴더 목록

| 파일 | 무엇 |
|------|------|
| `00-READ-FIRST.md` | 이 카드 |
| `BOSS.md` | 이 세션 Boss 말. 채워 감 |
| `ROLE.md` | 역할 (천장 4장) |
| `STUDIO.md` | 인프라 잠금 · D0 순서 |
| `RANGE.md` | 28레포 → 영상 찍기 |
| `eae-5repo-parse.md` | 5레포 보일러 파싱 |
| `hardware.md` | 하드웨어 실측 |
| `resident-notes.md` | 상주 수첩 파싱 |
| `CAN.md` | 이 방송국에서 내가 할 수 있는 것 |
| `CAI.md` | **터미널↔웹 왕복.** 천장 엔진=Imagine 2.0. CLI image_gen 금지 |
| `DUB-OVERWRITE.md` | **챌린지.** 그록 영상 몸 + SoVITS 덮어쓰기. 원장 `108` |
| `PD-IDEAS.md` | parksy-image 자산으로 찍는 프로그램 |
| `PD-PROPOSAL.md` | **렌즈 프로포절** · 파일럿 55초 샷리스트 · 80% A |
| `SESSION-2026-08-18.md` | **오늘 대화 전부 + 결론** |

5-repo English scaffold (no Hangul): `/root/eae-station/`

자동 읽기: `~/.grok/rules/` + `/root/work/.grok/rules/` + SessionStart 훅.
