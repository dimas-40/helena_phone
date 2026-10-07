#!/usr/bin/env python3
"""48칸 대시보드(index.html)를 큐 표에서 생성한다.

    python3 scripts/pd_dashboard.py            # 쓰기
    python3 scripts/pd_dashboard.py --check    # 개수만 확인

왜 생성하나: 48줄을 손으로 적으면 반드시 틀린다. 칸은 정확히 48개여야 하고
(플루치크 정본 = 기본 8×3 + dyad 8+8+8), 곡은 서로 겹치면 안 된다.
아래 QUEUE 가 정본이다 — 곡을 완성하면 그 줄의 slug 만 채우면 된다.

칸 이름과 곡 후보의 출처는 수첩 122·123 이다. 내가 지어낸 목록이 아니다.
"""
import sys
from pathlib import Path

OUT = Path("/root/work/midi_lane/pd/02-bach-prelude-c/site/index.html")

# (번호, 곡, 작곡가·연도, 칸, 슬러그)  — 슬러그가 있으면 완성된 페이지
QUEUE = [
    ("01", "짐노페디 제1번", "Erik Satie, 1888", "슬픔 · 생각에 잠김", "01-satie-gymnopedie"),
    ("02", "프렐류드 C장조, BWV 846", "J. S. Bach, 1722", "신뢰 · 수용", "02-bach-prelude-c"),
    ("03", "빗방울 전주곡", "Frédéric Chopin, 1839", "슬픔 · 슬픔", "03-chopin-raindrop"),
    ("04", "월광 소나타 1악장", "Ludwig van Beethoven, 1801", "슬픔 · 비통", "04-beethoven-moonlight"),
    ("05", "트로이메라이 Op.15 No.7", "Robert Schumann, 1838", "신뢰 · 신뢰", "05-schumann-traumerei"),
    ("06", "전주곡 올림다단조 Op.3 No.2", "Sergei Rachmaninoff, 1892", "분노 · 분노", "06-rachmaninoff-csm"),
    ("07", "사랑의 꿈 No.3", "Franz Liszt, 1850", "사랑 (기쁨+신뢰)", "07-liszt-liebestraum"),
    ("08", "발라드 No.1", "Frédéric Chopin, 1835", "회한 (슬픔+혐오)", "08-chopin-ballade1"),
    ("09", "리스트 9번 4악장 발췌", "Beethoven–Liszt, 편곡 1850 · 연주 1972", "희망 (기대+신뢰)", "09-beethoven-liszt-9th"),
    ("10", "야상곡 Op.9 No.2", "Frédéric Chopin, 1832", "감상 (신뢰+슬픔)", "10-chopin-nocturne9-2"),
    ("11", "발트슈타인 1악장", "Ludwig van Beethoven, 1804", "낙관 (기대+기쁨)", "11-beethoven-waldstein-1"),
    ("12", "오렌지 3개의 사랑 — 행진곡", "Sergei Prokofiev, 1919", "냉소 (혐오+기대)", None),
    ("13", "혁명 에튀드 Op.10 No.12", "Frédéric Chopin, 1831", "분노 · 격분", "13-chopin-revolutionary"),
    ("14", "환상즉흥곡 Op.66", "Frédéric Chopin, 1834", "기대 · 기대", "14-chopin-fantaisie-impromptu"),
    ("15", "장송행진곡 Op.35 3악장", "Frédéric Chopin, 1839", "절망 (공포+슬픔)", "15-chopin-funeral-march"),
    ("16", "군대 폴로네즈 Op.40 No.1", "Frédéric Chopin, 1838", "자부심 (분노+기쁨)", None),
    ("17", "침몰한 대성당", "Claude Debussy, 1910", "경외 (공포+놀람)", None),
    ("18", "악흥의 순간 Op.16 No.4", "Sergei Rachmaninoff, 1896", "시기 (슬픔+분노)", None),
    ("19", "왜? Op.12 No.3", "Robert Schumann, 1837", "죄책감 (기쁨+공포)", None),
    ("20", "즐거운 농부 Op.68 No.10", "Robert Schumann, 1848", "기쁨 · 평온", None),
    ("21", "터키행진곡 K.331 3악장", "Wolfgang A. Mozart, 1783", "기쁨 · 기쁨", None),
    ("22", "물레돌리는 노래 Op.67 No.4", "Felix Mendelssohn, 1845", "기쁨 · 환희", None),
    ("23", "캐논 (피아노 편)", "Johann Pachelbel, 1680경", "신뢰 · 존경", None),
    ("24", "전주곡 Op.28 No.6", "Frédéric Chopin, 1839", "순종 (신뢰+공포)", None),
    ("25", "아라베스크 No.1", "Claude Debussy, 1891", "호기심 (신뢰+놀람)", None),
    ("26", "도약 Op.12 No.2", "Robert Schumann, 1837", "기대 · 관심", None),
    ("27", "트롤하우겐의 결혼식날", "Edvard Grieg, 1896", "기대 · 경계", None),
    ("28", "전주곡 Op.28 No.2", "Frédéric Chopin, 1839", "공포 · 불안", None),
    ("29", "전주곡 Op.28 No.24", "Frédéric Chopin, 1839", "공포 · 공포", None),
    ("30", "민둥산의 하룻밤 (피아노 편)", "Modest Mussorgsky, 1867", "공포 · 극공", None),
    ("31", "퍽의 춤", "Claude Debussy, 1908", "놀람 · 산만", None),
    ("32", "놀람 교향곡 2악장 (피아노 편)", "Joseph Haydn, 1791", "놀람 · 놀람", None),
    ("33", "라 캄파넬라", "Franz Liszt, 1851", "놀람 · 경악", None),
    ("34", "짐노페디 No.3", "Erik Satie, 1888", "혐오 · 권태", None),
    ("35", "사르카즘 Op.17", "Sergei Prokofiev, 1914", "혐오 · 혐오", None),
    ("36", "알레그로 바르바로", "Béla Bartók, 1911", "혐오 · 역겨움", None),
    ("37", "전주곡 Op.28 No.22", "Frédéric Chopin, 1839", "분노 · 짜증", None),
    ("38", "비들로", "Modest Mussorgsky, 1874", "비난 (놀람+슬픔)", None),
    ("39", "미정", "", "멸시 (혐오+분노)", None),
    ("40", "토카타 Op.11", "Sergei Prokofiev, 1912", "공격성 (분노+기대)", None),
    ("41", "미정", "", "불신 (놀람+혐오)", None),
    ("42", "미정", "", "기쁨[3차] (기쁨+놀람)", None),
    ("43", "미정", "", "수치 (공포+혐오)", None),
    ("44", "미정", "", "격분[3차] (놀람+분노)", None),
    ("45", "미정", "", "비관 (슬픔+기대)", None),
    ("46", "미정", "", "병적 (혐오+기쁨)", None),
    ("47", "미정", "", "지배 (분노+신뢰)", None),
    ("48", "미정", "", "불안[3차] (기대+공포)", None),
]

HEAD = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>박씨 렌더링 — 퍼블릭 도메인 피아노 48칸</title>
<meta name="description" content="플루치크 감정 수레바퀴 48칸(기본 8×3 + dyad 8+8+8)에 퍼블릭 도메인 피아노를 한 곡씩 채우는 시리즈. 원곡 연주와, 음 단위로 채보해 다시 렌더한 연주를 한 트랙에 이어 붙였다.">
<link rel="canonical" href="https://parksy.kr/channel/musician/piano/">
<link rel="stylesheet" href="assets/piano.css">
<script>document.documentElement.className+=' js';</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
 {"@type":"Person","@id":"https://parksy.kr/#person","name":"박씨","url":"https://parksy.kr/",
  "sameAs":["https://parksy.kr/channel/musician/","https://www.youtube.com/channel/UCun6b2HD3ekp35PhqbTfOlg"]},
 {"@type":"CollectionPage","@id":"https://parksy.kr/channel/musician/piano/",
  "url":"https://parksy.kr/channel/musician/piano/",
  "name":"박씨 렌더링 — 퍼블릭 도메인 피아노 48칸",
  "inLanguage":"ko","author":{"@id":"https://parksy.kr/#person"},
  "publisher":{"@id":"https://parksy.kr/#person"},
  "about":{"@type":"Thing","name":"Plutchik 감정 수레바퀴 48칸 × 퍼블릭 도메인 피아노"}}
]}
</script>
<style>
  body{padding-bottom:0}
  header.pg{padding:4.6rem 0 2.4rem;border-bottom:1px solid var(--line2)}
  header.pg h1{font-size:clamp(2.2rem,5.4vw,3.3rem)}
  .count{font-family:var(--sans);font-size:.78rem;color:var(--dim);letter-spacing:.14em;
    margin:1.4rem 0 0;display:flex;gap:1.6rem;flex-wrap:wrap}
  .count b{color:var(--gold);font-variant-numeric:tabular-nums}
  .list{list-style:none;padding:0;margin:0}
  .list li{border-bottom:1px solid var(--line2)}
  .list .row{display:grid;grid-template-columns:3.2rem 1fr auto;gap:1.2rem;align-items:baseline;
    padding:1.35rem .9rem;margin:0 -.9rem;border-radius:8px;color:inherit;border-bottom:0}
  a.row{transition:background .3s var(--ease)}
  a.row:hover{background:rgba(255,255,255,.035)}
  .list .no{font-family:var(--mono);font-size:.82rem;color:var(--faint);letter-spacing:.12em;
    font-variant-numeric:tabular-nums}
  li.built .no{color:var(--gold)}
  .list .tt{font-size:1.1rem;font-weight:600;color:var(--ink2);display:block;line-height:1.5}
  li.built .tt{color:var(--ink)}
  a.row:hover .tt{color:var(--gold)}
  .list .mm{font-family:var(--sans);font-size:.78rem;color:var(--faint);display:block;margin-top:.3rem;line-height:1.7}
  .list .tag{font-family:var(--sans);font-size:.62rem;font-weight:700;letter-spacing:.16em;
    padding:.34rem .8rem;border-radius:100px;border:1px solid var(--line2);
    white-space:nowrap;color:var(--faint);transition:.3s}
  li.built .tag{border-color:rgba(217,164,65,.4);color:var(--gold)}
  a.row:hover .tag{color:var(--gold);border-color:rgba(217,164,65,.45)}
  li.done .tt::after{content:" ✓";color:var(--gold)}
  .note{font-family:var(--sans);font-size:.82rem;color:var(--faint);padding:2rem .9rem;
    margin:0 -.9rem;line-height:1.9;border-top:1px solid var(--line2)}
  .note b{color:var(--dim)}
  @media(max-width:620px){
    .list .row{grid-template-columns:2.4rem 1fr;gap:.5rem .9rem}
    .list .tag{grid-column:2;justify-self:start;margin-top:.45rem}
  }
</style>
</head>
<body>
<header class="pg"><div class="wrap">
  <p class="eyebrow">박씨 렌더링</p>
  <h1>퍼블릭 도메인 피아노<br>48칸</h1>
  <p class="lede" style="color:var(--ink2);font-size:1.06rem;margin:.6rem 0 0;max-width:36rem">
    원곡 연주와, 그것을 <b>음 단위로 받아 적어 다시 연주한 것</b>을
    한 트랙에 이어 붙여 듣는 페이지. 각 페이지에는 연주를 재서 얻은 숫자만 적었다.
  </p>
  <p class="count">
    <span>완성 <b>%d</b> / 48</span>
    <span>· 기본 8감정 × 강도 3단 <b>24</b></span>
    <span>· dyad 1차 <b>8</b> · 2차 <b>8</b> · 3차 <b>8</b></span>
  </p>
</div></header>

<main class="wrap">
  <ul class="list">
"""

TAIL = """  </ul>
  <p class="note">
    <b>칸은 플루치크 정본 48개다.</b> 기본 8감정 × 강도 3단 = 24칸, 그리고 두 감정의 곱인 dyad 24칸
    (1차 8 + 2차 8 + 3차 8). 8개 중 둘을 고르는 경우의 수 28 = dyad 24 + 반대축 4라서 빠짐없이 맞는다.
    목록 설계는 수첩 122·123.<br>
    <b>연주 녹음은 Wikimedia Commons 에서 라이선스가 명시된 것만</b> 골랐다
    (1호 Public domain · 2호 CC0 1.0 · 3호 CC BY 3.0 — 연주자 본인 배포, SHA-1 대조).
    4호는 <b>퍼블릭 도메인으로 배포된 녹음인데 연주자 이름이 없다</b> — 그래서 4호 페이지에는
    "연주자를 모르는 파일을 쓴다"고 적어 두었다. 모르는 것은 모른다고 적는다.<br>
    재현 렌더는 <b>Salamander Grand Piano V3</b> 샘플 (Alexander Holm, Yamaha C7 실녹음, CC BY 3.0)로
    <b>폰에서 직접</b> 친다.<br>
    작곡가 사망연도는 <b>업로드 전에 곡마다 다시 확인한다</b> — 이 표의 연도는 후보를 고르기 위한 것이다.
  </p>
</main>

<footer><div class="wrap">
  <p class="caveat" style="margin:0">
    원곡의 작곡은 퍼블릭 도메인이지만, <b>그 연주·그 녹음의 권리는 별개</b>다.
    우리가 내보내는 것은 원본 녹음의 복제가 아니라 <b>음 단위로 받아 적어 다시 연주한 것</b>이다.
    그런데도 채보 자체가 녹음의 2차적저작물이라는 논란이 가능한 <b>회색지대</b>이고,
    법률 검토를 받은 적은 없다. 지금은 <b>권리자가 곧 라이선서인 녹음만</b> 골라 쓰는 것으로 위험을 줄이고 있다.
  </p>
</div></footer>
</body>
</html>
"""


def row(no, title, meta, cell, slug):
    done = slug is not None
    mark = "" if title != "미정" else " — 미정"
    if done:
        return ('    <li class="built"><a class="row" href="%s/">\n'
                '      <span class="no">%s</span>\n'
                '      <span><span class="tt">%s</span>'
                '<span class="mm">%s</span></span>\n'
                '      <span class="tag">%s</span>\n'
                '    </a></li>\n' % (slug, no, title, meta, cell))
    inner = ('<span class="tt">%s</span><span class="mm">%s</span></span>'
             % ('미정' if title == "미정" else title, meta or "후보 탐색 중"))
    return ('    <li class="todo"><div class="row">\n'
            '      <span class="no">%s</span>\n'
            '      <span>%s\n'
            '      <span class="tag">%s</span>\n'
            '    </div></li>\n' % (no, inner, cell))


def main():
    assert len(QUEUE) == 48, "칸이 48개가 아니다: %d" % len(QUEUE)
    cells = [q[3] for q in QUEUE]
    assert len(set(cells)) == 48, "칸이 겹친다"
    pieces = [q[1] for q in QUEUE if q[1] != "미정"]
    assert len(set(pieces)) == len(pieces), "같은 곡이 두 칸에 있다"
    built = sum(1 for q in QUEUE if q[4])
    html = HEAD % built + "".join(row(*q) for q in QUEUE) + TAIL
    if "--check" in sys.argv:
        print("칸 48 · 완성 %d · 곡 %d" % (built, len(pieces)))
        return
    OUT.write_text(html, encoding="utf-8")
    print("→ %s" % OUT)
    print("   칸 48 · 완성 %d · 예정 %d · 곡 미정 %d"
          % (built, 48 - built, sum(1 for q in QUEUE if q[1] == "미정")))


if __name__ == "__main__":
    main()
