# 티스토리 카카오 캡차 — 설치 시 유의사항 (2026-08-22)

> 이전(bayaba 이식, 2026-08-19) 세션에서 이미 한 번 막혔던 문제. 재발 방지용.

## 문제 (bayaba 이식 로그에서 확인된 사실)

`batch_apply.py`로 카카오 로그인 시 **지도 클릭형 캡차(dkaptcha)**가 뜬다.
- headless 모드 → 캡차 iframe 자체가 로드 안 됨(봇감지)
- headless=False + xvfb-run → iframe은 로드되지만, Xvfb는 화면이 없는
  가상 디스플레이라 **사람이 지도를 볼 방법이 없음**
- OCR 시도 → 실패 확인됨 (지도 라벨 기울기/노이즈로 tesseract 판독 불가)
- 헤드리스 반복 로그인 → 카카오 봇감지 쿨다운만 늘어남 (하지 말 것)
- "비밀번호 일치하지 않습니다" 메시지 → 봇감지 오류일 수 있음, 비번 탓하지 말 것

## 해법 (2026-08-22 확정 — VNC/화면기기 이동 불필요)

Playwright는 Xvfb 안에 떠있는 화면을 `page.screenshot()`으로 그냥 이미지 파일로
뽑을 수 있다. VNC 설치나 화면 있는 기기로 옮길 필요 없이, 그 스크린샷 하나를
WSL Claude(집 PC)한테 보내면 거기서 눈으로 보고 클릭 좌표를 읽어줄 수 있다.

### 절차

1. `headless=False` + `xvfb-run`은 그대로 유지 (캡차 iframe 로드까지는 이미 검증됨)
2. 캡차 iframe(`#dkaptcha-*`)이 뜨면 OCR 시도하지 말고 즉시:
   ```python
   await page.screenshot(path="/root/work/tistory-naver/captcha_shot.png")
   ```
   찍고 스크립트를 그 지점에서 일시정지(`input()` 등으로 대기)
3. `captcha_shot.png`를 WSL Claude한테 전달 (scp 또는 텔레그램)
4. 좌표(x, y) 받으면:
   ```python
   await page.mouse.click(x, y)
   ```
   하고 이어서 진행
5. 계정당(dtslib1k@kakao.com, dtslib2k@kakao.com) **최초 로그인 때만** 캡차가 뜬다.
   한 번 통과하면 `cookies/{account}_state.json`에 세션이 저장되므로,
   그 계정 소속 나머지 4개 블로그는 재로그인 없이 순회 가능 — 계정 2개니까
   이 캡차 루프는 최대 2번만 타면 전체 10개 블로그 끝남.

## 체크리스트 (bayaba 로그 그대로 유효)

- [ ] `which pip` / `which python3` 먼저 확인 (Termux bionic vs Ubuntu glibc ABI 혼선 주의)
- [ ] pip 설치 시 `--break-system-packages` + `/usr/bin/python3 -m pip` 명시
- [ ] 스킨 적용은 `batch_apply.py` 사용 (`apply_skin.py`는 구식, CSS만 적용됨)
- [ ] 캡차 반복 시도 금지 — 쿨다운만 늘어남
- [ ] "비밀번호 틀림" 메시지를 그대로 믿지 말 것 — 봇감지 오류일 수 있음
- [ ] **계정이 2개(dtslib1k, dtslib2k)로 분리됨** — `batch_apply.py`가 "블로그 전부 같은
      카카오 계정" 가정으로 짜여있으니, email 기준으로 그룹핑해서 계정별로 따로 로그인 →
      해당 계정 소속 5개 블로그만 순회하는 방식으로 고쳐서 실행할 것

## 참고

- 이전 사례: bayaba(마왕가족) 이식 세션, 2026-08-19, 동일 증상으로 티스토리 스킨 적용만 실패
- 대상: `tistory-naver/accounts.json` 10개 블로그 (dtslib1k 5 + dtslib2k 5)
- SSOT: `hq/TISTORY-ENDPRODUCT-MAPPING-2026-08-22.md` (papyrus 커밋 6bc11ed)
