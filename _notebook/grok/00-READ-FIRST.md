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
이 CLI = S25 Ultra (proot 우분투). 탭이 아님. Boss 2026-08-24.
짝     = Tab S9 SM-X716N 쪽 Grok (그쪽도 proot 우분투).
일     = 크로스. 나는 탭 화면 GUI(ADB). 탭 Grok은 Termux. 화면 안 겹침.
         → CROSS.md
기기(탭, 짝) = Tab S9 계열 (8GB/128GB · 8 Gen 2 · Adreno 740 · S-Pen)
역할   = 용병 천장. 공기+빛 최대 4장 (스케치면 2). 공장 80%는 상주.
상주   = DeepSeek로 도는 Claude Code (`_Claude`). Aider 수첩은 없음.
상주 태블릿 수첩 원본 = **dimas-40/eaekr/_notebook/**
이 클론 remote = dimas-40/helena_phone (빈 원격).
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
| `PD-IDEAS.md` | parksy-image 자산으로 찍는 프로그램 |
| `PD-PROPOSAL.md` | **렌즈 프로포절** · 파일럿 55초 샷리스트 · 80% A |
| `SESSION-2026-08-18.md` | **오늘 대화 전부 + 결론** |
| `CROSS.md` | **S25 ↔ 탭 크로스** · GUI는 나 · Termux는 탭 Grok |
| `ROLE-DEVICES.md` | **세 기기 역할 카드** · 방마다 수가 다름 |
| `CANVAS.md` | **Imagine 캔버스 18기능** · 제공 화면 기준, 모바일 없음 |
| `../105-comfy-grokvideo-graft_Grok.md` | Comfy 안 올림. Imagine Video API만 접목 후보 |
| `../106-imagine-canvas-18_Grok.md` | 위 18개 번호 수첩 (HTML 커버리지) |

5-repo English scaffold (no Hangul): `/root/eae-station/`

자동 읽기: `~/.grok/rules/` + `/root/work/.grok/rules/` + SessionStart 훅.
