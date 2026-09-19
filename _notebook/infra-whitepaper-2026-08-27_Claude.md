# 🏭 proot Ubuntu (Galaxy S25) — 1인 미디어 공장 기술백서

> 작성: _Claude · 2026-08-27 · SSOT: dtslib-papyrus · 이 CLI = S25 Ultra

## 0. 한 줄 평가
**"부품 80% + 티스토리·GitHub 실전 가동. '원클릭 자동 발행' 공장은 아직."**

## 1. 하드웨어 (실측)
- Galaxy S25 Ultra (SM-S938N · Snapdragon 8 Elite · soc_id=618 · 12GB · Adreno 830)
- proot Ubuntu (aarch64) · Termux · `/root/work`

## 2. 계정·세계 구조 (4계정 4세계)
| 세계 | Google | 방송 | 기기 |
|------|--------|------|------|
| b | dtslib1979 | 경제방송 (16레포·10블로그·6채널) | **S25 (이 공장)** |
| c | thomas.tj.park | 교육방송 EAE (edu_art_engineer) | 탭 |
| a | dimas.thomas.sancho | 아리랑/KR (parksy_kr) | 보류 |
| — | helena751107 | 양산 노드 | S21 |

## 3. 플랫폼별 자동화 상태
| 플랫폼 | 상태 | 비고 |
|--------|------|------|
| 티스토리 10블로그 | ✅ **실전 가동** | 스킨·GEO·웹툰플레이어 10/10 (라이브) |
| GitHub Pages | ✅ 가동 (PWA 반쪽) | build_webzine md→html + GEO |
| 네이버 3계정 | ⚠️ 이식완료·미테스트 | login/post.cjs chromium 이식 + ax6-tap.js 배포 |
| YouTube 6채널 | ⚠️ OAuth 미연결 | 쿼터 60k(09-23 만료) + yt_upload.py |
| Instagram/Threads 1 | ❌ 미구현 | 플라이어(JS6) 방향 확정 |
| Telegram | ✅ | tg.sh 보고 |

## 4. 자동화 기반 (오늘 확립)
ADB(Shizuku 5900 인증) ✅ · AutoJS6(v6.7.0+접근성) ✅ · SMS 무인판독 ✅ · Playwright chromium ✅ · SSOT(ecosystem.json 16레포) ✅

## 5. 갭 (남은 것)
1. 자동발행 트리거(cron/watcher) 2. YouTube OAuth 3. 네이버 발행 첫 테스트 4. PWA 서비스워커 5. 웹툰 컨텐츠생성(parksy-image 미클론) 6. booklet.css

## 6. 다음 액션 (우선순위)
① 자동발행 트리거 → ② YouTube OAuth → ③ 네이버 발행 테스트 → ④ PWA 서비스워커

*_Claude · 2026-08-27 · proot Ubuntu Galaxy S25*
