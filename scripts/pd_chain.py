#!/usr/bin/env python3
"""남은 곡을 **짧은 것부터** 한 곡씩 끝까지 돌린다 — 채보부터 data.js 까지.

    nohup python3 -u scripts/pd_chain.py > /tmp/pd_chain.log 2>&1 &

    python3 scripts/pd_chain.py 46      # 한 곡만 (번호를 인자로)

왜 체인인가:
    채보는 **한 번에 하나만** 돌려야 한다(직렬 규칙 — 둘을 같이 돌려 둘 다 느려진
    2026-10-08 실수를 되풀이하지 않는다). 그런데 사람이 곡마다 앉아 있을 수 없다.
    그래서 앞 곡이 끝나면 다음 곡이 **저절로** 시작하게 한다 — CPU 가 놀지 않게.

사람이 하는 몫(이 체인이 안 하는 것):
    · page.py 쓰기 (쪽지 — 이 시리즈의 본체)
    · pd_page.py / pd_build_deploy.sh / pd_check_pages.py / push
    · 라이선스 판정 · 대시보드 슬러그 채우기
    체인은 **숫자와 소리**까지만 만든다. 글은 사람이 쓴다.

곡마다 하는 일:
    1. 채보        midi_extract.py ... --keep-raw       → mfNN_raw.mid
    2. 검증        pd_verify_transcription.py           → NN.corr.json (⚠ mfNN.verdict.json 은 midi_extract 가 쓴다 — 건드리지 않는다)
    3. 실측        pd_measure.py                        → NN.facts.json
    4. 원곡+재현   pd_render_combine.sh                 → NN-combined.mp3
    5. 그래프자료  pd_build_data.py --grid auto         → site/<slug>/data.js

⚠️ 이미 mfNN_raw.mid 가 있는 곡은 **건너뛴다**(다시 채보하지 않는다).
   다시 돌리려면 그 파일을 지우고 시작할 것.

⚠️ 검증이 "실패"로 나와도 **체인은 다음 곡으로 간다.** 다만 로그에 크게 남긴다.
   그 곡은 사람이 판정할 때까지 **쓰지 않는다**(30호와 같은 방식으로 보류).
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/root/work")
PD = ROOT / "midi_lane" / "pd"
S = ROOT / "scripts"

# (번호, 폴더, 원곡파일, 예상길이초)  — 짧은 순. 길이는 우리가 읽은 파일 길이가 아니라
# 채보 시간을 어림하기 위한 값이다(사람이 적은 것 — 실측은 facts.json 이 정본).
SONGS = [
    ("42", "42-chopin-black-key",        "blackkey.flac",  110.85),
    ("40", "40-scriabin-etude-8-12",     "scriabin40.ogg", 124.00),
    ("39", "39-mussorgsky-goldenberg",   "goldenberg.ogg", 128.35),   # ⚠ 30호와 같은 무소펜 세트
    ("35", "35-chopin-etude-25-6",       "etude35.flac",   130.19),
    ("41", "41-schumann-kreisleriana-1", "kreis41.ogg",    150.52),
    ("31", "31-debussy-golliwog",        "golliwog.wav",   160.50),
    ("47", "47-bach-italian-concerto-1", "italian1.ogg",   222.88),
    # ⚠ 46호 — 2026-10-08 에 **파일 제목이 뒤바뀐 것**을 확인했다. 제목이 N8 인 파일은
    #    내용이 No.3 이었고, 제목이 N3 인 파일이 실제 No.8 이다(소리 크로마 DTW 0.0885 대
    #    0.2835 · 채보 앞 21음 순서까지 일치 · 통제 0.2793). 그래서 원곡 파일을 바꿨다.
    #    근거 전문은 `midi_lane/pd/46-schumann-kreisleriana-8/_dl/SOURCE.txt`,
    #    No.3 자산은 같은 폴더 `_was-no3/` 에 남겨 두었다(버리지 않는다).
    ("46", "46-schumann-kreisleriana-8", "kreis46_n8_N3titled.ogg", 222.44),
    ("12", "12-ravel-alborada-del-gracioso", "alborada.flac", 357.26),
    ("26", "26-schubert-impromptu-90-3", "imp26.ogg",      357.84),
    ("43", "43-ravel-le-gibet",          "legibet.flac",   424.72),
    ("48", "48-schubert-impromptu-90-1", "imp48.ogg",      537.77),
    ("45", "45-bach-goldberg-var25",     "var25.mp3",      558.31),
    ("44", "44-chopin-ballade4",         "ballade4.oga",   676.66),
]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run(cmd, cwd, logfile, ok_codes=(0,)):
    """로그를 파일에도 남긴다 — 죽었을 때 어디서 죽었는지 봐야 한다."""
    with open(logfile, "a") as f:
        f.write(f"\n$ {' '.join(str(c) for c in cmd)}\n")
        f.flush()
        p = subprocess.run([str(c) for c in cmd], cwd=str(cwd),
                           stdout=f, stderr=subprocess.STDOUT)
    return p.returncode


def already(no, cwd):
    return (cwd / f"mf{no}_raw.mid").exists()


def do_song(no, slug, audio, dur):
    cwd = PD / slug
    d = cwd / "_dl"
    src = d / audio
    # 채보 로그는 **곡 폴더 안에** 남긴다. /tmp 에만 두면 재부팅에서 사라진다 —
    # 2026-10-08 에 42호 로그가 그렇게 없어져 "이 곡도 단선율화를 했나"를
    # 확인할 수 없었다(옛 곡들은 extract.log 를 곡 폴더에 남겨 확인이 된다).
    # 도구가 무엇을 했는지가 곡마다 남아야 쪽지에서 견줄 수 있다.
    lg = str(cwd / "extract.log")
    t0 = time.time()

    log(f"── {no}호 {slug} 시작 (원곡 {dur:.1f}초 → 채보 예상 {dur*12.5/60:.0f}분)")

    if not src.exists():
        log(f"   ✗ 원곡 없음: {src} — 건너뛴다")
        return "원곡없음"

    if already(no, cwd):
        log(f"   · mf{no}_raw.mid 이미 있음 — 채보 건너뜀")
    else:
        rc = run([sys.executable, "-u", S / "midi_extract.py", src, "-o", ".",
                  "--name", f"mf{no}", "--keep-raw"], cwd, lg)
        if rc != 0 or not already(no, cwd):
            log(f"   ✗ 채보 실패 (rc={rc}) — {lg} 참고. 다음 곡으로 간다")
            return "채보실패"
        log(f"   ✓ 채보 완료 ({(time.time()-t0)/60:.1f}분)")

    raw = cwd / f"mf{no}_raw.mid"

    # ── 2. 검증 (소리와 대조) ────────────────────────────────
    rc = run([sys.executable, S / "pd_verify_transcription.py", raw, src,
              "--out", cwd / f"{no}.corr.json"], cwd, lg)
    # 검증 실패는 **쪽지를 쓰라는 신호가 아니다.** 아래 마지막 줄이 실패한 곡에도
    # "쪽지를 쓰면 된다"고 말해서 39호(2026-10-08)에서 사람이 헷갈릴 뻔했다.
    # 그래서 판정을 여기서 기억해 두고 마지막 줄을 갈라 쓴다.
    held = None
    try:
        v = json.loads((cwd / f"{no}.corr.json").read_text())
        log(f"   검증: {v['verdict']}  flux {v['corr_flux']:+.3f} · rms {v['corr_rms']:+.3f}")
        if v["verdict"] == "실패":
            held = f"검증 실패 (flux {v['corr_flux']:+.3f} · rms {v['corr_rms']:+.3f})"
    except Exception as e:
        log(f"   ⚠ 검증 판정 읽기 실패: {e}")
        held = f"검증 판정을 읽지 못했다 ({e!r})"

    # ── 3. 실측 ─────────────────────────────────────────────
    rc = run([sys.executable, S / "pd_measure.py", raw, src,
              "--name", no, "--out", cwd / f"{no}.facts.json"], cwd, lg)
    if rc != 0:
        log(f"   ✗ 실측 실패 (rc={rc})")
        return "실측실패"

    facts = json.loads((cwd / f"{no}.facts.json").read_text())
    # 원곡을 자를 지점: 들리지 않는 꼬리를 버린다(pd_measure 의 tail_s 정의 그대로).
    orig_end = round(facts["orig_dur"] - facts.get("tail_s", 0.0), 2)
    orig_end = max(orig_end, round(facts["last_note"] + 0.3, 2))
    log(f"   실측: {facts['n_notes']}음 · 원곡 {facts['orig_dur']:.2f}s → {orig_end:.2f}s 에서 자른다")

    # ── 4. 원곡 + 2초 침묵 + 재현 ────────────────────────────
    combined = cwd / f"{no}-combined.mp3"
    rc = run(["bash", S / "pd_render_combine.sh", raw, src, combined, orig_end], cwd, lg)
    if rc != 0 or not combined.exists():
        log(f"   ✗ 렌더 실패 (rc={rc})")
        return "렌더실패"
    log(f"   ✓ 렌더 완료 {combined.stat().st_size:,}B")

    # ── 5. 그래프 자료 ──────────────────────────────────────
    site = cwd / "site" / slug
    site.mkdir(parents=True, exist_ok=True)
    (site / "img").mkdir(exist_ok=True)
    (site / "audio").mkdir(exist_ok=True)
    rc = run([sys.executable, S / "pd_build_data.py", "--midi", raw, "--audio", combined,
              "--orig-end", orig_end, "--gap-end", round(orig_end + 2.0, 2),
              "--grid", "auto", "--bar-unit", "칸", "--out", site / "data.js"], cwd, lg)
    if rc != 0:
        log(f"   ✗ data.js 실패 (rc={rc})")
        return "data실패"

    site_audio = site / "audio" / "combined.mp3"
    if not site_audio.exists() or site_audio.stat().st_size != combined.stat().st_size:
        subprocess.run(["cp", str(combined), str(site_audio)], check=True)

    # 검증에 실패했으면 **HOLD 표식을 남긴다** — 사람이 잊고 쪽지를 쓰지 않도록,
    # 그리고 pd_build_deploy.sh 가 배포 묶음에서 자동으로 빼도록.
    if held:
        (cwd / f"{no}.HOLD").write_text(
            f"{no}호 보류 — {held}\n"
            f"사람이 판정할 때까지 쓰지 않는다. 30호와 같은 방식.\n"
            f"다시 돌리려면 mf{no}_raw.mid 를 지우고 이 파일도 지운다.\n"
        )
        log(f"   ⛔ {no}호 **보류** — {held}")
        log(f"      {no}.HOLD 남김. 쪽지를 쓰지 않는다. 사람이 판정할 것.")
        return "보류"

    log(f"   ✅ {no}호 준비 끝 — 쪽지(page.py)를 쓰면 된다 · 총 {(time.time()-t0)/60:.1f}분")
    return "완료"


def wait_for_others():
    """이미 돌고 있는 채보가 있으면 **끝날 때까지 기다린다.**

    왜: 2026-10-08 에 둘을 동시에 돌려 서로 CPU 를 나눠 가져 **둘 다 느려졌다.**
    그 실수를 사람이 기억하는 것에 맡기지 않고 여기 코드로 막는다.
    """
    while True:
        out = subprocess.run(["pgrep", "-f", "midi_extract.py"], capture_output=True, text=True)
        pids = [p for p in out.stdout.split() if p.strip() and int(p) != __import__("os").getpid()]
        if not pids:
            return
        log(f"먼저 도는 채보가 있다 (pid {', '.join(pids)}) — 끝날 때까지 기다린다")
        time.sleep(30)


def main():
    # 인자를 주면 **그 번호만** 돌린다 (예: `pd_chain.py 46`). 한 곡만 다시 돌릴 때
    # 목록을 복사해 두 번째 체인 스크립트를 만들지 않으려고 여기에 붙였다 —
    # 2026-10-08 46호 제목 뒤바뀜을 고치며. 인자가 없으면 예전과 똑같이 전곡이다.
    only = set(sys.argv[1:])
    songs = [s for s in SONGS if not only or s[0] in only]
    if only:
        missing = only - {s[0] for s in SONGS}
        if missing:
            raise SystemExit(f"목록에 없는 번호: {sorted(missing)}")
    wait_for_others()
    log(f"체인 시작 — {len(songs)}곡 (짧은 순)" + (f" · 지정 {sorted(only)}" if only else ""))
    tally = {}
    for no, slug, audio, dur in songs:
        try:
            r = do_song(no, slug, audio, dur)
        except Exception as e:
            log(f"   ✗ {no}호 예외: {e!r}")
            r = "예외"
        tally[no] = r
    log("체인 끝 — " + " · ".join(f"{k}:{v}" for k, v in tally.items()))


if __name__ == "__main__":
    main()
