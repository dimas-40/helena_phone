#!/usr/bin/env bash
# 원곡 → 2초 침묵 → 재현 을 한 파일로 붙인다. 페이지의 오디오 정본이 이 파일이다.
#
#   bash scripts/pd_render_combine.sh <midi> <원곡오디오> <출력mp3> [원곡끝초]
#
# 왜 붙이나: 페이지는 "원곡을 듣고, 잠깐 쉬고, 우리가 친 것을 듣는다" 순서다.
# 두 파일을 따로 두면 플레이어가 끊기고, 타임라인이 두 개가 된다. 한 파일이면
# seek 하나로 전부 이동할 수 있다 — 페이지의 타임라인 클릭이 그걸 쓴다.
#
# 재현은 **살라만더 그랜드 피아노**(sfizz + SFZ)로만 친다. 이건 규칙이다.
#
# 렌더 엔진: /root/src/sfizz/build/library/bin/sfizz_render
#   소스에서 직접 빌드했다 (1.2.3). Termux cmake 로는 proot 에서 안 되고
#   Ubuntu cmake 로 빌드해야 한다. 자세한 건 _notebook/124 §6.6.
set -euo pipefail

MIDI="${1:?midi 필요}"
ORIG="${2:?원곡 오디오 필요}"
OUT="${3:?출력 mp3 필요}"
ORIG_END="${4:-}"

SFZ=/root/salamander/SalamanderGrandPianoV3_44.1khz16bit/SalamanderGrandPianoV3.sfz
RENDER=/root/src/sfizz/build/library/bin/sfizz_render
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# sfizz 가 정리 단계에서 죽어도 "렌더가 됐는지"를 가릴 기준 — midi 길이의 절반.
MIDI_SEC=$(python3 - "$MIDI" <<'PY'
import sys, mido
m = mido.MidiFile(sys.argv[1])
print("%.3f" % (m.length))
PY
)

[ -x "$RENDER" ] || { echo "sfizz_render 없음: $RENDER"; exit 1; }
[ -f "$SFZ" ] || { echo "SFZ 없음: $SFZ"; exit 1; }

# 원곡 끝을 알면 그 지점에서 자른다. 트랜스크립션은 곡보다 길게 잡히는 일이
# 흔해서(잔향·박수·무음), 안 자르면 타임라인이 실제보다 뒤로 밀린다.
if [ -n "$ORIG_END" ]; then
  ffmpeg -v error -y -i "$ORIG" -t "$ORIG_END" -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
         -ar 44100 -ac 2 "$TMP/a.wav"
else
  ffmpeg -v error -y -i "$ORIG" -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
         -ar 44100 -ac 2 "$TMP/a.wav"
fi

# -v 는 스레드 스케줄 경고를 쏟는다. 경고가 로그를 덮으면 실패를 못 본다.
# sfizz 1.2.3 은 정리 단계에서 assert 로 죽는 일이 **간헐적으로** 있다
# (Voice.cpp:902 "Missing promise during fillWithData"). 그때도 wav 는 대부분 써졌지만
# **끝자락(0.5~1초)이 잘린다** — 조용히 잘린 트랙을 내보내면 안 된다.
# 그래서 실패하면 최대 2번 더 시도하고, 그래도 안 되면 그때만 "잘렸다"고 알리며 통과시킨다.
# (2026-10-07 바르톡 36호 실측: -p 256 은 매번 죽고, -p 128 은 부하가 겹칠 때만 죽었다.)
RC=1
for try in 1 2 3; do
  set +e
  "$RENDER" --sfz "$SFZ" --midi "$MIDI" --wav "$TMP/r.wav" \
            --samplerate 44100 -p 128 --use-eot 2>/dev/null
  RC=$?
  set -e
  [ "$RC" -eq 0 ] && break
  echo "  (sfizz 종료코드 $RC — $try번째 시도 실패. 다시 친다)" >&2
done
if [ "$RC" -ne 0 ]; then
  RW=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/r.wav" 2>/dev/null || echo 0)
  if awk -v a="$RW" -v b="$MIDI_SEC" 'BEGIN{exit !(a > b*0.7)}'; then
    echo "  ⚠ sfizz 가 세 번 다 죽었다(종료코드 $RC). wav ${RW}s — **끝자락이 잘렸을 수 있다**" >&2
  else
    echo "sfizz 실패 (종료코드 $RC, wav ${RW}s)" >&2; exit 1
  fi
fi
ffmpeg -v error -y -i "$TMP/r.wav" -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
       -ar 44100 -ac 2 "$TMP/b.wav"

ffmpeg -v error -y -f lavfi -t 2.0 -i anullsrc=r=44100:cl=stereo -c:a pcm_s16le "$TMP/gap.wav"

ffmpeg -v error -y -i "$TMP/a.wav" -i "$TMP/gap.wav" -i "$TMP/b.wav" \
  -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1[out]" -map "[out]" \
  -c:a libmp3lame -q:a 3 -ar 44100 -ac 2 "$OUT"

for f in "$TMP/a.wav" "$TMP/gap.wav" "$TMP/b.wav"; do
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  printf '  %-10s %8.2fs\n' "$(basename "$f")" "$d"
done
echo "  combined  $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s  $(du -h "$OUT" | cut -f1)"
