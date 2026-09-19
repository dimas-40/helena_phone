---
date: 2026-08-24
agent: Grok
mark: _Grok
type: community-research
boss: true
status: verdict
---

# ComfyUI 피로 → GrokVideoNode — 커뮤니티 실측과 접목 판정

Boss: 「로컬 GPU VRAM·노드 스파게티에 지친 유저가 GrokVideoNode로 텍스트/이미지만 던지고 15초+오디오를 API로 받는다. 커뮤니티 리서치해서 우리한테 접목할 수 있는지 봐.」

---

## 0. 한 줄

```
유행은 실재다. 공식이다.
접목할 것은 ComfyUI가 아니라, 그 노드가 감싼 xAI Imagine Video API다.

탭/S25에 Comfy를 올리지 않는다. 그건 피로를 다시 사는 것.
우리는 이미 그 레인에 앉아 있다. 구멍은 「체급」과 「지갑」이다.
```

---

## 1. 커뮤니티가 실제로 하는 일 (2026-01 ~ 08)

지친 축은 실재. 로컬 Wan/AnimateDiff/CogVideo 그래프 + VRAM 부족.  
Reddit r/grok (2026-08 근처): 로컬 Comfy 영상은 5090+64GB가 아니면 Grok 웹만 못 따라간다. 「로컬은 시간 낭비」까지 나옴.  
이건 감정의 글이지 벤치가 아니다. 방향만 증거.

**공식 응답이 노드다.** 2026-01-29 ComfyUI 블로그: `grok-imagine-image` / `grok-imagine-video`를 **partner node**로 넣음.  
핵심 노드 이름: **`GrokVideoNode`**. 문서: LoadImage(선택) → GrokVideoNode → SaveVideo. 로컬 가중치 없음. **외부 API.**

할 수 있는 일 (Comfy 공식 템플릿):

| 노드 | 하는 일 | 한계 (문서) |
|------|---------|-------------|
| GrokVideoNode | 텍스트 또는 한 장 → 영상. 모델 `grok-imagine-video` / `1.5` | 1~15초. 시드는 재현 보장 없음 |
| GrokVideoEditNode | 기존 클립을 말로 고침 | 입력 1~8.7초, ≤50MB |
| GrokVideoExtendNode | 뒤에 2~10초 이어 붙임 | 입력 2~15초 |
| GrokVideoReferenceNode | 참조 이미지 최대 7장 | 문서상 duration 2~10초, 480/720 |

2026-06-16: **Imagine Video 1.5** API GA. 웹/앱은 1.5 Fast. 오디오(효과·대사) 같은 패스. 6초 720p ≈ 25초 대기(xAI 공지).

커스텀 팩: `Cuimao777/ComfyUI-Grok-Imagine-Video` — 공식 REST (`/v1/videos/generations|edits|extensions`) + **자기 `XAI_API_KEY`**. 공식 partner node는 Comfy 크레딧 중간 과금.

과금 함정 (r/comfyui): 생성 후 모더레이션에 걸려도 청구됐다는 보고. 공식 FAQ: partner node는 무료 아님. **자기 xAI 키 BYOK는 partner node에 아직 기본 없음** (커스텀 팩이 그 구멍을 팜).

---

## 2. GrokVideoNode가 감싼 것 = 우리 CLI와 같은 문

xAI REST:

```
POST https://api.x.ai/v1/videos/generations
Authorization: Bearer $XAI_API_KEY
model: grok-imagine-video | grok-imagine-video-1.5
duration: 1–15
resolution: 480p / 720p (1.5는 T2V 1080p)
image.url | reference_images ≤7 | reference_audios voice_id
```

오디오 트랙은 기본 포함. 프리셋 보이스(eve 등)는 1.5 참조영상. **자기 목소리 파일은 파트너 신청.**  
결과 URL은 휘발. 받아서 바로 저장해야 함.  
API 단가 문서 예: 초당 과금 (480p $0.05/s 등). SuperGrok 월 $30과 **다른 지갑.**

Comfy 그래프 3칸은 이 POST를 그림으로 그린 것뿐이다.

---

## 3. 우리 자리 — 이미 겹친다

| 커뮤니티 | 우리 (이미) | 구멍 |
|----------|-------------|------|
| LoadImage | 천장 스틸 · 웹 Imagine · REF_HOST_SUIT | HAND로 웹 첨부 중 |
| GrokVideoNode | 이 CLI `image_to_video` / `reference_to_video` | CLI 도구는 6/10초, 480/720. REST 1.5는 15초·1080p |
| SaveVideo | `/sdcard/Download/grok-cross/outputs` → S21 ffmpeg | 탭에 ffmpeg 없음 |
| Comfy 그래프 | **안 함.** ROLE: 로컬 Comfy/GPU 금지 | 맞음. 다시 열지 않음 |

탭 CAI가 웹 Imagine 2.0을 집은 이유: CLI `image_gen`이 저가 모델이라는 판단. **영상도 같은 분열이 있으면** 웹/API 1.5가 천장, CLI 도구가 초안.

실측 이 폰 `.secrets.env`: **`XAI_API_KEY` 없음.** Grok CLI `auth.json`만 있음. `grok_api.py`는 chat/image까지. **video generations 없음.**  
TTS 403 선례: SuperGrok 구독 ≠ 모든 xAI API.

---

## 4. 접목 판정

### 한다 (API 래퍼. Comfy 아님)

커뮤니티가 산 단순함 = `이미지+한 줄 → 15초 MP4(오디오 포함)`.  
그걸 탭/S25에 붙이는 형태:

```
천장 스틸 (웹 Imagine / image_edit)
    → POST /v1/videos/generations   (GrokVideoNode와 동일)
    → grok-cross/outputs/*.mp4
    → S21 공장 concat · LUT · 업로드
```

코드 위치: `scripts/hand/` 옆 `imagine_video.py` 한 파일. 노드 스파게티 0.  
키: console.x.ai `XAI_API_KEY`. SuperGrok 로그인만으로는 **미실측·과금 분리.**

### 하지 않는다

- 탭/S25/S21에 ComfyUI 설치
- Comfy Cloud 크레딧으로 partner node 돌리기 (중간 마진 + 로그인 화이트리스트)
- 로컬 Wan/AnimateDiff 부활 (VRAM 없음, ROLE 잠금)
- 「오디오 동기화」를 우리 TTS/RVC로 다시 입히는 걸 1.5 기본 오디오와 섞어 과장

### 웹 Imagine vs API

| | grok.com/imagine | REST API | 이 CLI 도구 |
|--|------------------|----------|-------------|
| 체급 | 사람이 쓰는 1.5 Fast (CAI 천장) | `grok-imagine-video-1.5` | Build `image_to_video` (6/10초) |
| 손 | HAND/접근성 (웹뷰 구멍 있음) | curl 한 줄. 결정론 | 이 세션 툴 |
| 돈 | SuperGrok 구독 | 초당 API | 구독 안에 있을 수도, 아닐 수도 |

천장 숏이 15초+대사가 필요하면 **API 1.5 또는 웹**. CLI 10초 도구로 「커뮤니티가 말한 그 체급」이라고 우기지 말 것.

---

## 5. 다음 수 (Boss가 지갑을 열 때)

1. `XAI_API_KEY`를 `.secrets.env`에만 넣는다. 레포 금지.
2. `scripts/hand/imagine_video.py` — POST generations → 폴링 → outputs에 저장. Comfy 없음.
3. 파일럿: REF_HOST_SUIT 1장 + 카메라 한 줄 → 6초 720p 1클립. 과금 확인.
4. 되면 PD 샷리스트 칸 ②를 `duration=6|10|15`로 연다. 웹 피커는 스틸 천장만.

안 열면: 지금 CLI `image_to_video` 10초 + 웹 Imagine 스틸. 커뮤니티 래퍼와 **같은 구름**, 다른 문.

---

## 출처 (열어 본 것)

- Comfy 공식 블로그 2026-01-29 · GrokVideoNode 내장 문서 · 튜토리얼 (gen/edit/extend/reference)
- xAI Imagine API 뉴스 · Video 1.5 2026-06-16 · REST `/v1/videos/generations`
- Cuimao777/ComfyUI-Grok-Imagine-Video (자기 키)
- r/grok 로컬 vs 웹 · r/comfyui 모더레이션 과금
- 우리: `83` · `ROLE.md` · `CAN.md` · `PD-PROPOSAL.md` · `CAI.md`(탭) · `HAND.md`

*agent mark `_Grok` · 2026-08-24*
