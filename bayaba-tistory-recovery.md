# bayaba 티스토리 스킨 적용 — 만회 실행 지침

> 대상: **bayaba-1979** 계정 · 5개 티스토리 블로그
> 상태: GitHub Pages 5개 / YouTube 5채널 / 티스토리 매칭 = **완료**. 남은 건 **스킨 자동 적용 1건뿐.**
> 실패 원인: **카카오 로그인 캡차를 기계로 뚫으려 함.** 정답은 "로그인 = 사람 게이트 1회, 그 이후가 자동".
> 실행 시점: **내일(2026-08-20) 아침 첫 시도.** 오늘은 로그인 손 떼기.

---

## 0. 오늘(08-19) 즉시 하지 말 것

| 금지 | 이유 |
|------|------|
| ❌ 로그인 재시도 | 캡차는 **반복이 유발**. 시도할수록 쿨다운만 늘어남 |
| ❌ OCR로 지도 캡차 풀기 | 지도 라벨은 사람 눈 판단용. 기계로 못 품 |
| ❌ xvfb / VNC / RustDesk 설치 | **불필요한 우회** (보일러플레이트 메모리에 명시) |
| ❌ `apply_skin.py` 사용 | **구식**(CSS만). 정식은 `batch_apply.py` |
| ❌ "비밀번호 틀림" 메시지 신뢰 | 카카오는 봇감지 시 오류가 일정하지 않음. 비번은 정확했음 |

---

## 1. 준비 — accounts.json 검증 (내일 실행 전, 1회)

`tistory-naver/accounts.json`(gitignored)을 bayaba 실제 값으로 채운다. `accounts.json.template`은 **양식 참고용**일 뿐 — 여기에 비번을 직접 채우는 게 아니라 `accounts.json`에.

```json
{
  "password": "<bayaba 카카오 비번>",
  "accounts": [
    {"id": "bayaba_phone",    "email": "s01084271775@gmail.com", "blog": "bayaba-phone"},
    {"id": "bayaba_log",      "email": "s01084271775@gmail.com", "blog": "bayaba-1979"},
    {"id": "bayaba_jokbal",   "email": "s01084271775@gmail.com", "blog": "bayaba-jokbal"},
    {"id": "bayaba_chicken",  "email": "s01084271775@gmail.com", "blog": "bayaba-chicken"},
    {"id": "bayaba_install",  "email": "s01084271775@gmail.com", "blog": "bayaba-installation"}
  ]
}
```

- 5개 블로그 = **카카오 1계정 공유** → 로그인 1번이면 5블로그 전부 커버.
- `blog` 값은 티스토리 서브도메인 slug (`.tistory.com` 앞부분).

---

## 2. 내일 아침 — 경로 A (정상, 권장): headless 첫 시도

**핵심 원리:** 기기 IP + **하루 첫 시도**는 보통 캡차 없이 로그인된다. 캡차는 반복 로그인이 유발한 것. → **단 한 번, 깨끗하게.**

```bash
# ① 환경 확인 (Termux bionic vs Ubuntu glibc ABI 함정 회피)
which python3           # 반드시 /usr/bin/python3 (Ubuntu) — /data/data/com.termux/... 이면 오답
/usr/bin/python3 --version

# ② playwright 없으면 Ubuntu pip로 설치
/usr/bin/python3 -m pip install playwright --break-system-packages
/usr/bin/python3 -m playwright install chromium   # (이미 되어 있으면 생략)

# ③ 로그인 1회 + 5블로그 세션 시드 (headless, 첫 시도)
cd /root/work
python3 tistory-naver/renew_sessions.py

# ④ 위 ③이 "✅ 전 블로그 세션 유효"로 끝나야 함.
#    exit code 0 = 성공. 그대로 아래 §3으로.
```

- `renew_sessions.py`는 로그인 1회 → TSSESSION을 **+7일로 보정해 영속화** → 5개 블로그에 시드 → manage URL 실측 probe까지 한다.
- **절대 반복 실행 금지.** 실패하면 그날은 멈추고 다음날. (경로 B로 갈 수도 있음)

---

## 3. 스킨 일괄 적용 — batch_apply.py

세션이 유효해진 뒤에만 (로그인 성공 후):

```bash
python3 tistory-naver/batch_apply.py            # 5개 전부
python3 tistory-naver/batch_apply.py --only bayaba_jokbal   # 하나만 시험
python3 tistory-naver/batch_apply.py --dry-run  # 저장 없이 미리 확인
```

이 스크립트가 하는 일 (블로그마다):
1. 스킨 전환 `POST /manage/design/skin/set.json {name:"pg_Whatever"}`
2. `GET /manage/design/skin/html.json` → HTML+CSS 주입
3. `POST html.json` 저장 → 재조회로 **마커 검증**(`html_marker=True` / `css_marker=True`)

**주의 — 테마:** `batch_apply.py`는 `apply_layout.py`의 `THEME_MAP`을 `id`로 찾는다. bayaba id가 없으면 **기본 테마(틸/골드)**로 떨어진다. → 1차로는 "기본 테마로 전부 적용"이 목표. 테마 개별화는 스킨이 다 붙은 **다음 단계**에서 `apply_layout.py`의 `THEME_MAP`에 bayaba id를 추가.

---

## 4. 캡차가 떴다면 — 경로 B (화면 있는 기기 1회)

headless 첫 시도(§2-③)에서 `"답해 주세요"` 캡차가 뜨면, **반복하지 말고** 화면 있는 기기(S21 폰 / 태블릿)에서:

```bash
# 화면 있는 기기의 proot에서, 사람이 직접 지도 캡차 클릭 (1회)
python3 tistory-naver/renew_sessions.py --headed
```

1. 사람이 지도 캡차(POI 라벨)를 **직접 클릭** → 로그인 완료.
2. 성공하면 `tistory-naver/cookies/` 에 `*_state.json` + persistent profile이 저장됨.
3. 그 `cookies/` 디렉토리 + `accounts.json` 을 **헤드리스 머신으로 복사**:

```bash
rsync -av tistory-naver/cookies/ <headless-ip>:/root/work/tistory-naver/cookies/
scp tistory-naver/accounts.json <headless-ip>:/root/work/tistory-naver/accounts.json
```

4. 헤드리스 머신에서 `batch_apply.py` 실행 → **캡차 없이** 스킨 적용 (저장된 TSSESSION 재사용).

> ⚠️ bayaba 카카오는 **새 계정**이라, 기존 S21의 cookies(helena/eae 계정)를 복사해도 **계정이 달라 못 씀.** 반드시 bayaba 계정으로 로그인한 cookies여야 한다.

---

## 5. 환경 체크리스트 (친구 머신에서 반복된 삽질 방지)

| 증상 | 원인 | 정답 |
|------|------|------|
| `pip install playwright` → No matching distribution | Termux pip(3.14 bionic)이 PATH에 섞임 | `/usr/bin/python3 -m pip`로 명시 |
| `No module named pip` | Ubuntu python에 pip 없음 | `apt install python3-pip python3-venv` |
| `externally-managed-environment` | PEP 668 | `--break-system-packages` |
| 스킨 안 붙음 | `apply_skin.py`(구식) 씀 | `batch_apply.py`(정식) |
| 캡차 무한 | headless 반복 로그인 | 하루 1회 + 쿨다운 15~30분 |

**기억:** 이 머신은 **proot Ubuntu(glibc)**. Termux(bionic)의 python/pip을 쓰면 안 됨. 항상 `/usr/bin/python3` 경로 확인.

---

## 6. 검증 (완료 선언 전에 반드시)

```bash
# ① 세션 유효성
python3 tistory-naver/renew_sessions.py --dry-run   # 전부 ✅ 여야 함

# ② 스킨 적용 확인 (각 블로그 manage 페이지에 마커 존재)
curl -s https://bayaba-phone.tistory.com/manage | grep -c HELENA   # (로그인 쿠키 필요 시 renew 후)
```

스킨이 실제 반영됐는지는 **블로그 프론트**(`https://bayaba-phone.tistory.com/`)에서 다크 배경 + S21 시그니처(테두리/카메라 모듈) 렌더 확인이 최종 증거.

---

## 7. 보안 — 지금 당장 조치

1. **카카오 비번이 작업 로그에 평문 노출됨** → 카카오 계정 비밀번호 **즉시 재발급** (계정 → 보안 → 비밀번호 변경).
2. 이후 비번은 **`accounts.json`(gitignored)에만**, 수첩·로그·커밋에 절대 금지.
3. `.gitignore`에 `tistory-naver/accounts.json` + `tistory-naver/cookies/` 포함 확인 (기본 보일러플레이트에 이미 있음).
4. 재발급한 비번으로 §1의 `accounts.json`을 갱신한 뒤 실행.

---

## 8. 재발 방지 체크리스트

- [ ] 카카오/티스토리 로그인 = **화면 있는 기기 or 하루 첫 headless 1회**. CI/headless 반복 금지.
- [ ] `which python3` / `which pip` 먼저 확인 (Termux bionic vs Ubuntu glibc ABI).
- [ ] 스킨 적용은 `batch_apply.py` (구식 `apply_skin.py` 아님).
- [ ] 캡차 반복 시도 금지 — 쿨다운만 늘어남.
- [ ] "비밀번호 틀림" 메시지 그대로 믿지 말 것 — 봇감지 오류일 수 있음.
- [ ] 시크릿은 `.secrets.env` / `accounts.json`(gitignored)에만. 로그·커밋에 평문 금지.

---

*만회 지침 · 2026-08-19 작성 · 2026-08-20 첫 실행용 · 에이전트 마크 `_Claude`*
