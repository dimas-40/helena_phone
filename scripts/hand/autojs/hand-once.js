// hand-once.js — one command from grok-cross/cmd.json → result.json
"auto";
auto.waitFor();
auto.setMode("fast");

var CMD = "/sdcard/Download/grok-cross/cmd.json";
var RES = "/sdcard/Download/grok-cross/result.json";

function findNode(q) {
    var w = null;
    var timeout = parseInt(q.timeout || "900", 10);
    if (q.id) w = id(q.id).findOne(timeout);
    if (!w && q.desc) {
        w = desc(q.desc).findOne(timeout);
        if (!w) w = descContains(q.desc).findOne(250);
    }
    if (!w && q.text) {
        w = text(q.text).findOne(timeout);
        if (!w) w = textContains(q.text).findOne(250);
        if (!w) w = desc(q.text).findOne(250);
        if (!w) w = descContains(q.text).findOne(250);
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
    var q = doc;
    if (op === "health" || op === "pkg") {
        return { ok: true, engine: "autojs6", pkg: currentPackage(), act: currentActivity() };
    }
    if (op === "back") {
        back();
        return { ok: true, engine: "autojs6", op: "back" };
    }
    if (op === "input") {
        setText(String(q.text || ""));
        return { ok: true, engine: "autojs6", op: "input" };
    }
    var w = findNode(q);
    if (op === "find") return { ok: !!w, engine: "autojs6", node: info(w) };
    if (op === "click") {
        if (!w) return { ok: false, engine: "autojs6", error: "not_found", q: { text: q.text, desc: q.desc, id: q.id } };
        var did = w.click();
        if (!did && w.bounds()) click(w.bounds().centerX(), w.bounds().centerY());
        return { ok: true, engine: "autojs6", node: info(w) };
    }
    return { ok: false, error: "unknown_op", op: op };
}

var out;
try {
    if (!files.exists(CMD)) {
        out = { ok: false, error: "no_cmd" };
    } else {
        var doc = JSON.parse(files.read(CMD));
        files.remove(CMD);
        out = run(doc);
    }
} catch (e) {
    out = { ok: false, error: String(e) };
}
files.createWithDirs("/sdcard/Download/grok-cross/");
files.write(RES, JSON.stringify(out));
