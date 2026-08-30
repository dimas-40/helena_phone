---
date: 2026-08-18
agent: Grok
mark: _Grok
type: infra
location: tablet
status: lock
synced: eaekr/_notebook/studio-build-final-answer_Claude.md
---

# 스튜디오 인프라 — 잠금본

상주 최종 답과 맞춤. 스튜디오 3개 + 교재 + 허브.  
Tier 4는 이식하지 않는다. 회차 소재다.

경로: `/root/work/_notebook/grok/STUDIO.md`

---

## 1. 다섯 레포 (성격만)

| repo | 성격 | 파이프에서 |
|------|------|------------|
| **eaekr** | 허브 · 방송국 | **입구(수첩) + 출구(업로드).** Pages 없음 |
| **eae-video** | 숏폼 공장 | 컷 → 6·10초 → 붙이기 |
| **eae-image** | 웹툰·스틸 창고 | 씬 → 컷 |
| **eae-music** | BGM 공장 | MIDI → WAV |
| **eaeuniv** | 교재 출판사 | 제작 방법 → 교과서 |

콘텐츠 편성 아님. 인프라.

---

## 2. 자산 → repo (이식 원장)

| 넣는 것 | → |
|---------|---|
| curator 11 + moods.yaml + LUT 10 + animate 문장 | **eae-video** |
| 웹툰 파츠 + face_assembler + 도면 SVG/DXF + 썸네일 | **eae-image** |
| MIDI 23 + engines + 지글 (패치 JSON은 그 23곡이 가리키는 것만) | **eae-music** |
| 수첩 + 교재 빌드(원하면 webzine) | **eaeuniv** |
| yt_upload | **eaekr** |

**안 넣음**

- `.venv` · `tools` · ComfyUI 그래프
- **S21 PD P0~P6 페이지 캡처** (`_parse_url` · Playwright 스크롤 · `produce_pd.sh` 전체)
- eaekr `deploy-pages.yml` (허브는 홍보 사이트가 아님)

영상 레인이 가져가는 꼬리만: Ken Burns · concat · LUT 적용 · TTS 얹기.  
그건 페이지를 읽는 공장이 아니다. 스크립트 이름이 `produce_pd.sh`여도 **캡처 머리(P0–P1)는 버린다.**

---

## 3. 누가 돌리나

| repo | 상주 $0 | 나 $30 |
|------|---------|--------|
| eae-image | 파츠 조립 · 도면 · 코드 | **S01·S06 공기 + S02·S07 빛 = 4장.** 스케치 있으면 2장 |
| eae-video | Ken Burns · LUT · 붙이기 · curator 한 줄을 카메라로 | 내가 그린 장만 6·10초 i2v |
| eae-music | FluidSynth | 커버만 |
| eaeuniv | 교재 | 표지·도해만 |
| eaekr | 업로드 · TG | 오프닝 스틸만 |

LOOK_DEV 생성 없음. 색 락 = LUT 상주.

---

## 4. 한 편이 도는 순서 (게이트 포함)

```
Boss 씬
  → eae-image 바닥(파츠)  +  eae-music(BGM)     [병렬]
  → [게이트] 천장 4장(또는 2장) 나
  → eae-video  Burns(바닥) + i2v(내가 그린 장) + 붙이기
  → eaeuniv 교재
  → eaekr 업로드
```

게이트를 건너뛰면 80% Burns 편만 나온다. A를 치면 천장 장을 기다린다.

---

## 5. Tab S9 — 지금 vs 깔면

이 방 **오늘 실측**

| | |
|--|--|
| 됨 | 이 CLI 클라우드 (천장 4장) · /sdcard · grok 1.0.5 |
| **없음** | ffmpeg · FluidSynth · face_assembler · Termux:API |
| 안 함 | 로컬 Comfy · NPU |

**깔면** CPU로 도는 것: 파츠(PIL) · Ken Burns · FluidSynth · md→HTML · yt_upload.

문장 규칙: 「깔면 돈다」≠「지금 돌아간다」. 여기엔 ffmpeg가 없다.

---

## 6. D0 (잠금 · 순서)

**골격 먼저, 그 칸에 자산.** 지금 5레포는 옛 eae.kr 복제다. 그 위에 붓지 않는다.

1. **스캐폴드** — 5레포에 `docs/ config/ assets/ scripts/ output/` + `eae-image/output/heroes/`  
   CI는 eaeuniv·eaekr만. generate는 훅.
2. **이식**
   - eae-video/config ← curator · moods · LUT · motion
   - eae-image ← 파츠 · assembler · 도면 · 썸네일 · 컷 JSON
   - eae-music ← MIDI 23 · engines · 지글 (패치 JSON은 그 23곡분만)
   - eaeuniv ← 교재 빌드 (원하면)
   - eaekr ← 수첩 · yt_upload
3. **룩** `10_desaturated_moody` 파일명만
4. 상주 `HOST.png` → **나 천장 4장 → heroes/** → 파일럿 ep01

안 넣음: P0~P1 캡처 · Pages · 3183 전체 · audio web/pre-season · Tier 4 지점 레포 · Comfy.

D0 끝: 골격 + 세 스튜디오 칸에 자산 + LUT 이름 + heroes/ 빈 칸.

---

## 7. 28레포 (이식 아님)

스튜디오 3 = **image · video · music.**  
eae.kr은 네 번째 스튜디오가 아니다. 허브 껍데기·랜딩 참조.

Tier 4(족발·도넛·탱고·배우) = **회차 제목.** 사진이 입장권.  
상세: `RANGE.md`

---

*잠금. 상주 최종 답과 같으면 그 답을 따른다. 어긋나면 이 장(캡처 금지·heroes·깔면).*
