---
date: 2026-08-24
agent: Grok
mark: _Grok
type: pipeline
location: s25-ultra
pair: tab-s9
---

# HAND — 접근성 레이더 (비전은 폴백)

Boss 2026-08-24. 탭 Grok CAI 왕복(샷→좌표 추론)을 접는다.

## 판정 (정직)

맞는 것: LLM이 스크린샷 보고 좌표를 때리는 건 **구조적 낭비**. 네이티브 UI는 접근성 노드를 직접 쳐야 한다.

틀린/과장:
- AutoJS6가 웹 Imagine에서 **100%** 라는 말은 안 함. Chrome/웹뷰는 노드가 비는 화면이 있다. 그때만 비전.
- `uiautomator dump` 자체는 비전가 아니다. 낭비가 되는 지점은 XML을 **LLM에게 읽히는 것**.
- 탭에 ffmpeg 없음. 양산 concat/TTS는 S21 공장.

실측 2026-08-24: 탭 `org.autojs.autojs6` 6.7.0, 접근성 **이미 ON**.

## 레인

```
기본   AutoJS6 HTTP  127.0.0.1:18765   (adb shell curl)
폴백   uiautomator XML을 로컬 파서     (hand/uia.py, LLM 없음)
예외   NEED_VISION 신호만. 에이전트가 샷을 열 때
```

CLI: `python3 scripts/hand/hand.py --serial 100.86.15.50:5900 click --text 완료`

탭 Termux는 앞에 두지 않음. S25가 이 손을 돌린다. `CROSS.md`.

## 오늘 실측 (2026-08-24)

| 시도 | 결과 |
|------|------|
| 탭 AutoJS6 6.7.0 + 접근성 ON | 설치됨 |
| HTTP `adb shell curl :18765` | 안드로이드 셸에 curl 없음 → 폐기. `adb forward` + 호스트 curl 또는 파일 IPC |
| RunIntentActivity → result.json | **아직 안 떨어짐.** 외부 실행 권한/파일 URI 막힘 가능. `HAND_AUTOJS=1`로만 재시도 |
| `uiautomator dump` + 로컬 파서 | **됨.** LLM 없이 `사이드바 전환`·`새로운 생성` 타격 |
| Imagine 웹 | 라벨은 보임. 작곡줄(업로드/제출)은 높이 0이거나 계정 메뉴와 **bounds 겹침**. 웹뷰는 폴백 구간 |
| 비전 좌표 | 탭 Grok CAI 왕복 — **금지.** NEED_VISION 신호일 때만 |

코드: `scripts/hand/` · 탭에도 복사됨. `cai.sh`는 `click/find/tree`를 hand로 넘김.
