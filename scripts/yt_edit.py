#!/usr/bin/env python3
"""yt_edit.py — 화면녹화 raw → YouTube 규격 편집기 (폰·컨테이너 공용).

Boss 레인은 PD Pipeline 과 다르다. 입력이 이미 "칠판(URL) 위에서 내가 떠든 화면녹화"다.
그래서 TTS·VO 생성·Ken Burns 가 전부 필요 없다. 있는 건 셋뿐이다:
  ① 실수한 구간 지우기  ② 테이크 이어붙이기  ③ YouTube 규격 맞추기

job JSON 하나로 조작한다. 에이전트가 콘티를 짜면 그게 곧 이 파일이다:

{
  "output": "final.mp4",
  "takes": [
    {"file": "take1.mp4", "title": "1. 문제 제기", "cuts": [[12.5, 18.0]]},
    {"file": "take2.mp4", "title": "2. 방법",     "cuts": []},
    {"file": "take3.mp4", "title": "3. 마무리",   "cuts": [[3.0, 9.2]]}
  ],
  "loudness": -14.0
}

왜 테이크 단위인가:
  파생 표준(phone-video-length-standard)이 "15분 원테이크 금지, 5분×3테이크"다.
  실수가 테이크 안에 격리되고, 테이크 경계가 그대로 챕터 경계가 된다.
  모듈 경계 = 챕터 = 자연 브레이크포인트 = 광고 슬롯 (넷이 같은 자리).

cut 은 **그 테이크의 원본 타임라인** 기준 초 단위다. 뒤 컷이 앞 컷에 영향받지 않는다.
챕터 타임스탬프는 컷 반영 후 **출력 타임라인**으로 자동 계산된다.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ── YouTube 규격 ────────────────────────────────────────────────────────────
# 음량: YouTube 는 -14 LUFS integrated 로 정규화한다. 미리 맞춰두면 재인코딩
# 손실이 줄고, 안 맞추면 유튜브가 알아서 눌러버려서 다이내믹이 죽는다.
TARGET_LUFS = -14.0
TRUE_PEAK = -1.5
LRA = 11.0

VIDEO_ENCODER = "libx264"
PRESET = "veryfast"   # 폰 CPU 실측: 1080x2340@30 10초 → 2.4초 (15분 ≈ 3.7분)
CRF = 18              # YouTube 재인코딩을 견디는 수준. 23은 화면글자가 뭉갠다.
MAX_FPS = 60.0        # 120fps 녹화는 강의에 과하다 — 프레임만 두 배, 화질 이득 없음
AUDIO_BITRATE = "192k"
AUDIO_RATE = 48000

# ── 레인 ────────────────────────────────────────────────────────────────────
# 레인 이름 하나로 캔버스·크롭·글자·배경이 전부 결정된다. 값의 출처는 추측이 아니다:
#   크롭  = 앱스토어 PWA lecture-long/app.js:64
#           CONFIG.devices.S25_ULTRA { topCutPct: 0.090, bottomCutPct: 0.040 }
#   음량  = 앱스토어 clip-shorts/app.js:568  (-16 LUFS)
#   블러  = 배경은 **한 장만** 만들어 재사용한다. 매 프레임 블러하면 15초 편집이
#           38초, 한 장이면 12초였다 (2026-09-22 S25 Ultra 실측). 뒤가 안 변하는데
#           매번 다시 계산하고 있었다.
LANES = {
    "lecture":   {"canvas": "1920x1080", "footer": "dtslib.kr"},
    "tour":      {"canvas": "1920x1080", "footer": "dtslib.kr"},
    "narration": {"canvas": "1080x1920", "footer": ""},
}
TOP_CUT = 0.090
BOTTOM_CUT = 0.040
BG_BLUR = 40
BG_DARK = 0.18


class EditError(RuntimeError):
    pass


def run(cmd: list[str]) -> None:
    """ffmpeg 실행. 실패하면 stderr 꼬리를 그대로 올린다."""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-15:])
        raise EditError(f"ffmpeg 실패 (exit {proc.returncode}):\n{tail}")


def probe(path: Path) -> dict:
    """길이·해상도·fps 를 읽는다. ffprobe 없이 ffmpeg -i 파싱은 취약해서 안 쓴다."""
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_streams", "-show_format", str(path)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise EditError(f"ffprobe 실패: {path}\n{proc.stderr.strip()}")
    data = json.loads(proc.stdout)

    video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    if video is None:
        raise EditError(f"영상 스트림이 없습니다: {path}")
    audio = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)

    def _rate(s: str | None) -> float:
        n, d = (s or "0/0").split("/")
        return float(n) / float(d) if float(d) else 0.0

    # 여기엔 **두 개의 다른 fps** 가 필요하다. 하나로 겸용하려다 2026-09-22 에
    # 화면과 소리가 17.7초 어긋나는 사고가 났다. 역할이 다르다:
    #
    #   fps (출력)   = 컨테이너가 선언한 r_frame_rate, 60 으로 캡.
    #                  유튜브에 내보낼 규격이다. avg 를 여기 쓰면 없는 프레임을
    #                  복제해 용량만 늘고 저더가 생긴다.
    #   retime_fps   = 실제 **촬영** 간격 = nb_frames/duration (= avg_frame_rate).
    #                  삼성 화면녹화기는 60 을 선언하고 82.73 으로 담는다.
    #                  컷으로 생긴 빈 구간을 메울 때 프레임 사이 간격을 이 값으로
    #                  놓아야 실제 시간이 보존된다. 60 으로 놓으면 44.5초가 62.1초가 된다.
    nominal = _rate(video.get("r_frame_rate"))
    average = _rate(video.get("avg_frame_rate"))
    if nominal <= 0:
        nominal = average or 30.0
    retime = average if average > 0 else nominal

    return {
        "duration": float(data["format"]["duration"]),
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": min(nominal, MAX_FPS),
        "retime_fps": retime,
        "src_fps": nominal,
        "vfr": abs(average - nominal) > 0.5,
        "has_audio": audio is not None,
    }


def trim_filter(cuts: list[list[float]], retime_fps: float) -> tuple[str | None, str | None]:
    """컷 구간을 '제외'하는 select 필터쌍을 만든다.

    between(t,s,e) 을 부정해 곱으로 잇는다. 쉼표는 필터 파서의 구분자라 \\, 로
    이스케이프해야 한다 — 이걸 빼먹으면 "No such filter" 로 죽는다.
    """
    if not cuts:
        return None, None
    keep = "*".join(f"not(between(t\\,{s:.3f}\\,{e:.3f}))" for s, e in cuts)
    # ⚠️ setpts=N/FRAME_RATE/TB 를 쓰면 안 된다 (2026-09-22 실측, 폰에서 잡음).
    #    그 식은 프레임 N 을 N/60 초 자리에 놓는다 — 즉 **모든 프레임이 60fps 간격**이라고
    #    가정하고 시간축을 다시 깐다. 그런데 삼성 화면녹화기는 선언 60fps 인데 실제
    #    프레임 간격은 82.73fps 다(nb_frames 3928 / 47.48s). 그래서 44.5초짜리 컷이
    #    62.1초로 늘어나고, 소리는 44.4초에 끝나 **화면과 소리가 17.7초 어긋났다**.
    #    → 그래서 **프레임을 실제 촬영 간격(retime_fps)으로 다시 놓는다.** 이것도 두
    #      가지 일이라 나눠서 봐야 한다:
    #        · setpts=N/…/TB 는 select 가 남긴 **빈 구간을 메운다** (필수)
    #        · 그 나눗셈 값이 곧 프레임 간격이다 → 여기 60 을 넣으면 위 사고가 난다
    #      CFR 변환은 아래 fps 필터가 타임스탬프를 보고 알아서 한다.
    #      (PTS-STARTPTS 만 쓰면 빈 구간이 안 메워져 **컷이 통째로 무시된다** — 실측)
    vf = f"select='{keep}',setpts=N/{retime_fps:.6f}/TB"
    af = f"aselect='{keep}',asetpts=N/SR/TB"
    return vf, af


def normalize_cuts(raw: object, take_no: int) -> list[list[float]]:
    cuts: list[list[float]] = []
    for item in raw or []:
        if isinstance(item, dict):
            s, e = float(item["start"]), float(item["end"])
        else:
            s, e = float(item[0]), float(item[1])
        if e <= s:
            raise EditError(f"테이크 {take_no}: 컷 끝이 시작보다 앞입니다 ({s} → {e})")
        cuts.append([s, e])
    cuts.sort()
    return cuts


def _crop_expr(info: dict, top: float, bottom: float) -> str:
    """S25 상태바·내비바를 잘라낸다. 짝수 높이로 내림 — yuv420p 는 홀수를 못 담는다."""
    h = info["height"]
    ch = max(2, int(h * (1 - top - bottom)) // 2 * 2)
    return f"crop={info['width']}:{ch}:0:{int(h * top)}"


def find_font() -> str:
    """글자용 폰트. 없으면 빈 문자열 — 그러면 글자를 **안 그린다**(조용히 건너뛴다).

    이 조용한 건너뛰기가 함정이다. 컨테이너 베이스(python:3.12-slim)엔 fontconfig 도
    한글 폰트도 없어서, 폰트를 안 넣고 구우면 한글 제목이 **아무 오류 없이** 안 나온다.
    """
    try:
        out = subprocess.run(["fc-match", "-f", "%{file}", "sans"],
                             capture_output=True, text=True)
        return out.stdout.strip() if out.returncode == 0 else ""
    except FileNotFoundError:
        return ""


def make_backdrop(src: Path, info: dict, canvas: str, top: float, bottom: float, dst: Path) -> None:
    """가로 캔버스용 블러 배경 **한 장**. 재사용이 이 파이프라인의 속도 그 자체다."""
    cw, ch = canvas.split("x")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
        "-frames:v", "1", "-vf",
        f"{_crop_expr(info, top, bottom)},"
        f"scale={cw}:{ch}:force_original_aspect_ratio=increase,crop={cw}:{ch},"
        f"gblur=sigma={BG_BLUR},eq=brightness=-{BG_DARK}:saturation=1.1",
        str(dst),
    ])


def process_take(src: Path, dst: Path, cuts: list[list[float]], info: dict,
                 lane: str | None = None, work: Path | None = None,
                 overlay: str = "", footer: str = "",
                 top: float = TOP_CUT, bottom: float = BOTTOM_CUT) -> None:
    """테이크 하나를 컷 + (레인이 있으면) 캔버스 배치까지 해서 중간규격으로 인코딩한다.

    전부 같은 코덱·fps·해상도로 맞춰야 concat demuxer 가 -c copy 로 붙일 수 있다.
    여기서 규격이 어긋나면 뒤에서 화면이 깨지거나 오디오가 밀린다.
    """
    vf, af = trim_filter(cuts, info["retime_fps"])
    pre = f"{vf}," if vf else ""

    # 짝수 차원 강제 — yuv420p 는 홀수 폭/높이를 담지 못해 인코더가 죽는다.
    scale = "scale=trunc(iw/2)*2:trunc(ih/2)*2"
    # VFR → CFR 은 **fps 필터**로 한다. `-r`/`-fps_mode cfr` 로 강제하면 ffmpeg 가
    # 타임스탬프를 무시하고 프레임을 나열만 해서 시간 왜곡이 난다.
    # fps 필터는 타임스탬프를 읽고 프레임을 복제/낙하시켜 **실제 시간을 보존**한다.
    fps_f = f"fps={info['fps']:.6f}"

    # ── 레인 없음: 예전 경로 그대로 (-vf 하나로 끝난다) ────────────────────
    if not lane:
        vf_all = f"{pre}{scale},{fps_f}" if pre else f"{scale},{fps_f}"
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf", vf_all]
        if af and info["has_audio"]:
            cmd += ["-af", af]
        cmd += [
            "-c:v", VIDEO_ENCODER, "-preset", PRESET, "-crf", str(CRF),
            "-pix_fmt", "yuv420p", "-profile:v", "high",
            # CFR 고정은 위 fps 필터가 이미 했다. 여기서 -r 을 또 주면 필터 결과를
            # 다시 나열해 시간이 또 틀어진다.
            "-fps_mode", "cfr",
            "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", str(AUDIO_RATE), "-ac", "2",
            "-movflags", "+faststart", str(dst),
        ]
        run(cmd)
        return

    # ── 레인 있음 ──────────────────────────────────────────────────────────
    # 배경 PNG 를 끼우는 순간 입력이 둘이 되므로 -vf 로는 못 한다. -filter_complex 로
    # 전부 옮긴다(-vf 와 -filter_complex 를 같이 주면 ffmpeg 가 하나만 쓴다).
    cfg = LANES[lane]
    cw_s, ch_s = cfg["canvas"].split("x")
    cw, ch = int(cw_s), int(ch_s)
    portrait = ch > cw
    crop = _crop_expr(info, top, bottom)

    inputs = ["-i", str(src)]
    if portrait:
        # 세로 캔버스는 배경이 필요 없다 — 그대로 꽉 채운다.
        head = f"[0:v]{pre}{crop},scale={cw}:{ch}:force_original_aspect_ratio=increase,crop={cw}:{ch}"
        tail = head
    else:
        bg = (work or Path(".")) / "bg.png"
        make_backdrop(src, info, cfg["canvas"], top, bottom, bg)
        inputs += ["-loop", "1", "-i", str(bg)]
        head = f"[0:v]{pre}{crop},scale=-2:{ch}:flags=lanczos[fg];"
        tail = "[1:v][fg]overlay=(W-w)/2:(H-h)/2:shortest=1"

    font = find_font()
    draw = f",drawtext=fontfile='{font}':text='{overlay}':x=70:y=70:fontsize=52:fontcolor=white@0.9" \
        if (overlay and font) else ""
    foot_txt = footer or cfg.get("footer", "")
    draw += f",drawtext=fontfile='{font}':text='{foot_txt}':x=w-tw-70:y=h-110:fontsize=40:fontcolor=white@0.75" \
        if (foot_txt and font) else ""

    fc = f"{head}{tail}{draw},{fps_f},format=yuv420p[vout]"
    maps = ["-map", "[vout]"]
    if info["has_audio"]:
        fc += f";[0:a]{af + ',' if af else ''}aformat=sample_fmts=fltp:sample_rates={AUDIO_RATE}:channel_layouts=stereo[aout]"
        maps += ["-map", "[aout]"]

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
           "-filter_complex", fc, *maps,
           "-c:v", VIDEO_ENCODER, "-preset", PRESET, "-crf", str(CRF),
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-fps_mode", "cfr",
           "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", str(AUDIO_RATE), "-ac", "2",
           "-movflags", "+faststart", str(dst)]
    run(cmd)


def concat(parts: list[Path], dst: Path, work: Path) -> None:
    """concat demuxer 로 이어붙인다. 재인코딩 없음(-c copy)."""
    listing = work / "concat.txt"
    listing.write_text(
        "".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8"
    )
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(listing),
        "-c", "copy", "-movflags", "+faststart", str(dst),
    ])


def loudnorm(src: Path, dst: Path, target: float) -> None:
    """음량만 다시 입힌다. 비디오는 copy — 두 번 인코딩하지 않는다.

    loudnorm 은 전체 구간의 integrated loudness 를 보므로 반드시 **합본 뒤에**
    한 번만 건다. 테이크마다 걸면 테이크 간 음량 차이가 남는다.
    """
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
        "-af", f"loudnorm=I={target}:TP={TRUE_PEAK}:LRA={LRA}",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", str(AUDIO_RATE), "-ac", "2",
        "-movflags", "+faststart", str(dst),
    ])


def stamp(seconds: float) -> str:
    """챕터용 M:SS / H:MM:SS. YouTube 는 첫 챕터가 0:00 이어야 인식한다."""
    total = int(seconds)
    h, m, s = total // 3600, (total % 3600) // 60, total % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def chapters(titles: list[str], durations: list[float]) -> str:
    lines, cursor = [], 0.0
    for title, dur in zip(titles, durations):
        lines.append(f"{stamp(cursor)} {title}")
        cursor += dur
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="화면녹화 → YouTube 규격 편집")
    ap.add_argument("job", help="job JSON 경로")
    ap.add_argument("--dry-run", action="store_true",
                    help="인코딩 없이 계획만 출력 (폰에서 미리 확인용)")
    args = ap.parse_args()

    job_path = Path(args.job)
    if not job_path.is_file():
        print(f"job 파일이 없습니다: {job_path}", file=sys.stderr)
        return 2
    job = json.loads(job_path.read_text(encoding="utf-8"))

    base = job_path.parent
    takes = job.get("takes") or []
    if not takes:
        print("takes 가 비었습니다.", file=sys.stderr)
        return 2

    out = (base / job.get("output", "final.mp4")).resolve()
    target_lufs = float(job.get("loudness", TARGET_LUFS))

    # 레인은 선택이다. 안 주면 예전처럼 컷·이어붙이기·음량·챕터만 한다.
    lane = job.get("lane")
    if lane and lane not in LANES:
        print(f"모르는 레인입니다: {lane}  ({' | '.join(LANES)})", file=sys.stderr)
        return 2
    overlay = job.get("overlay", "")
    footer = job.get("footer", "")
    top = float(job.get("top_cut", TOP_CUT))
    bottom = float(job.get("bottom_cut", BOTTOM_CUT))

    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            print(f"{tool} 가 없습니다.", file=sys.stderr)
            return 2

    # ── 계획 수립 + 입력 검증 (인코딩 전에 전부 실패시킨다) ──────────────
    plan = []
    for i, take in enumerate(takes, 1):
        src = (base / take["file"]).resolve()
        if not src.is_file():
            print(f"테이크 {i} 파일이 없습니다: {src}", file=sys.stderr)
            return 2
        info = probe(src)
        cuts = normalize_cuts(take.get("cuts"), i)

        removed = sum(e - s for s, e in cuts)
        kept = info["duration"] - removed
        if kept <= 0:
            print(f"테이크 {i}: 컷이 영상 전체를 지웁니다.", file=sys.stderr)
            return 2
        if not info["has_audio"]:
            print(f"⚠️  테이크 {i}: 오디오 스트림이 없습니다 (무음으로 나갑니다)")

        plan.append({
            "no": i, "src": src, "info": info, "cuts": cuts,
            "title": take.get("title") or f"파트 {i}",
            "kept": kept,
        })
        flag = " [VFR→CFR]" if info["vfr"] else ""
        src = (f"  원본 {info['src_fps']:.0f}fps"
               if info["src_fps"] != info["fps"] else "")
        print(f"  테이크 {i}: {info['duration']:.1f}s - 컷 {removed:.1f}s "
              f"→ {kept:.1f}s  ({info['width']}x{info['height']} "
              f"@{info['fps']:.0f}fps{src}{flag})")

    total = sum(p["kept"] for p in plan)
    print(f"\n  합계 {total:.1f}s ({total/60:.1f}분) · 테이크 {len(plan)}개")
    if total < 480:
        print(f"  ⚠️  8분 미만 — 중간광고 자격이 없습니다 (YouTube 규칙)")
    elif total < 720:
        print(f"  ⚠️  12분 미만 — 하한(12분) 아래입니다")

    print("\n  챕터(설명란에 붙여넣기):")
    ch = chapters([p["title"] for p in plan], [p["kept"] for p in plan])
    for line in ch.splitlines():
        print(f"    {line}")

    if args.dry_run:
        print("\n  --dry-run 이므로 인코딩하지 않았습니다.")
        return 0

    # ── 실행 ────────────────────────────────────────────────────────────
    work = Path(tempfile.mkdtemp(prefix="yt_edit_"))
    try:
        parts = []
        for p in plan:
            dst = work / f"take{p['no']}.mp4"
            print(f"  [{p['no']}/{len(plan)}] 인코딩 중…", flush=True)
            process_take(p["src"], dst, p["cuts"], p["info"],
                         lane=lane, work=work, overlay=overlay, footer=footer,
                         top=top, bottom=bottom)
            parts.append(dst)

        joined = work / "joined.mp4"
        print("  이어붙이는 중…", flush=True)
        concat(parts, joined, work)
        if len(parts) > 1:
            # concat -c copy 는 타임스탬프를 이어 붙이므로 실제 길이를 다시 잰다
            real = probe(joined)["duration"]
            drift = real - total
            if abs(drift) > 1.0:
                print(f"  ⚠️  합본 길이 {real:.1f}s — 계산값 {total:.1f}s 와 "
                      f"{drift:+.1f}s 차이 (챕터 타임스탬프가 밀릴 수 있음)")

        print("  음량 정규화 중…", flush=True)
        loudnorm(joined, out, target_lufs)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    final = probe(out)
    print(f"\n  ✅ {out}")
    print(f"     {final['duration']:.1f}s · {out.stat().st_size/1e6:.1f}MB")

    ch_path = out.with_suffix(".chapters.txt")
    ch_path.write_text(ch + "\n", encoding="utf-8")
    print(f"     챕터: {ch_path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except EditError as e:
        print(f"\n❌ {e}", file=sys.stderr)
        sys.exit(1)
