# 아르누보 웹툰 + 성우 나레이션 풀파이프라인 (2026-08-30 확정)

박씨 고정 프리셋(parksy_30s, po-deepfake FACE_LIBRARY와 동일 소스) → 삼성 갤러리
MCP(restyle_image, 좌표 dump 동적탐색)로 배경/장면만 프롬프트로 바꿔가며 아르누보
스타일 컷 여러 장 생성 → webtoon.py로 캐러셀 웹툰 조립(말풍선=텍스트 렌더링) →
edge-tts(ko-KR-InJoonNeural)로 컷별 나레이션 mp3 생성 → 컷 전환 시 해당 나레이션
자동재생되도록 플레이어에 JS 훅 삽입.

## 재현 절차

**1. 컷 생성 (parksy-gallery MCP, restyle_image)**
```python
# source 인자 생략 = 항상 DEFAULT_SOURCE(parksy_30s.png) 고정 인물 사용
await session.call_tool("restyle_image", {
    "style": "아르 누보",              # 박씨 확정 고정 스타일 — 바꾸지 말 것
    "prompt": "<장면 프롬프트>",
    "wait": 22,
    "crop_bottom": 8.0,
})
```
- 컷마다 다른 `prompt`(배경/상황)만 바꾸고 `style`은 항상 "아르 누보" 고정
- 결과는 `/sdcard/DCIM/박씨 갤러리/Drawing_assist_<timestamp>.jpg`에 저장됨

**2. 웹툰 조립 (webtoon.py)**
- manifest JSON에 `images`(위 컷들, base64 또는 URL) + `dialogue`(컷별 대사) 작성
- `python3 tistory-naver/webtoon.py episodes/<manifest>.json --dump > out.html`
- 캐러셀 뷰어(`assets/parksy-webtoon-player.html`)가 말풍선(대사) 자동 렌더링

**3. 나레이션 (edge-tts, ko-KR-InJoonNeural — CLAUDE.md 확정 성우)**
```bash
edge-tts --voice ko-KR-InJoonNeural --rate=+10% --text "<대사>" --write-media cutN.mp3
```
- 컷 개수만큼 mp3 생성, 이 폴더(`episodes/<manifest>-audio/`)에 함께 보관

**4. 컷↔나레이션 동기화 (플레이어 패치)**
`assets/parksy-webtoon-player.html`의 `render()` 함수 끝에 이벤트 디스패치 추가:
```js
document.dispatchEvent(new CustomEvent('pw-panel-change', {detail: cur}));
```
출력 HTML 하단에 `<audio id="pw-audio-N">` N개 + 아래 리스너 삽입:
```js
document.addEventListener('pw-panel-change', function(e){
  // 이전 오디오 정지 → audios[e.detail] 재생
});
```

## 검증 완료 (2026-08-30)
- 3컷 생성: 새벽 서재 / 방송 스튜디오 / 노을 창가 — 전부 아르누보 + 동일 인물(정장·안경) 확인
- 나레이션 3개 개별 + concat 풀트랙(11.2s) 생성 확인
- Claude Artifact로 최종 조립본 시연 (컷 전환 시 나레이션 자동재생 확인)

## 아직 안 한 것
- **티스토리 실제 발행**은 안 함(계정/블로그 실제 게시는 외부 공개 행위라 별도 확인 필요)
- 나레이션 자동재생은 브라우저 정책상 사용자 첫 탭(제스처) 이후에만 소리가 남 —
  강제 자동재생 시도 안 함(에러 없이 조용히 실패하는 게 더 나쁨)
- 이 레시피를 스크립트 하나로 묶는 자동화(`produce_webtoon_va.sh` 같은)는 아직 없음
  — 지금은 수동 3단계(컷생성→조립→오디오)를 순서대로 실행한 것
