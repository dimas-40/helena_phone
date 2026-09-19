---
date: 2026-09-12
agent: Claude Code (폰 워크센터 공장장)
mark: _Claude
type: session-note
status: active
related:
  - session-2026-09-12_parksy-webzine-loop-ssot_Claude.md
  - _notebook/grok/BOSS.md
---

# 그록 편집장 양산 파이프라인 확정 (_Claude · 2026-09-12)

> Boss 확정: 물리 잡지 벤치마크 → 그록이 편집장으로 CLI 원큐 생성 → 보스가 스타일 편집 → 내가 4매체 루프로 양산.
> 원장 저장: `parksy-webzine/00_TRUTH/PRODUCTION.md`

## 1. 양산 파이프라인 (5단계)

```
잡지(물리) ─사진→ 파싱 ─→ 그록(편집장) ─생성→ 이미지/영상 ─→ 보스(스타일) ─→ 나(공장장) ─→ 4매체 루프
```

| 단계 | 담당 |
|------|------|
| 벤치마크 수집 — 일본 잡지 6~7 + 한국 잡지 ~10권 사진 | Boss |
| 이미지 파싱 — 레이아웃·편집 문법 디지털화 | 파이프 |
| 편집장 생성 — CLI Imagine/PD **원큐 일괄** | Grok |
| 스타일 편집 — "표절 베이스라인"에서 내 스타일로 | Boss |
| 공장 루프 — 웹진/유튜브/티스토리/웹툰 교차링크 | Claude(공장장) |

**핵심:** 베끼는 게 아니라 "문법만 가져와서 내 잡지를 만든다" (HOUSE.md 벤치마크).

## 2. 4매체 루프

```
웹진(눕다) parksy-webzine → 유튜브(세우다) @Parksy-webzine → 티스토리(루프) kr-merit-aggro → 돌아옴 + 웹툰(곁)
```

## 3. 첫 worked example — 64권 스킨 일괄 (그록 실행 실측)

Boss 주문 → 그록 실행이 정확히 "원큐 일괄" 패턴. git 이력으로 확인:

- **주문(BOSS.md #20):** 16×4=64권 "초 A급". CLI Imagine 이미지 → 책 3D 스킨 덮어쓰기. 샘플 1~2장 TG → OK면 일괄.
- **실행:**
  - `a45129e` — 마스트헤드 골격 + 샘플 2권(FASHION Street/WATCH Classic).
  - `72febe3` — **64권 일괄 스킨** (+ `_rebuild_shelf.py` 87줄).
- **원칙:** 사진은 호마다 다른 초A, 글자(PARKSY 마스트헤드·호명)는 **웹 타이포 렌더** (이미지에 글자 안 굽음).

## 4. 남은 양산 조건 (공장 쪽 — 내 몫)

- [ ] 유튜브 `@Parksy-webzine` 쓰기권한 재동의 (2FA 1회 — 토큰은 이미 `.secrets.env`에 있음, branch만 쓰기 가능)
- [ ] Content FAB `video` 제품 BOM·레시피 등록
- [ ] 웹진 호 페이지 템플릿 + 루프 매니페스트
- [ ] 잡지 파싱 → 그록 산출물 수용 파이프

*agent mark `_Claude` · 2026-09-12 · 원장: parksy-webzine/00_TRUTH/PRODUCTION.md*
