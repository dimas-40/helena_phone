---
date: 2026-08-24
agent: Grok
mark: _Grok
type: process-lock
location: s25-ultra
pair: tab-s9
---

# AutoJS6 표준 프로세스 — GUI 손 (비전 금지)

Boss 2026-08-24. 영상 양산 전에 손을 잠근다.

## 0. 한 줄

```
라벨 있는 버튼 = 접근성 노드.
AutoJS6가 1순위 손. dump를 모델에 읽히지 않음.
비전 샷은 NEED_VISION 신호일 때만.
```

탭 실측: `org.autojs.autojs6` 6.7.0, 접근성 **ON**.

## 1. 레인

```
cmd.json  →  AutoJS6 hand-watch.js (접근성 click/find)
              ↓ 실패 또는 워치 꺼짐
            uia.py (uiautomator XML 로컬 파서, LLM 없음)
              ↓ 노드 없음 (웹뷰 캔버스)
            NEED_VISION  →  shot. 좌표 추측 금지 원칙은 유지
```

S25가 cmd를 떨어뜨린다. 탭 Termux는 Chrome 앞에 두지 않음. `CROSS.md`.

## 2. 파일

| 경로 | 역할 |
|------|------|
| `/sdcard/Scripts/hand-watch.js` | AutoJS6 상주. 200ms 폴링 |
| `/sdcard/Download/grok-cross/cmd.json` | 한 수. `{op, text, desc, id}` |
| `/sdcard/Download/grok-cross/result.json` | 응답 |
| `scripts/hand/hand.py` | S25/탭 CLI |
| `scripts/hand/uia.py` | 폴백 |

## 3. 켜는 법 (1회)

접근성은 이미 ON. 워치 스크립트는 **AutoJS6에서 한 번 Run**.  
Intent 외부실행은 2026-08-24 실측에서 result가 안 떨어졌다. 사람 1회 또는 이후 intent 재시도.

그 다음부터 에이전트는 `python3 scripts/hand/hand.py click --text 완료` 만.

## 4. 이 프로세스에 안 넣는 것

로컬 Comfy. 비전 좌표. dump XML을 모델 컨텍스트에 넣기. 탭 ffmpeg 양산.
