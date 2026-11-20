# test_serve.py — exercises the 3-mount routing without a real socket by driving the handler's
# translate_path + POST helpers through a subprocess-started server.
import subprocess, sys, time, os, tempfile, urllib.request, urllib.error, json, signal, shutil, socket

HERE = os.path.dirname(os.path.abspath(__file__))

# A free port per run: a fixed one collided with a studio the user already had open on it.
def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); return s.getsockname()[1]

PORT = _free_port()
BASE = "http://127.0.0.1:%d" % PORT

def _start(tmp, figma_procedure=None):
    runtime = os.path.join(tmp, "runtime"); pack = os.path.join(tmp, "pack"); out = os.path.join(tmp, "out")
    for d in (runtime, pack, out): os.makedirs(d, exist_ok=True)
    with open(os.path.join(runtime, "studio.js"), "w") as f: f.write("RUNTIME_JS")
    with open(os.path.join(pack, "_ds_bundle.js"), "w") as f: f.write("PACK_BUNDLE")
    with open(os.path.join(out, "screen.html"), "w") as f: f.write("OUT_HTML")
    if figma_procedure is not None:
        with open(os.path.join(pack, "figma-export.json"), "w") as f: json.dump({"procedure": figma_procedure}, f)
        with open(os.path.join(pack, "_ds_manifest.json"), "w") as f: json.dump({"pack": {"name": "Pack", "reuseRule": "Reuse."}}, f)
    p = subprocess.Popen([sys.executable, os.path.join(HERE, "serve.py"),
                          "--runtime", runtime, "--pack", pack, "--out", out, "--port", str(PORT)])
    for _ in range(50):
        try:
            # A GET-able 200 route; runtime/studio.js exists so it responds once listening.
            urllib.request.urlopen(BASE + "/_studio/studio.js", timeout=0.5)
            break
        except urllib.error.HTTPError:
            break  # server is up and responding (any HTTP status means it's listening)
        except urllib.error.URLError:
            time.sleep(0.1)  # not accepting connections yet
    return p, out

def _get(path):
    return urllib.request.urlopen(BASE + path, timeout=3).read().decode()

def _post(path, obj):
    req = urllib.request.Request(BASE + path, data=json.dumps(obj).encode(),
          headers={"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req, timeout=3)

def test_three_mounts_and_comment_write():
    tmp = tempfile.mkdtemp()
    p, out = _start(tmp)
    try:
        assert _get("/_studio/studio.js") == "RUNTIME_JS"
        assert _get("/_pack/_ds_bundle.js") == "PACK_BUNDLE"
        assert _get("/screen.html") == "OUT_HTML"
        req = urllib.request.Request(BASE + "/__comments",
              data=json.dumps({"comments":[{"n":1}]}).encode(),
              headers={"Content-Type":"application/json"}, method="POST")
        assert json.loads(urllib.request.urlopen(req, timeout=3).read())["ok"] is True
        assert os.path.exists(os.path.join(out, "comments.jsonl"))
    finally:
        p.send_signal(signal.SIGTERM); p.wait(timeout=5)
        shutil.rmtree(tmp, ignore_errors=True)

def test_pack_traversal_is_contained():
    tmp = tempfile.mkdtemp()
    p, out = _start(tmp)
    try:
        # A traversal attempt must not escape the pack mount (served content stays within roots).
        try:
            body = _get("/_pack/../runtime/studio.js")
        except urllib.error.HTTPError as e:
            body = str(e.code)
        assert body != "RUNTIME_JS"   # must NOT leak the runtime file via /_pack traversal
    finally:
        p.send_signal(signal.SIGTERM); p.wait(timeout=5)
        shutil.rmtree(tmp, ignore_errors=True)

def test_spec_export_route_is_gone():
    """Spec.md is no longer a handoff, so the server must not write one."""
    tmp = tempfile.mkdtemp()
    p, out = _start(tmp)
    try:
        try:
            code = _post("/__spec", {"file": "/screen.spec.md", "markdown": "# x"}).status
        except urllib.error.HTTPError as e:
            code = e.code
        assert code == 404
        assert not os.path.exists(os.path.join(out, "screen.spec.md"))
    finally:
        p.send_signal(signal.SIGTERM); p.wait(timeout=5)
        shutil.rmtree(tmp, ignore_errors=True)

def _post_raw(path, body, headers=None):
    h = {"Content-Type": "application/json"}; h.update(headers or {})
    try:
        return urllib.request.urlopen(urllib.request.Request(BASE + path, data=body, headers=h, method="POST"), timeout=3).status
    except urllib.error.HTTPError as e:
        return e.code

def test_figma_request_is_logged_as_one_json_line():
    """Export → Figma: one compact line per request; `procedure` and `pack` come from the pack itself, never from the body."""
    tmp = tempfile.mkdtemp()
    p, out = _start(tmp, figma_procedure="source/figma-export.md")
    try:
        body = {"url": "http://x/screen.html", "candidateId": "A", "candidateLabel": "Direction A",
                "procedure": "../../elsewhere.md", "pack": {"name": "stale copy"}}
        assert _post_raw("/__figma", json.dumps(body, indent=2).encode()) == 200  # multi-line on purpose
        lines = open(os.path.join(out, "figma-requests.jsonl"), encoding="utf-8").read().splitlines()
        assert [json.loads(l) for l in lines] == [{"url": "http://x/screen.html", "candidateId": "A",
            "candidateLabel": "Direction A", "procedure": "source/figma-export.md", "pack": {"name": "Pack", "reuseRule": "Reuse."}}]
    finally:
        p.send_signal(signal.SIGTERM); p.wait(timeout=5)
        shutil.rmtree(tmp, ignore_errors=True)

def test_figma_request_rejects_bad_bodies_and_packs_without_export():
    tmp = tempfile.mkdtemp()
    p, out = _start(tmp, figma_procedure="source/figma-export.md")
    try:
        assert _post_raw("/__figma", b"not json") == 400
        assert _post_raw("/__figma", b"[1, 2]") == 400
        assert not os.path.exists(os.path.join(out, "figma-requests.jsonl"))
    finally:
        p.send_signal(signal.SIGTERM); p.wait(timeout=5)
        shutil.rmtree(tmp, ignore_errors=True)
    tmp = tempfile.mkdtemp()
    p, out = _start(tmp)  # this pack ships no figma-export.json
    try:
        assert _post_raw("/__figma", json.dumps({"candidateId": "A"}).encode()) == 404
        assert not os.path.exists(os.path.join(out, "figma-requests.jsonl"))
    finally:
        p.send_signal(signal.SIGTERM); p.wait(timeout=5)
        shutil.rmtree(tmp, ignore_errors=True)

def test_posts_from_another_origin_are_refused():
    """The request files wake an agent, so only the studio page itself may write them."""
    tmp = tempfile.mkdtemp()
    p, out = _start(tmp, figma_procedure="source/figma-export.md")
    try:
        body = json.dumps({"candidateId": "A"}).encode()
        assert _post_raw("/__figma", body, {"Origin": "http://evil.example"}) == 403
        assert _post_raw("/__comments", body, {"Origin": "http://evil.example"}) == 403
        assert _post_raw("/__figma", body, {"Host": "evil.example:%d" % PORT}) == 403  # DNS rebinding
        assert not os.path.exists(os.path.join(out, "figma-requests.jsonl"))
        assert not os.path.exists(os.path.join(out, "comments.jsonl"))
        assert _post_raw("/__figma", body, {"Origin": BASE}) == 200
    finally:
        p.send_signal(signal.SIGTERM); p.wait(timeout=5)
        shutil.rmtree(tmp, ignore_errors=True)

def _watch(tmp, *args):
    # Watcher timeout (5s) stays under communicate's (15s), so a missed line ends in the assert, not a TimeoutExpired.
    return subprocess.Popen(["bash", os.path.join(HERE, "watch-captures.sh"), tmp, "5", *args],
                            stdout=subprocess.PIPE, text=True)

def _watch_sees(tmp, request_file, args, line):
    w = _watch(tmp, *args)
    try:
        time.sleep(1.5)
        with open(os.path.join(tmp, request_file), "a") as fh: fh.write(line + "\n")
        printed, _ = w.communicate(timeout=15)
        return printed.strip()
    finally:
        if w.poll() is None: w.kill()

def test_watcher_reads_the_named_request_file():
    """watch-captures.sh <outDir> <timeout> figma-requests.jsonl prints only the new line, then exits."""
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "figma-requests.jsonl"), "w") as fh: fh.write('{"old": 1}\n')
        assert _watch_sees(tmp, "figma-requests.jsonl", ["figma-requests.jsonl"], '{"candidateId": "A"}') == '{"candidateId": "A"}'
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def test_watcher_defaults_to_capture_requests():
    """Without a third argument the PNG flow is unchanged: capture-requests.jsonl, not figma-requests.jsonl."""
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "figma-requests.jsonl"), "w") as fh: fh.write('{"figma": 1}\n')
        assert _watch_sees(tmp, "capture-requests.jsonl", [], '{"candidateId": "B"}') == '{"candidateId": "B"}'
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
