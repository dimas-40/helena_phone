// hand-server.js — AutoJS6 6.7.0 accessibility HTTP radar
// Listen 127.0.0.1:18765  (adb shell curl from S25 / this tab)
// Keep this script running. Do not console.show() — it covers Chrome.

"auto";

auto.waitFor();
auto.setMode("fast");

var PORT = 18765;
var HOST = "127.0.0.1";
var running = true;

function jout(obj) {
    return JSON.stringify(obj);
}

function decode(s) {
    try {
        return String(java.net.URLDecoder.decode(String(s || ""), "UTF-8"));
    } catch (e) {
        return String(s || "");
    }
}

function parseReq(line) {
    var m = String(line || "").match(/^GET\s+(\S+)\s+HTTP/);
    if (!m) return null;
    var u = m[1];
    var i = u.indexOf("?");
    var path = i < 0 ? u : u.substring(0, i);
    var q = {};
    if (i >= 0) {
        var parts = String(u.substring(i + 1)).split("&");
        for (var n = 0; n < parts.length; n++) {
            var kv = parts[n].split("=");
            q[decode(kv[0])] = decode(kv.length > 1 ? kv[1] : "");
        }
    }
    return { path: path, q: q };
}

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

function nodeInfo(w) {
    if (!w) return null;
    var b = w.bounds();
    return {
        text: String(w.text() || ""),
        desc: String(w.desc() || ""),
        id: String(w.id() || ""),
        className: String(w.className() || ""),
        clickable: !!w.clickable(),
        bounds: b ? [b.left, b.top, b.right, b.bottom] : null
    };
}

function clickNode(w) {
    if (!w) return false;
    if (w.click()) return true;
    var b = w.bounds();
    if (b) {
        click(b.centerX(), b.centerY());
        return true;
    }
    return false;
}

function collectTree(limit) {
    limit = limit || 80;
    var roots = className("android.widget.FrameLayout").find();
    var out = [];
    var nodes = selector().find();
    var n = Math.min(nodes.length, limit);
    for (var i = 0; i < n; i++) {
        var w = nodes[i];
        var t = String(w.text() || "");
        var d = String(w.desc() || "");
        if (!t && !d && !w.clickable()) continue;
        out.push(nodeInfo(w));
    }
    return out;
}

function handlePath(req) {
    var p = req.path;
    var q = req.q;
    if (p === "/health" || p === "/") {
        return { ok: true, engine: "autojs6", port: PORT, pkg: currentPackage() };
    }
    if (p === "/pkg") {
        return { ok: true, pkg: currentPackage(), act: currentActivity() };
    }
    if (p === "/find") {
        var w = findNode(q);
        return { ok: !!w, engine: "autojs6", node: nodeInfo(w) };
    }
    if (p === "/click") {
        var w2 = findNode(q);
        if (!w2) return { ok: false, engine: "autojs6", error: "not_found", q: q };
        var did = clickNode(w2);
        return { ok: did, engine: "autojs6", node: nodeInfo(w2) };
    }
    if (p === "/input") {
        var s = q.text || "";
        if (!s) return { ok: false, error: "missing_text" };
        setText(s);
        return { ok: true, engine: "autojs6", input: s };
    }
    if (p === "/back") {
        back();
        return { ok: true, engine: "autojs6", op: "back" };
    }
    if (p === "/tree") {
        return { ok: true, engine: "autojs6", pkg: currentPackage(), nodes: collectTree(parseInt(q.limit || "80", 10)) };
    }
    return { ok: false, error: "unknown_path", path: p };
}

function httpRespond(sock, obj, code) {
    var body = jout(obj);
    var bytes = new java.lang.String(body).getBytes("UTF-8");
    var outs = new java.io.DataOutputStream(sock.getOutputStream());
    var status = code || 200;
    var head =
        "HTTP/1.1 " + status + " OK\r\n" +
        "Content-Type: application/json; charset=utf-8\r\n" +
        "Content-Length: " + bytes.length + "\r\n" +
        "Connection: close\r\n\r\n";
    outs.write(new java.lang.String(head).getBytes("US-ASCII"));
    outs.write(bytes);
    outs.flush();
}

function handleSock(sock) {
    try {
        sock.setSoTimeout(5000);
        var ins = new java.io.BufferedReader(new java.io.InputStreamReader(sock.getInputStream(), "UTF-8"));
        var line = ins.readLine();
        var req = parseReq(line);
        var skip;
        while ((skip = ins.readLine()) != null) {
            if (skip.length() === 0) break;
        }
        if (!req) {
            httpRespond(sock, { ok: false, error: "bad_request" }, 400);
            return;
        }
        var result = handlePath(req);
        httpRespond(sock, result, result.ok ? 200 : 404);
    } catch (e) {
        try {
            httpRespond(sock, { ok: false, error: String(e) }, 500);
        } catch (e2) {}
    } finally {
        try { sock.close(); } catch (e3) {}
    }
}

var server = new java.net.ServerSocket();
server.bind(new java.net.InetSocketAddress(HOST, PORT));

new java.lang.Thread(function () {
    while (running) {
        try {
            var sock = server.accept();
            new java.lang.Thread(function () { handleSock(sock); }).start();
        } catch (e) {
            if (running) log("hand-server accept: " + e);
        }
    }
}).start();

files.createWithDirs("/sdcard/Download/grok-cross/");
files.write("/sdcard/Download/grok-cross/hand-server.ok", String(new Date().getTime()));
toast("hand-server :" + PORT);
log("hand-server listening " + HOST + ":" + PORT);

setInterval(function () {}, 60000);
