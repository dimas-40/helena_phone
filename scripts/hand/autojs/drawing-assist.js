// drawing-assist.js — 삼성 그리기 어시스트(Creative Studio) AutoJS6 자동화 v2
// 텍스트→이미지 / 사진 업로드→스타일 변경 / 워터마크 크롭 / 프리셋 44개
// ※ 실제 자동화는 ADB(MCP parksy-gallery)가 권장. 이 스크립트는 AutoJS6 단독 실행용.
"auto";
auto.waitFor();
auto.setMode("fast");

// ===== 설정 =====
var PROMPT = "cute golden retriever puppy";
var STYLE = "아르 누보"; // 기본값 (Boss 지정)
var PHOTO_INDEX = 0;    // restyle 시 박씨 갤러리 앨범 사진 인덱스 0~3
var CROP_BOTTOM = 8;    // 워터마크 하단 크롭 %

// ===== 스타일 10종 (태블릿 1600x2560, "모두 보기" 전체 그리드 좌표) =====
var STYLES = {
  "아르 누보": [273, 357],
  "웹툰": [624, 357],
  "소프트 일러스트": [975, 357],
  "인스타툰": [1326, 357], // ❌ 버림 (안 씀)
  "수채화": [273, 625],
  "일러스트": [624, 625],
  "팝아트": [975, 625],
  "스케치": [1326, 625],
  "3D 카툰": [273, 893],
  "유화": [624, 893],
};

// ===== 좌표 상수 =====
var NEW = [1443, 119];      // 새로 작성
var STYLE_CHANGE = [242, 1896]; // 스타일 변경 탭
var TEXT_INPUT = [500, 1896];
var VIEW_ALL = [1287, 2114];
var GENERATE = [800, 2275];
var SAVE = [851, 270];
var PHOTO_POS = [[150, 348], [410, 348], [670, 348], [930, 348]];
var GALLERY_ALBUM = [1115, 969]; // 사진 선택기의 박씨 갤러리 앨범

function tap(p) { click(p[0], p[1]); sleep(800); }

function generate(prompt, style, cropBottom) {
  // 앱이 이미 그리기 어시스트 화면이라고 가정
  tap(NEW); sleep(2000);
  tap(TEXT_INPUT); sleep(1200);
  setText(prompt); sleep(1000);
  back(); sleep(1500);
  tap(VIEW_ALL); sleep(2000);
  tap(STYLES[style]); sleep(1500);
  tap(GENERATE); sleep(20000);
  tap(SAVE); sleep(4000);
  toast("생성 완료: " + style);
}

function restyle(photoIndex, style, prompt) {
  tap(STYLE_CHANGE); sleep(2500);
  tap(GALLERY_ALBUM); sleep(2500);
  tap(PHOTO_POS[photoIndex]); sleep(3000);
  if (prompt) {
    tap([800, 1896]); sleep(1500);
    tap([1503, 1866]); sleep(1000);
    tap(TEXT_INPUT); sleep(1000);
    setText(prompt); sleep(1000);
    back(); sleep(1500);
  }
  tap(VIEW_ALL); sleep(2000);
  tap(STYLES[style]); sleep(1500);
  tap(GENERATE); sleep(20000);
  tap(SAVE); sleep(4000);
  toast("재스타일 완료: " + style);
}

// ===== 진입점 =====
// generate(PROMPT, STYLE, CROP_BOTTOM);   // 텍스트→이미지
// restyle(PHOTO_INDEX, STYLE, "");        // 사진→스타일 변경
toast("drawing-assist v2 로드됨. generate() / restyle() 호출");
