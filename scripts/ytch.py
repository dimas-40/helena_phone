#!/usr/bin/env python3
"""
ytch — 폰 상주 YouTube 채널 러너 (전 채널).

랩탑 6개 레포에서 긁어온 **채널별 토큰 18개**를 지도(CHANNEL-MAP.json)로 삼아,
어느 채널이든 폰에서 읽고 쓴다. 기본 채널 = musician-parksy (박씨 음악 배포 아카이브).

  channels                  등록된 채널 지도 전체
  whoami   [--channel S]    그 토큰이 실제로 여는 채널 확인 (channels.list mine)
  playlists[--channel S]    채널 소유 플레이리스트
  videos   [--channel S] [--playlist PLID]
  add      <PLID> <VIDEOID> [--channel S]        playlistItems.insert
  upload   <file> --title T [...] [--confirm]    videos.insert (게이트)

토큰 실물(레포 밖, gitignored): /root/.secrets/youtube/
  CHANNEL-MAP.json                     토큰파일 → 채널 지도
  parksyimage_accounts/accounts/*.json 채널별 토큰 15개 (upload 스코프 O)
  papyrus_accounts/accounts/token_*.json 계정 a~d 토큰

⚠️ 하드 룰: --confirm 없이는 업로드하지 않는다. (TG 보고 → Boss 검수 → 실행)
⚠️ 자격증명 값은 절대 출력하지 않는다.
"""
import json, os, sys, urllib.request, urllib.parse, urllib.error

BASE = os.environ.get("YT_SECRET_DIR", "/root/.secrets/youtube")
MAPFILE = os.path.join(BASE, "CHANNEL-MAP.json")
API = "https://www.googleapis.com/youtube/v3"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3"

# 슬러그 → (토큰파일, 그룹, 시크릿경로)
SECRETS = {
    "parksyimage": os.path.join(BASE, "parksyimage_accounts/client_secret.json"),
    "papyrus":     os.path.join(BASE, "papyrus_accounts/client_secret.json"),
}
TOKDIR = {
    "parksyimage": os.path.join(BASE, "parksyimage_accounts/accounts"),
    "papyrus":     os.path.join(BASE, "papyrus_accounts/accounts"),
}
DEFAULT_CHANNEL = "musician-parksy"


class YT:
    def __init__(self, slug):
        self.slug = slug
        m = json.load(open(MAPFILE))
        key = f"token_{slug}.json"
        # papyrus 계정 토큰은 token_a.json 형태로도 존재
        if key not in m:
            key = f"{slug}.json" if f"{slug}.json" in m else key
        if key not in m:
            near = [k for k in m if slug in k]
            raise SystemExit(f"❌ 채널 '{slug}' 없음. 근접: {near or '없음'}\n"
                             f"   전체 보기: python3 scripts/ytch.py channels")
        self.meta = m[key]
        if "error" in self.meta:
            raise SystemExit(f"❌ '{slug}' 토큰 무효: {self.meta['error']}")
        self.group = self.meta["group"]
        self.channel_id = self.meta["id"]
        self.channel_name = self.meta["channel"]
        s = json.load(open(SECRETS[self.group]))
        s = s.get("installed") or s.get("web") or s
        self.cid, self.csec = s["client_id"], s["client_secret"]
        t = json.load(open(os.path.join(TOKDIR[self.group], key)))
        self.rt = t.get("refresh_token")
        if not self.rt:
            raise SystemExit(f"❌ '{slug}' 토큰에 refresh_token 없음")
        self._at = None

    @property
    def at(self):
        if self._at:
            return self._at
        d = urllib.parse.urlencode({"client_id": self.cid, "client_secret": self.csec,
                                    "refresh_token": self.rt, "grant_type": "refresh_token"}).encode()
        try:
            r = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data=d, timeout=30))
        except urllib.error.HTTPError as e:
            raise SystemExit(f"❌ [{self.slug}] 토큰 갱신 실패 HTTP {e.code}: {e.read().decode()[:200]}")
        self._at, self.scope = r["access_token"], r.get("scope", "")
        return self._at

    def req(self, url, method="GET", body=None, extra=None):
        h = {"Authorization": "Bearer " + self.at}
        if body is not None:
            h["Content-Type"] = "application/json"
        if extra:
            h.update(extra)
        data = json.dumps(body).encode() if body is not None else None
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h, method=method), timeout=120)
            b = r.read()
            return json.loads(b) if b else {}
        except urllib.error.HTTPError as e:
            raise SystemExit(f"❌ [{self.slug}] HTTP {e.code}: {e.read().decode()[:400]}")


def parse_args(argv):
    pos, opt, i = [], {}, 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            k = a[2:]
            if k == "confirm":
                opt[k] = True
            else:
                opt[k] = argv[i + 1]
                i += 1
        else:
            pos.append(a)
        i += 1
    return pos, opt


# ---------- 명령 ----------
def cmd_channels(_p, _o):
    m = json.load(open(MAPFILE))
    print(f"{'슬러그':28s} {'채널':16s} {'구독':>4s} {'영상':>4s}  upload  ID")
    for k, v in sorted(m.items(), key=lambda x: x[0]):
        slug = k.replace("token_", "").replace(".json", "")
        if "error" in v:
            print(f"{slug:28s} ❌ {v['error'][:40]}")
            continue
        print(f"{slug:28s} {v['channel']:16s} {v.get('subs','?'):>4} {v.get('videos','?'):>4}  "
              f"{'Y' if v.get('upload_scope') else 'N':^6s}  {v['id']}")


def cmd_whoami(_p, o):
    y = YT(o.get("channel", DEFAULT_CHANNEL))
    d = y.req(f"{API}/channels?part=snippet,statistics&mine=true")
    for it in d.get("items", []):
        s, st = it["snippet"], it["statistics"]
        tag = "★ 지도와 일치" if it["id"] == y.channel_id else "⚠️ 지도와 불일치!"
        print(f"{tag} {s['title']} | {it['id']} | 구독 {st.get('subscriberCount')} 영상 {st.get('videoCount')}")
    print(f"  슬러그: {y.slug} · 그룹: {y.group} · 업로드 스코프: {'Y' if 'upload' in getattr(y,'scope','') else 'youtube.full'}")


def cmd_playlists(_p, o):
    y = YT(o.get("channel", DEFAULT_CHANNEL))
    d = y.req(f"{API}/playlists?part=snippet,contentDetails&mine=true&maxResults=50")
    for it in d.get("items", []):
        print(f"{it['id']}  {it['contentDetails']['itemCount']:>3}개  {it['snippet']['title']}")


def cmd_videos(_p, o):
    y = YT(o.get("channel", DEFAULT_CHANNEL))
    if o.get("playlist"):
        d = y.req(f"{API}/playlistItems?part=snippet&playlistId={o['playlist']}&maxResults=50")
        for it in d.get("items", []):
            sn = it["snippet"]
            print(f"{sn['resourceId'].get('videoId')}  {sn['title']}")
    else:
        d = y.req(f"{API}/search?part=snippet&channelId={y.channel_id}&maxResults=50&type=video&order=date")
        for it in d.get("items", []):
            sn = it["snippet"]
            print(f"{it['id']['videoId']}  {sn['publishedAt'][:10]}  {sn['title']}")


def cmd_add(p, o):
    if len(p) < 2:
        raise SystemExit("usage: add <playlistId> <videoId> [--channel S]")
    y = YT(o.get("channel", DEFAULT_CHANNEL))
    r = y.req(f"{API}/playlistItems?part=snippet", "POST",
              {"snippet": {"playlistId": p[0], "resourceId": {"kind": "youtube#video", "videoId": p[1]}}})
    print(f"✅ 추가됨: {r['id']} → {p[0]}")


def cmd_upload(p, o):
    slug = o.get("channel", DEFAULT_CHANNEL)
    if not p:
        raise SystemExit("usage: upload <file> --title T [--desc D] [--tags a,b] "
                         "[--privacy private|unlisted|public] [--playlist PLID] [--channel S] [--confirm]")
    path = p[0]
    if not os.path.exists(path):
        raise SystemExit(f"❌ 파일 없음: {path}")
    size = os.path.getsize(path)
    title = o.get("title") or os.path.basename(path)
    privacy = o.get("privacy", "private")
    if not o.get("confirm"):
        y = YT(slug)
        print("── 업로드 계획 (실행 안 함 — 자동 업로드 금지) ──")
        print(f"  채널   : {y.channel_name} ({y.channel_id})")
        print(f"  파일   : {path}  ({size/1e6:.1f} MB)")
        print(f"  제목   : {title}")
        print(f"  공개   : {privacy}")
        print(f"  재생목록: {o.get('playlist', '(없음)')}")
        print("  실행하려면 --confirm 추가 (Boss 검수 후).")
        return
    y = YT(slug)
    meta = {"snippet": {"title": title, "description": o.get("desc", ""),
                        "tags": [t for t in o.get("tags", "").split(",") if t],
                        "categoryId": o.get("category", "10"), "channelId": y.channel_id},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}}
    init = urllib.request.Request(
        f"{UPLOAD}/videos?uploadType=resumable&part=snippet,status", data=json.dumps(meta).encode(),
        headers={"Authorization": "Bearer " + y.at, "Content-Type": "application/json",
                 "X-Upload-Content-Type": "video/*", "X-Upload-Content-Length": str(size)}, method="POST")
    loc = urllib.request.urlopen(init, timeout=60).headers.get("Location")
    with open(path, "rb") as f:
        put = urllib.request.Request(loc, data=f.read(),
                                     headers={"Content-Type": "video/*", "Content-Length": str(size)}, method="PUT")
        r = json.load(urllib.request.urlopen(put, timeout=1800))
    print(f"✅ 업로드: https://youtu.be/{r['id']}  ({r['snippet']['title']})")
    if o.get("playlist"):
        cmd_add([o["playlist"], r["id"]], {"channel": slug})


CMDS = {"channels": cmd_channels, "whoami": cmd_whoami, "playlists": cmd_playlists,
        "videos": cmd_videos, "add": cmd_add, "upload": cmd_upload}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        raise SystemExit(__doc__.strip() + "\n\n명령: " + " · ".join(CMDS))
    pos, opt = parse_args(sys.argv[2:])
    CMDS[sys.argv[1]](pos, opt)
