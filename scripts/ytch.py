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


BOOL_FLAGS = {"confirm", "sync"}


def parse_args(argv):
    pos, opt, i = [], {}, 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            k = a[2:]
            if k in BOOL_FLAGS:
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


# ---------- 레저(공개/비공개 레인) ----------
POLICY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "configs", "publish-policy.json")
LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "configs", "publish-ledger.json")


def _policy():
    return json.load(open(POLICY, encoding="utf-8"))


def _ledger():
    if os.path.exists(LEDGER):
        return json.load(open(LEDGER, encoding="utf-8"))
    return {"updated": None, "videos": {}}


def _save_ledger(led):
    import datetime
    led["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
    json.dump(led, open(LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def _set_privacy(y, vid, privacy):
    cur = y.req(f"{API}/videos?part=status&id={vid}")["items"][0]["status"]
    cur["privacyStatus"] = privacy
    y.req(f"{API}/videos?part=status", "PUT", {"id": vid, "status": cur})


def cmd_ledger(_p, o):
    """현재 공개/비공개 상태를 레저로 뽑는다. --sync 면 API에서 새로 읽는다."""
    y = YT(o.get("channel", DEFAULT_CHANNEL))
    led = _ledger()
    if o.get("sync"):
        ids, tok = [], None
        while True:
            u = f"{API}/playlistItems?part=snippet&playlistId=UU{y.channel_id[2:]}&maxResults=50" + (f"&pageToken={tok}" if tok else "")
            d = y.req(u); ids += [i["snippet"]["resourceId"]["videoId"] for i in d["items"]]
            tok = d.get("nextPageToken")
            if not tok:
                break
        import datetime
        seen = set()
        for i in range(0, len(ids), 50):
            d = y.req(f"{API}/videos?part=status,snippet&id={','.join(ids[i:i+50])}")
            for v in d["items"]:
                vid = v["id"]; seen.add(vid)
                rec = led["videos"].get(vid, {})
                rec["title"] = v["snippet"]["title"]
                rec["published_at"] = v["snippet"]["publishedAt"][:10]
                rec["privacy"] = v["status"]["privacyStatus"]
                # API 상태로부터 추정 — 공개면 published, 아니면 기존 기록 유지(없으면 draft)
                if v["status"]["privacyStatus"] == "public":
                    rec.setdefault("state", "published")
                    rec["state"] = "published"
                else:
                    rec.setdefault("state", "draft")
                    rec.setdefault("first_seen", datetime.datetime.now().isoformat(timespec="seconds"))
                led["videos"][vid] = rec
        _save_ledger(led)
        print(f"동기화: {len(seen)}편")
    from collections import Counter
    c = Counter(v.get("state", "?") for v in led["videos"].values())
    p = _policy()["states"]
    print(f"레저 {len(led['videos'])}편 · 갱신 {led.get('updated')}")
    for s, n in c.most_common():
        st = p.get(s, {})
        print(f"  {s:10s} {st.get('ko','?'):6s} → {st.get('privacy','?'):8s} {n:>3d}편")
    print("\n※ 공개(published)는 Boss 결재 기록이 있어야 코드가 허용한다.")


def cmd_stage(p, o):
    """상태 전이. published는 결재 기록 없으면 거부된다."""
    if len(p) < 2:
        raise SystemExit("usage: stage <videoId> <draft|review|approved|published|retired> [--by NAME] [--channel S]")
    vid, target = p[0], p[1]
    pol = _policy()
    if target not in pol["states"]:
        raise SystemExit(f"❌ 없는 상태: {target} (가능: {', '.join(pol['states'])})")
    led = _ledger()
    rec = led["videos"].setdefault(vid, {"title": ""})
    cur = rec.get("state", "draft")
    st = pol["states"][target]

    import datetime
    now = datetime.datetime.now().isoformat(timespec="seconds")
    # 게이트: 사람 결재가 필요한 상태
    if st.get("by") == "boss" and not (o.get("by") or rec.get("approved_by")):
        raise SystemExit(
            f"⛔ 거부 — '{target}'({st['ko']})는 Boss 결재가 필요한 전이다.\n"
            f"   자동화는 절대 공개하지 않는다 (rule: {pol['rules']['note']})\n"
            f"   쓰는 법: stage {vid} {target} --by Boss"
        )
    if st.get("by") == "boss" and o.get("by"):
        rec["approved_by"] = o["by"]
        rec["approved_at"] = now

    trans = f"{cur}->{target}"
    if cur != target and trans not in pol["transitions"] and not (o.get("by")):
        raise SystemExit(f"⛔ 정의되지 않은 전이: {trans} (policy.transitions 참조)")

    y = YT(o.get("channel", DEFAULT_CHANNEL))
    if pol["rules"].get("enforce_privacy"):
        _set_privacy(y, vid, st["privacy"])
    rec["state"] = target
    rec["privacy"] = st["privacy"]
    rec["changed_at"] = now
    rec["history"] = rec.get("history", []) + [{"at": now, "from": cur, "to": target, "by": o.get("by", st.get("by"))}]
    _save_ledger(led)
    print(f"✅ {vid}  {cur} → {target} ({st['ko']})  privacy={st['privacy']}"
          + (f"  · 결재: {o['by']}" if o.get("by") else ""))


def cmd_publish(p, o):
    """결재 후 공개. --by 없으면 무조건 거부."""
    if not p:
        raise SystemExit("usage: publish <videoId> --by Boss [--channel S]")
    if not o.get("by"):
        raise SystemExit("⛔ 거부 — 공개는 Boss 결재 없이 불가. --by Boss 를 명시하라.")
    cmd_stage([p[0], "published"], o)


CMDS = {"channels": cmd_channels, "whoami": cmd_whoami, "playlists": cmd_playlists,
        "videos": cmd_videos, "add": cmd_add, "upload": cmd_upload,
        "ledger": cmd_ledger, "stage": cmd_stage, "publish": cmd_publish}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        raise SystemExit(__doc__.strip() + "\n\n명령: " + " · ".join(CMDS))
    pos, opt = parse_args(sys.argv[2:])
    CMDS[sys.argv[1]](pos, opt)
