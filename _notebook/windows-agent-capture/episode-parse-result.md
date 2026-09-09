# 파싱 결과 — 2026-09-09 에피소드 문서 (Windows 에이전트 포렌식)

> 원본: `episode-2026-09-09.md` (12546B/254줄, 검증 완료) · 파싱: Claude Code(레인2)

## ✅ 검증
- 파일 존재: `C:\Users\dtsli\박씨PC\로그\2026-09-09-세션-랩탑-WSL-WTG-포렌식.md`
- 크기/줄수 일치: 12546 bytes / 254줄 (에이전트 보고 12.5KB/253줄과 실질 일치)

## 핵심 파싱 결과 (내 이전 해석 정정 포함)

### 1. WSL 2개 = "의도된 2계층" (이전 내 말 정정!)
`Ubuntu 본진 + UbuntuMin 경량 복구판` — **찌꺼기가 아니라 설계된 2계층.**
- Ubuntu: 개발 본진 (Docker/git/python/node/Claude Code, 패키지 1294개)
- wsl-min(UbuntuMin): **mosh 원격 복구/상시접속용 경량판** (SSH가 WiFi↔LTE 전환 시 끊기는 문제 해결용)
- 단, wsl-min은 VHDX 소실로 현재 죽은 등록 (06-19 이주 시 이미 "VHD 없음" 기록)

### 2. WD Passport 2TB = 3역할 겸용
- T: WTG_EFI(0.5G) = 부팅 / W: WTG_WIN10(100G) = 복구 지휘소 / D: DATA(1762G) = 창고+WSL 본거지(D:\WSL\ext4.vhdx 269G)

### 3. WTG 복구 시스템의 정체
**"전원만 들어오면, 윈도우가 완전히 죽어도 USB 하나로 원격 복구(포맷 재설치 포함)"**
- 부팅플로우: 전원→WTG 부팅→자동로그인→NVMe 체크→(정상)Win11 복귀 68% / (죽음)응급모드(DeepSeek Agent+Tailscale)
- RECOVER.sh = diskpart clean→DISM Win11→bcdboot→setup-wsl→28레포 재구축 (포맷 수준)

### 4. 교차복구 원칙 (설계 의도 확정)
> "OS는 자기 자신을 못 고친다. WSL↔Windows 교차 복구."
> "박씨가 PC 앞에 없어도 전원만 들어오면 원격 복구 가능한 구조."

### 5. 진짜 적 = Windows Update 강제 재부팅 → 3중 방어
1) 예방(Update 차단) 2) 생존(AC리커버리+AutoAdminLogon+wsl-autostart+Tailscale) 3) 최후복구(WTG)

## 발견된 리스크 5
1. 기종 불일치 (문서 XPS15 9570 vs 실제 XPS13 9370) → 복구문서 교정 필요
2. wsl-min 소실 (mosh 레이어 미가동)
3. REBUILD.md 소실
4. Tailscale IP 드리프트 (문서값 vs 실측 불일치)
5. 백업은 존재 (D:\WSL\ubuntu-backup.tar 120GB, 05-18)

## 다음 액션 6 (미결)
1. wsl-min unregister or 재import
2. BIOS AC Power Recovery 설정
3. WTG 부팅 1회 실검증(F12)
4. 복구문서 기종 교정(9570→9370)
5. Tailscale IP 갱신
6. WSL Ubuntu 기동 → dtslib(100.90.83.128) 노드 온라인 복귀
