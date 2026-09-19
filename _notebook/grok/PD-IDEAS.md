---
date: 2026-08-18
agent: Grok
mark: _Grok
type: pd-ideas
location: tablet
source: dimas-40/eaekr/_notebook/parksy-image-assets_Claude.md
          + dtslib1979/parksy-image 실측
---

# 이 자산으로 PD가 하는 일

자산은 창고다. ComfyUI를 여기 돌리는 게 아니다.  
나는 **감독 YAML을 숏으로 번역**한다.

---

## 자산이 실제로 하는 일

| 자산 | 창고에 있는 것 | 내가 쓰는 법 |
|------|----------------|--------------|
| `curator/` 11명 | 축(샷스케일·톤·팔레트·모션·리듬·프레이밍) + 토큰 | **연출 언어.** 프롬프트에 박는다 |
| `moods.yaml` | 주제→감독 쌍 (예: 인프라=정일성+큐브릭) | **에피소드 렌즈** 자동 선택 |
| animate JSON | ken_burns / pan / zoom (ComfyUI 그래프) | 그래프는 안 돌림. **카메라 한 줄**로 옮김 |
| LUT 10개 .cube | noir·teal·kodak·bleach… | ffmpeg 전엔 **그 룩으로 스틸을 다시 그림**. 있으면 .cube 얹음 |
| `웹툰/` + 프롬프트 | 캐릭터 기준 장 | **호스트 얼굴 고정** (`image_edit` 참조) |
| `썸네일/` | 네이버·유튜브 프레임 | **같은 구도에 새 회차만 앉힘** |
| `도면/` SVG 컷 1–4 | 이미 스토리보드 | 글자 안 다시 그림. **컷을 비추고 6초** |
| `assets/audio/` | 감정 지글 | 붙일 때 큐 시트만. 믹스는 ffmpeg |
| ComfyUI 워크플로 | flux / wan / AnimateDiff | **이식 안 함.** 그 자리는 이 CLI |

S21 P0~P6 페이지 캡처 공장은 **여기로 안 옮긴다.**  
가져올 머리만: 연출 결정(P0.6 자리) = curator + moods.

---

## 프로그램 다섯 (고르면 찍는다)

### A. 렌즈 한 과

같은 강의 한 줄. 감독 하나만 갈아끼움.  
정일성(카메라) / 큐브릭(대칭) / 왕가위(앰버-틸) / 봉준호(비대칭 계급).  
결과: 같은 내용, 다른 방송. 교육방송이 **연출을 가르친다.**

재료: curator YAML + 네 스케치 또는 웹툰 호스트.  
도구: `image_edit` → `image_to_video` 6초.

### B. 웹툰 호스트

`웹툰/` 한 장을 기준 얼굴로 박고, 스튜디오에 앉혀 대사 한 줄.  
`reference_to_video` + 보이스. 회차마다 같은 참조.

재료: 웹툰 png + `.prompt.txt` + 네가 주는 대사.

### C. 도면이 이미 콘티다

「새벽 3시에 혼자 주방을 닦」 cut01–04 + overview.  
컷마다 6초. moods: 기본 정일성, 감정 회차는 고레에다.  
LUT는 kodak 또는 noir.

재료: `도면/svg/*_cut0N.svg`. 숫자는 다시 그리지 않음.

### D. 룩북 — LUT 열 장

마스터 스틸 하나. LUT 이름 10개로 열 장 재생성.  
네가 회차 색을 고른다. ffmpeg 오면 그 .cube를 영상에 얹음.

### E. 썸네일 틀

있는 유튜브/네이버 썸네일 구도를 잡지처럼 읽고, 새 회차 제목만 앉힘.  
글자는 코드(HTML)로. 그림만 `image_edit`.

---

## 창고에서 지금 끌어올 것 / 나중에

**지금 (가볍다, eae-video 머리):**  
`curator/*.yaml` · `moods.yaml` · animate JSON의 `positive` 문장 · LUT 이름 표.

**콘텐츠 날 때 pull:**  
그 회차 웹툰 1장 · 도면 그 에피소드 SVG · 썸네일 틀 1장 · 오디오 1개.

**안 옮김:** `.venv` · `tools` · ComfyUI 그래프 · 페이지캡처 PD 전체.

상주가 물은 「파일 전부 복사 vs 목록만」: **목록 + 위 머리만.** 3183 복사는 PD가 아니다.

---

구체 플랜(파일럿 샷·80% 마감): **`PD-PROPOSAL.md`**

*아이디어 · 찍으라면 프로포절 D0부터.*
