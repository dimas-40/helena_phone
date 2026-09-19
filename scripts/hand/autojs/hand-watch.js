// hand-watch.js — AutoJS6 상주 레이더. Run 한 번.
// Polls /sdcard/Download/grok-cross/cmd.json every 200ms.
"auto";
auto.waitFor();
auto.setMode("fast");

var CMD = "/sdcard/Download/grok-cross/cmd.json";
var RES = "/sdcard/Download/grok-cross/result.json";
var OK = "/sdcard/Download/grok-cross/hand-watch.ok";

files.createWithDirs("/sdcard/Download/grok-cross/");
files.write(OK, String(new Date().getTime()));
toast("hand-watch on");
log("hand-watch polling");

function findNode(q) {
    var w = null;
    var timeout = parseInt(q.timeout || "800", 10);
    if (q.id) w = id(q.id).findOne(timeout);
    if (!w && q.desc) {
        w = desc(q.desc).findOne(timeout);
        if (!w) w = descContains(q.desc).findOne(200);
    }
    if (!w && q.text) {
        w = text(q.text).findOne(timeout);
        if (!w) w = textContains(q.text).findOne(200);
        if (!w) w = desc(q.text).findOne(200);
        if (!w) w = descContains(q.text).findOne(200);
    }
    return w;
}

function info(w) {
    if (!w) return null;
    var b = w.bounds();
    return {
        text: String(w.text() || ""),
        desc: String(w.desc() || ""),
        id: String(w.id() || ""),
        clickable: !!w.clickable(),
        bounds: b ? [b.left, b.top, b.right, b.bottom] : null
    };
}

function run(doc) {
    var op = doc.op || "find";
    if (op === "health") return { ok: true, engine: "autojs6-watch", pkg: currentPackage() };
    if (op === "back") { back(); return { ok: true, engine: "autojs6-watch", op: "back" }; }
    if (op === "input") { setText(String(doc.text || "")); return { ok: true, engine: "autojs6-watch" }; }
    var w = findNode(doc);
    if (op === "find") return { ok: !!w, engine: "autojs6-watch", node: info(w) };
    if (op === "click") {
        if (!w) return { ok: false, engine: "autojs6-watch", error: "not_found" };
        var did = w.click();
        if (!did && w.bounds()) click(w.bounds().centerX(), w.bounds().centerY());
        return { ok: true, engine: "autojs6-watch", node: info(w) };
    }
    return { ok: false, error: "unknown_op", op: op };
}

setInterval(function () {
    if (!files.exists(CMD)) return;
    var out;
    try {
        var doc = JSON.parse(files.read(CMD));
        files.remove(CMD);
        out = run(doc);
    } catch (e) {
        out = { ok: false, error: String(e) };
    }
    files.write(RES, JSON.stringify(out));
}, 200);

setInterval(function () {
    files.write(OK, String(new Date().getTime()));
}, 5000);
