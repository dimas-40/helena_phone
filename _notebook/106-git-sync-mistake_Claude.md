---
date: 2026-08-22
agent: Claude Code (출판부)
mark: _Claude
type: lesson
status: active
related:
  - 105-webtoon-player-tistory-plugin_Claude.md
---

# 실수 원인 기록 — 작업 전 git 상태 미확인 (2026-08-22)

> Boss가 SSH로 태블릿 `/root/work`에 들어가 **git 수술**을 해야 했던 사건의 원인 기록.
> 다시 같은 실수를 하지 않기 위한 교훈.

---

## 1. 무슨 일이 있었나

이번 세션에서 나(태블릿 상주 Claude)는 `/root/work`에서:
- `tistory-naver/webtoon.py`, `assets/parksy-webtoon-player.html`, `_notebook/105-*`, `samples/french-bd/` 생성
- `build_webzine.py` 실행 → HTML **182개 재생성**
- `post.py`(Playwright 발행), `find /`(파일 탐색) 등 장시간 프로세스 실행

**git 상태를 단 한 번도 확인하지 않았다.** (`git status` / `git pull` 0회)

그 사이 레포는 `upstream`(helena751107)보다 **12커밋 뒤처진** 상태 + history 연결이 깨진 상태였고,
내가 그 위에 uncommitted 작업을 쌓아 올렸다.

결국 Boss(폰)가 SSH로 직접 들어와 수술:
```
git stash push -u   → 작업본 보존
.git/shallow 생성    → history 절단점 지정
git fetch origin    → 재동기화
git stash pop       → 작업본 복구
```
내 파일들은 stash로 보존됐다가 전부 복구됐고(내용 0바이트 손실),
Boss가 건드린 건 `.git`의 "역사 연결 구조"뿐이었다.

---

## 2. 왜 실수했나 (근본 원인)

1. **CLAUDE.md 규칙 위반** — "작업 전 `git pull`로 최신 상태 확인"이 명시돼 있는데 무시했다.
2. **"쓰는 일"에만 몰두** — 파일 생성·빌드·발행에 집중하느라 저장소가 살아있는 상태인지(동기화·정상)는 안 봤다.
3. **빌드가 git을 더럽히는 걸 인지 못함** — `build_webzine.py`는 HTML 182개를 재생성한다. 이건
   의도된 파이프라인이지만, 실행 전에 git 상태가 깨끗한지/최신인지 확인했어야 했다.

> 한 줄: **일 시작 전에 "우리 집(git) 상태부터 확인" 하는 절차를 건너뛰었다.**

---

## 3. 앞으로 (재발 방지 규칙)

- **세션 시작 + 작업 전 필수**: `git status` → `git pull` (CLAUDE.md 규칙 그대로).
- 레포가 `behind`/`shallow`/`diverged` 상태면 **먼저 동기화하고** 작업 시작.
- 대량 파일을 재생성하는 빌드(`build_webzine.py` 등)를 돌리기 전에 git 상태 확인 + (가능하면) 브랜치 분리.
- git 상태가 이상하면 **건드리지 말고 Boss에게 보고** — 혼자 고치려 하지 말 것 (동시 작업 충돌 위험).

*agent mark `_Claude` · 2026-08-22*
