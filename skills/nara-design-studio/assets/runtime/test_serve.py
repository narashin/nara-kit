# test_serve.py — exercises the 3-mount routing without a real socket by driving the handler's
# translate_path + POST helpers through a subprocess-started server.
import subprocess, sys, time, os, tempfile, urllib.request, urllib.error, json, signal, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))

def _start(tmp):
    runtime = os.path.join(tmp, "runtime"); pack = os.path.join(tmp, "pack"); out = os.path.join(tmp, "out")
    for d in (runtime, pack, out): os.makedirs(d, exist_ok=True)
    with open(os.path.join(runtime, "studio.js"), "w") as f: f.write("RUNTIME_JS")
    with open(os.path.join(pack, "_ds_bundle.js"), "w") as f: f.write("PACK_BUNDLE")
    with open(os.path.join(out, "screen.html"), "w") as f: f.write("OUT_HTML")
    p = subprocess.Popen([sys.executable, os.path.join(HERE, "serve.py"),
                          "--runtime", runtime, "--pack", pack, "--out", out, "--port", "8931"])
    time.sleep(1.0)
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
