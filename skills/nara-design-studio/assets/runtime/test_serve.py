# test_serve.py — exercises the 3-mount routing without a real socket by driving the handler's
# translate_path + POST helpers through a subprocess-started server.
import subprocess, sys, time, os, tempfile, urllib.request, urllib.error, json, signal, shutil

HERE = os.path.dirname(os.path.abspath(__file__))

def _start(tmp):
    runtime = os.path.join(tmp, "runtime"); pack = os.path.join(tmp, "pack"); out = os.path.join(tmp, "out")
    for d in (runtime, pack, out): os.makedirs(d, exist_ok=True)
    with open(os.path.join(runtime, "studio.js"), "w") as f: f.write("RUNTIME_JS")
    with open(os.path.join(pack, "_ds_bundle.js"), "w") as f: f.write("PACK_BUNDLE")
    with open(os.path.join(out, "screen.html"), "w") as f: f.write("OUT_HTML")
    p = subprocess.Popen([sys.executable, os.path.join(HERE, "serve.py"),
                          "--runtime", runtime, "--pack", pack, "--out", out, "--port", "8931"])
    for _ in range(50):
        try:
            # A GET-able 200 route; runtime/studio.js exists so it responds once listening.
            urllib.request.urlopen("http://127.0.0.1:8931/_studio/studio.js", timeout=0.5)
            break
        except urllib.error.HTTPError:
            break  # server is up and responding (any HTTP status means it's listening)
        except urllib.error.URLError:
            time.sleep(0.1)  # not accepting connections yet
    return p, out

def _get(path):
    return urllib.request.urlopen("http://127.0.0.1:8931" + path, timeout=3).read().decode()

def test_three_mounts_and_comment_write():
    tmp = tempfile.mkdtemp()
    p, out = _start(tmp)
    try:
        assert _get("/_studio/studio.js") == "RUNTIME_JS"
        assert _get("/_pack/_ds_bundle.js") == "PACK_BUNDLE"
        assert _get("/screen.html") == "OUT_HTML"
        req = urllib.request.Request("http://127.0.0.1:8931/__comments",
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
