// ax6-ig-threads.js — 인스타/스레드 통합계정(edu_art_engineer) AutoJS6 실터치 로그인
// 네이버(ax6-tap.js)와 동일 원칙: CDP/Playwright 지문 없음, accessibility 실터치만 사용.
"auto";
auto.waitFor();
auto.setMode("fast");

var ACCOUNT = { id: "edu_art_engineer", username: "edu_art_engineer", pw: "think4good*" };

var LOG = "/sdcard/Download/ax6-ig-threads.log";
function log(msg) {
    files.append(LOG, "[" + new Date().toLocaleTimeString() + "] " + msg + "\n");
}

function hit(label, timeout) {
    timeout = timeout || 1200;
    var w = text(label).findOne(timeout);
    if (!w) w = textContains(label).findOne(400);
    if (!w) w = desc(label).findOne(400);
    if (!w) w = descContains(label).findOne(400);
    return w;
}

// Chrome 자동입력(저장된 비밀번호) 바텀시트 — 뜨면 뒤로가기로 닫고 계속 (OS 설정 안 건드림)
function dismissAutofillSheet() {
    if (hit("저장된 비밀번호", 600) || hit("자동 완성", 500)) {
        log("자동입력 시트 감지 → 뒤로가기로 닫음");
        back();
        sleep(500);
        return true;
    }
    return false;
}

function loginInstagram() {
    log("=== " + ACCOUNT.id + " Instagram 로그인 시작 ===");
    app.startActivity({
        action: "android.intent.action.VIEW",
        data: "https://www.instagram.com/accounts/login/",
        packageName: "com.android.chrome"
    });
    sleep(4000);

    // "로그인 또는 가입" 링크는 혼합 스타일 텍스트(회색+파란색 스팬)라 접근성 노드
    // text() 매칭이 불안정함(2026-08-27 실측). 실측 확인된 좌표 실터치로 대체.
    // 좌표는 이 태블릿(2560x1600) 화면 실측값 — 다른 기기 이식 시 재측정 필요.
    var formReady = false;
    for (var t = 0; t < 6 && !formReady; t++) {
        if (hit("휴대폰 번호", 800)) { formReady = true; break; }
        click(1856, 1312);
        sleep(1200);
    }
    if (!formReady) { log("FAIL: 로그인폼 진입 실패(좌표 탭 반복 실패)"); return "FAIL_NO_LOGIN_FORM"; }

    // 아이디 필드 — 주소창(omnibox)도 editable로 잡히므로 화면 상단(y<300, 주소창 영역)은 제외.
    function pageEditables() {
        return editable().find().toArray().filter(function (n) {
            return n.boundsInScreen().top > 300;
        });
    }
    var candidates = [];
    for (var i = 0; i < 6 && candidates.length === 0; i++) {
        sleep(500);
        candidates = pageEditables();
    }
    if (candidates.length === 0) { log("FAIL: 아이디 필드 없음(주소창 제외 후)"); return "FAIL_NO_ID_FIELD"; }
    var idField = candidates[0];
    idField.click(); sleep(400);
    dismissAutofillSheet();
    idField.setText(ACCOUNT.username);
    sleep(300);
    dismissAutofillSheet();

    var fields = pageEditables();
    if (fields.length < 2) { log("FAIL: 비밀번호 필드 없음"); return "FAIL_NO_PW_FIELD"; }
    var pwField = fields[1];
    pwField.click(); sleep(400);
    dismissAutofillSheet();
    pwField.setText(ACCOUNT.pw);
    sleep(300);
    dismissAutofillSheet();

    var loginBtn = hit("로그인", 1500);
    if (!loginBtn) { log("FAIL: 로그인 버튼 없음"); return "FAIL_NO_BUTTON"; }
    loginBtn.click();
    sleep(4000);

    // reCAPTCHA 이미지 챌린지 벽 — 실행 중단, 사람(또는 상위 세션)이 이미지 판별 후 이어서 처리
    if (hit("로봇이 아닙니다", 1000) || hit("reCAPTCHA", 1000)) {
        log(ACCOUNT.id + " → reCAPTCHA 이미지 챌린지 벽 도달 (스크린샷 판별 후 수동 이어서)");
        return "WALL_RECAPTCHA";
    }
    // WhatsApp/SMS 코드 인증 벽
    if (hit("WhatsApp 메시지", 1000) || hit("확인하세요", 800)) {
        log(ACCOUNT.id + " → WhatsApp/SMS 코드 인증 벽 도달 (등록기기에서 코드 확인 필요)");
        return "WALL_CODE";
    }
    log(ACCOUNT.id + " → 로그인 시도 완료 (결과 스크린샷으로 확인 필요)");
    return "SUBMITTED";
}

// Threads는 별도 로그인이 필요 없음 — Instagram 세션이 살아있으면
// threads.com 접속 시 "Instagram으로 계속하기(edu_art_engineer)" 브릿지
// 버튼이 자동으로 뜨고, 클릭 한 번으로 완전히 로그인됨(2026-08-27 실측 —
// 캡차/OTP 벽 전혀 없음). 그래서 Instagram 로그인 완주 후 이 함수만
// 이어 붙이면 됨.
function loginThreadsViaInstagramBridge() {
    log("=== Threads Instagram 브릿지 로그인 시작 ===");
    app.startActivity({
        action: "android.intent.action.VIEW",
        data: "https://www.threads.com/",
        packageName: "com.android.chrome"
    });
    sleep(4000);
    var bridge = hit("Instagram으로 계속하기", 3000);
    if (!bridge) {
        // 이미 로그인된 상태로 바로 피드가 뜨는 경우도 있음(재실행 시)
        if (hit("추천", 1500) || hit("새로운 스레드", 1500)) {
            log("Threads → 이미 로그인 상태로 피드 진입됨");
            return "ALREADY_LOGGED_IN";
        }
        log("FAIL: Instagram 브릿지 버튼 없음");
        return "FAIL_NO_BRIDGE_BUTTON";
    }
    bridge.click();
    sleep(4000);
    if (hit("추천", 2000) || hit("새로운 스레드", 1500)) {
        log("Threads → 브릿지 로그인 완주, 피드 진입 확인");
        return "SUBMITTED";
    }
    log("Threads → 브릿지 클릭 완료(결과 스크린샷으로 확인 필요)");
    return "SUBMITTED_UNCONFIRMED";
}

var igResult = loginInstagram();
var results = { instagram_login: igResult };
// Instagram 로그인이 완주됐거나 이미 세션이 있는 경우에만 Threads 이어서 진행
if (igResult === "SUBMITTED" || igResult === "WALL_RECAPTCHA" || igResult === "WALL_CODE") {
    results.threads_login = loginThreadsViaInstagramBridge();
}
files.write("/sdcard/Download/ax6-ig-threads-result.json", JSON.stringify(results));
log("=== 완료: " + JSON.stringify(results) + " ===");
toast("ax6-ig-threads done: " + JSON.stringify(results));
