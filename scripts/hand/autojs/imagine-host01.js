// imagine-host01.js — AutoJS6 MODEL (HOST-01)
// 한 요청을 잠근다. 반복은 이 파일 Run.
// 비전 좌표 금지. 글자/desc 클릭.
//
// 하는 일:
//   grok.com/imagine 이미 열린 상태에서
//   비디오 · 10s · 제출 을 글자로 누른다.
// 첨부·프롬프트는 이미 작곡기에 있다고 가정하거나
// /sdcard/Download/grok-cross/prompt-host01.txt 를 붙여넣는다.
"auto";
auto.waitFor();
auto.setMode("fast");

function hit(label) {
    var w = text(label).findOne(1200);
    if (!w) w = textContains(label).findOne(400);
    if (!w) w = desc(label).findOne(400);
    if (!w) w = descContains(label).findOne(400);
    if (!w) {
        toast("missing: " + label);
        return false;
    }
    if (!w.click() && w.bounds()) click(w.bounds().centerX(), w.bounds().centerY());
    sleep(400);
    return true;
}

toast("HOST-01 model");
hit("비디오");
hit("10s");
hit("1080p");
hit("제출");
toast("HOST-01 submitted");
