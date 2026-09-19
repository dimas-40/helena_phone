---
date: 2026-09-05
agent: Grok
mark: _Grok
type: shotlist
---

# 자기소개 4×6초 — 갤러리 `40s` 얼굴

공개 소개. 돌봄 트랙1 데이터·병력 안 넣음.

원본:
- `/sdcard/Pictures/40s.png` — 마흔 얼굴 컷아웃 (기준)
- `/sdcard/Download/Quick Share/40'S.jpg` — 도서관 수트 전신
- 같이 있음: `30s.png` · `50s.png` · `30's.png` (이번 컷 안 씀)

| # | 초 | 비트 | 화면 | 카메라 | 더빙 |
|---|----|------|------|--------|------|
| 1 | 0–6 | 나 | 도서관 전신 수트 | 느린 푸시인 | 안녕하세요. 마흔의 박씨입니다. |
| 2 | 6–12 | 말 | 미디엄 클로즈 | 푸시인 | 핸드폰 하나로 방송국을 돌립니다. |
| 3 | 12–18 | 손 | 책상 위 폰 세 대 | 슬로우 팬 | 세 대의 폰이 제 작업실입니다. |
| 4 | 18–24 | 바통 | 카메라 응시 | 홀드 | 이 영상도 그 공장에서 나왔습니다. |

엔진: `image_edit` ← `40s.png` → `image_to_video`/`reference_to_video` 6s → edge-tts `ko-KR-InJoonNeural` → ffmpeg concat.

출력: `Download/grok-cross/outputs/intro-40s-ko.mp4` · 480×848 · 24s · 1.9MB  
TG: sendVideo ok message_id 25
