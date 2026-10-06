# 121. YouTube 음원 → MIDI 추출 — 폰에서 돈다

> 2026-10-06 · `_Claude`
> 계기: `_notebook/120-channel-triangle_Claude.md` (사각형) · `_notebook/118-parksy-label-goal-real-bottleneck_Claude.md` (진짜 병목 = 편집)
> 실물: `scripts/midi_extract.py` (422행)

---

## 0. Boss의 질문과 답

> "그러면 이제 미리 추출하는 솔루션은 나온 거냐? 어떻게 만점짜리로 리팩토링 해야 되냐"

**나왔다. 그리고 폰에서 돈다.** — PC로 안 가도 된다.

Boss가 기억한 옛 솔루션(`parksy-audio/pre-season/xtract/`)은 **`basic-pitch`** 를 썼다.
그건 이 폰에서 **설치 불가**(`numpy<1.24` + `tensorflow`, Python 3.14에 휠 없음).
2026-03-15 `MUSIC-PIPELINE-DECISION` 문서가 "Basic Pitch Termux 설치 불가 → PC WSL2"로 결론낸 이유가 그것이다.

**그 결정은 이 모델에 한해 낡았다.** 우리는 **`piano_transcription_inference`** 로 간다 —
Qiuqiang Kong의 CRNN, **PyTorch 전용**(numba 없음). 폰에서 실제로 돌아간다.

---

## 1. 왜 폰에서 도는가 — numba 함정을 피했기 때문

`librosa.pyin` · `librosa.piptrack` 은 **폰에서 크래시**한다:

```
UNREACHABLE executed at .../llvm/lib/CodeGen/TargetSchedule.cpp:226!
```

numba JIT의 aarch64 LLVM 코드젠 버그다. (import는 되고 **JIT 시점에** 죽는다 — CLAUDE.md의 "numba ARM64 크래시"는 맞았지만 원인이 다르다.)

→ **numba를 한 줄도 안 타는 계보**만 쓴다. torch 경로는 안전하다.
이것이 `basic-pitch`(numba/tf 계보) 대신 `piano_transcription_inference`(순수 torch)를 쓰는 **유일한 이유**다.

---

## 2. 파이프라인 6단계

```
[1/6] 가져오기   yt-dlp -x --audio-format wav → 16kHz mono
[2/6] 채보       piano_transcription_inference (torch CPU)
[3/6] 단선율화   동시발음 접기 → 1음씩          ← 여기가 Boss가 말한 "단선율 피아노"의 핵심
[4/6] 양자화     IOI 중앙값 → BPM 추정 → 1/16 격자 스냅
[5/6] 조 정렬    Krumhansl-Schmuckler → 조성 추정 → 스케일 밖 음 스냅
[6/6] 쓰기       GM program 0 (Acoustic Grand) · ppq 480 · mido
```

### 실측 검증 (2026-10-06, 19초 루프 소재)

```
[3/6] 단선율화: 43음 → 32음 (동시발음 11개 접음, 전략=strong)
[4/6] 양자화: 127.6 BPM · 1/16음표 격자 (strength=1.0)
[5/6] 조 정렬: G4 minor — 스케일 밖 0음 이동
최종 32음 · 127.6 BPM · G4 minor
재읽기 32음 · 동시발음 0곳          ← 진짜 단선율 증명
앞 20음: D4 D#4 F4 G4 D4 D#4 F4 G4 G4 D4 D#4 F4 G4 D4 D#4 F4 F4 G4 D4 D#4
```

모티프 `D4 → D#4 → F4 → G4` 가 그대로 살아났고, **G minor로 확정**됐다
(G단음계 = G A Bb C D Eb F — D#=Eb·F·G·D 전부 스케일 안, 스케일 밖 0음).
`재읽기 동시발음 0곳` = 파일을 다시 읽어 확인한 진짜 단선율.

---

## 3. 반드시 짚을 함정 (전부 실제로 밟았다)

| 함정 | 증상 | 처방 |
|---|---|---|
| **`load_audio()` 죽음** | `No librosa.core attribute audio` | 라이브러리 함수 우회 → `librosa.load(path, sr, mono)` 로 배열 직접 전달 |
| **`audioread` 미선언 의존** | `ModuleNotFoundError` | `pip3 install --break-system-packages audioread` |
| **`msg.time` 오독** | 15초 파일이 "11225.00s" | delta tick이지 초가 아니다 → `mido.tick2second` 누적 |
| **`time must be int`** | 저장 실패 | `last=0`(int) 강제. float 하나가 파일 전체를 막는다 |
| **단선율화 과붕괴** | 43음 → 19음, 첫 모티프 소실 | **겹침 체이닝** 금지 → **어택 근접(onset_window=0.06)** 으로 클러스터링 |
| **비공개 영상** | `ERROR: Private video` | API로 `privacyStatus == "public"` 필터 후 소재 선정 |

**단선율화가 가장 위험하다.** 겹침(overlap)으로 묶으면 0.02초 음이 15초 음에 전이적으로 연결돼 곡이 뭉개진다.
어택 근접으로 묶어야 한다 — 이게 43→19 붕괴를 43→32 복구로 바꾼 한 줄이다.

---

## 4. 만점으로 가는 리팩토링 — 확정된 것 / 휴리스틱인 것

### ✅ 확정 (건드리지 말 것)
- 모델 선정 (`piano_transcription_inference`, 순수 torch)
- 16kHz mono 정규화
- gm program 0 · ppq 480 · mido write
- **단선율화 = 어택 근접 클러스터링** (겹침 체이닝은 폐기)
- 재읽기 검증 (`동시발음 0곳`) 을 게이트로

### ⚠️ 휴리스틱 (여기가 "만점"의 여지)
| 파라미터 | 현재 | 문제 | 만점 방향 |
|---|---|---|---|
| `onset_window` | 0.06 고정 | 빠른 곡/느린 곡 동일 취급 | **템포 연동** — 추정 BPM의 1/16 길이에 비례 |
| 양자화 `strength` | 1.0 (전량 스냅) | 셋잇단·루바토 죽임 | **스윙/셋잇단 감지 시 격자 전환** (4/4 → 4/3) |
| 조 추정 | 곡 전체 1회 | 전조(modulation) 놓침 | **마디 단위 국소 조 추정** |
| 옥타브 중복 | `octave_dedup` 일괄 | 실제 옥타브 연주를 지움 | **벨로시티/지속시간 비교 후 판단** |
| 벨로시티 | 모델 출력 그대로 | GM 렌더가 밋밋 | **마스터 게이트에서 다이내믹 커브 재적용** |
| 반주 잔재 | 필터 없음 | 피아노 외 소리도 채보 | **스펙트럼 게이트** (단선율 채널이면 불필요할 수도) |

### 🎯 만점의 정의 (Boss 기준선 규칙 — 정본 §4)
> "[박씨 렌더링]의 결과물은 항상 **Ref.AIVA · Ref.Gemini Song보다 좋아야** 한다."

즉 **추출 정확도가 만점이 아니다. 렌더 결과가 기준선을 넘는 게 만점이다.**
추출은 수단이고, 채점은 `FluidSynth 렌더 → 사람 귀` 다.
→ 리팩토링 우선순위는 **추출 정밀도 < 렌더 청감** 이다.

---

## 5. Boss가 말한 "곱셈"의 나머지 절반

> "이게 곱해지려면은 진짜 괜찮은 **피아노 단선율 YouTube 음악 채널**이 있어야 될 거고"

**이 파이프라인은 소재 품질에 곱해진다.** 소재가 나쁘면 곱은 0이다.

소재 채널 선정 기준 (제안 — Boss 결재 필요):
1. **단선율 피아노** (반주·오케스트라 없음) — 단선율화가 이미 되지만, 원본이 깨끗할수록 손실이 적다
2. **공개(public) 영상** — 비공개는 yt-dlp가 못 뽑는다 (실측)
3. **퍼블릭 도메인 원곡** — 편곡·렌더·업로드까지 가면 **저작권이 최종 병목**이다
4. **템포 안정** — 루바토 심하면 양자화가 곡을 망친다
5. **길이 2~5분** — 200초(Clair de Lune)는 CPU에서 오래 걸린다

⚠️ **여기가 ④ 루프백과 만나는 지점이다.** 저작권이 걸리는 원곡은
YouTube(③)로 못 보낸다 → **parksy.kr 루프백(④)** 으로 간다.
정본: `_notebook/120-channel-triangle_Claude.md` · `parksy.kr/docs/LOOPBACK-STRUCTURE.md`

---

## 6. 사용법

```bash
# 기본 — URL 하나로 끝
python3 scripts/midi_extract.py "https://www.youtube.com/watch?v=XXXX" -o out/

# 단선율 유지 보수
python3 scripts/midi_extract.py SRC -o out/ --strategy strong --grid 4 --quant-strength 0.7
python3 scripts/midi_extract.py SRC -o out/ --key G:minor --no-scale-snap
```

출력: `<name>.mid`(GM program 0) · `<name>.csv`(검수용) · `--keep-raw` 시 `<name>.raw.mid`(원본 채보)

---

## 7. 남은 일

- [ ] **실곡 검증** — Debussy Clair de Lune(`ezJw7RrqvQ0`, 201초) 실측 진행 중. 루프 소재가 아닌 첫 실곡
- [ ] 소재 채널 기준 §5 — Boss 결재
- [ ] 휴리스틱 6종 §4 — 우선순위는 렌더 청감
- [ ] **기준선 A/B** — Ref.AIVA · Ref.Gemini Song과 나란히 렌더해 비교 (만점 판정)

---

*`_Claude` · 2026-10-06 · 이 문서는 폰 proot의 MIDI 추출 정본이다.*
