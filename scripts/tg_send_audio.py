#!/usr/bin/env python3
"""음원을 텔레그램으로 보낸다. tg.sh 는 글자만 보내므로 따로 있다.

사용:
  python3 scripts/tg_send_audio.py FILE.mp3 --title "제목" --performer "연주자" --caption "설명"

토큰은 .secrets.env 에서 읽는다. 값은 절대 출력하지 않는다.
"""
import argparse
import mimetypes
import os
import sys
from pathlib import Path

SECRETS = Path(__file__).resolve().parent.parent / ".secrets.env"


def load_secrets(path=SECRETS):
    """KEY=VALUE 를 환경으로 올린다. 파일이 없으면 있는 환경변수를 쓴다."""
    env = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("TG_TOKEN", "TG_CHAT"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


def main():
    ap = argparse.ArgumentParser(description="음원을 텔레그램으로 보낸다")
    ap.add_argument("file", help="보낼 파일 (mp3/wav/m4a)")
    ap.add_argument("--title", default="", help="곡 제목")
    ap.add_argument("--performer", default="", help="연주자·출처")
    ap.add_argument("--caption", default="", help="파일 위에 붙는 설명")
    ap.add_argument("--duration", type=int, default=0, help="길이(초). 0이면 생략")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print("실패: 파일 없음 %s" % path, file=sys.stderr)
        return 1

    env = load_secrets()
    token, chat = env.get("TG_TOKEN", ""), env.get("TG_CHAT", "")
    if not token or not chat:
        print("실패: TG_TOKEN 또는 TG_CHAT 이 없다 (.secrets.env 확인)", file=sys.stderr)
        return 1

    try:
        import requests
    except ImportError:
        print("실패: requests 가 없다", file=sys.stderr)
        return 1

    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    data = {
        "chat_id": chat,
        "title": args.title or path.stem,
        "performer": args.performer or "parksy-midi",
    }
    if args.caption:
        data["caption"] = args.caption
    if args.duration > 0:
        data["duration"] = str(args.duration)

    url = "https://api.telegram.org/bot%s/sendAudio" % token
    with open(path, "rb") as fh:
        r = requests.post(url, data=data,
                          files={"audio": (path.name, fh, mime)}, timeout=300)

    if r.status_code != 200:
        # 토큰이 응답 URL 에 섞여 나올 수 있으니 본문만 짧게 보여준다
        print("실패: HTTP %s\n%s" % (r.status_code, r.text[:400]), file=sys.stderr)
        return 1

    j = r.json()
    if not j.get("ok"):
        print("실패: %s" % str(j.get("description", j))[:400], file=sys.stderr)
        return 1

    res = j.get("result", {})
    print("보냄: %s (%d bytes) → message_id %s" % (
        path.name, path.stat().st_size, res.get("message_id", "?")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
