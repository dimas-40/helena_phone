---
date: 2026-08-18
agent: Grok
mark: _Grok
type: parse
location: tablet
---

# 상주 에이전트 수첩 파싱 (이 태블릿)

## 결론부터

**`*_Aider.md` = 0장.** Aider(`ds`) 수첩은 이 방에 없다.  
`aider` 바이너리도 PATH에 없음. 래퍼만 `scripts/ds.sh` — 실행하면 "aider 없음"으로 죽음.

상주가 적어 둔 것은 **Claude Code + DeepSeek 과금**, 마크 **`_Claude`**.

**2026-08-18 08:54 — 태블릿 수첩 원본은 허브 `dimas-40/eaekr`로 이식됨.**  
커밋 `9bdb6de` `docs: 태블릿 업무 수첩 이식`. 이 helena_phone 클론에 남은 건 **사본**.

| 지금 원본 (허브) | 바이트 | 무엇 |
|------------------|--------|------|
| `dimas-40/eaekr/_notebook/tablet-broadcast-studio_Claude.md` | 9722 | 방송국 부서 + 서플라이 체인 |
| `dimas-40/eaekr/_notebook/tablet-setup-parksy-method_Claude.md` | 4702 | parksy 공법 파싱 |

실측: 로컬 사본과 **바이트 동일**.  
`eae-music` · `eae-image` · `eae-video` · `eaeuniv` 에는 `_notebook` **없음**.

허브에 추가됨 (08-18, 상주): `s21-publishing-automation_Claude.md` — S21 바꾸기 전 6채널 인벤토리. Grok 참고용.

이 클론에만 남은 상주 글 (허브로 안 옮김):

| 파일 | 무엇 |
|------|------|
| `session-2026-08-18_Claude.md` | 계정 지도 · PAT · 콜라보 수락 |
| `grok-cli-install-troubleshooting_Claude.md` | 이 CLI 설치 삽질 (TTY/ENXIO) |

`99-devlog.md` 하단 08-18 섹션도 같은 상주가 쌓음.

---

## 1. session-2026-08-18 — 계정

- 과금 = DeepSeek (`api.deepseek.com/anthropic`, `deepseek-v4-pro`). Anthropic 아님.
- `gh` = **dimas-40**. 이 기기 push 계정.
- helena751107 = 콘텐츠 5레포 원조. dtslib1979 = 허브 28레포.
- PAT full admin → 로테이션 권장 (원문은 수첩에 없음).
- 팬딩: dimas-40 vs helena751107 원조 정리 · SSOT owner 불일치 · 태블릿 보일러플레이트.

상주는 본문을 "S21"이라고 썼다. **실리콘은 태블릿.** 그 수첩의 기기 라벨은 틀린 채로 남아 있다.

---

## 2. tablet-setup-parksy-method — 공법

- 태블릿 = Tier 2 · 손(펜) · `Thomas.tj.Park@gmail.com`.
- 사다리: S21 베이스라인 → 태블릿 이식 → S25 뇌.
- 상주 당시 갭: "이 환경이 S21인지 태블릿인지 미확정". **지금은 태블릿으로 실측 끝** (`hardware.md`).

---

## 3. tablet-broadcast-studio — 이 방의 일 (상주 계획)

태블릿 = **교육방송 스튜디오**. 출판(helena Pages) 아님.

```
dtslib1979 (뇌) --fork--> dimas-40 (여기) --업로드--> thomas.tj.park YouTube
```

EAE 5레포 (private): eae-music · eae-image · eae-video · eaekr · eaeuniv.  
껍데기 생성은 상주가 했다고 체크. 콘텐츠 pull · 스플릿 · 스모크는 남음.

내 칸과 맞닿는 줄: **입력① 그림 = 스케치→Grok (클라우드).**  
ffmpeg 영상 렌더는 상주/반장 레인. 이 방엔 ffmpeg 아직 없음.

---

## 4. grok-cli-install-troubleshooting — 이 CLI

- grok 1.0.5 설치·로그인 성공. 로그인 메일 `dtslib1979@gmail.com`.
- `grok "안녕"` ENXIO = 네트워크 아님. **`/dev/tty` 없는 헤드리스**.
- 상주가 gai.conf/hosts를 건드렸다가 **원상복구**함.
- Termux alias: `grok`=`gr`=`proot-distro login ubuntu -- bash -lc "cd /root/work && /root/.grok/bin/grok"`

---

## 상주 팬딩 (내가 훔치지 않음)

- EAE fork 콘텐츠 pull · parksy-image 스플릿 · FluidSynth 스모크
- SSOT를 dimas-40 / thomas.tj.park 로
- 태블릿 person_name/tagline Boss 지정
- 8/20 보안패치 스킵
- Aider 자체는 **미설치** — 반장 수첩을 기대한 자리는 비어 있음
