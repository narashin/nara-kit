#!/usr/bin/env python3
"""
nara-design-studio dev server (generic — no design-system specifics).

Serves three mounts so the engine runtime, the DS pack, and the generated output can live in
separate directories yet resolve under one origin:
  /_studio/*  -> the engine runtime dir (studio.js / studio.css / layout-contract.js)
  /_pack/*    -> the DS pack dir (bundle, tokens, data, manifest, kit helpers)
  /*          -> the output dir (generated candidate HTML, out/, handoff/)
It also captures the studio's POSTs (comments / interactions / capture / figma) into the output dir.

Usage:
  python3 serve.py --pack <packDir> --out <outDir> [--runtime <dir>] [--port 8917]
"""
import argparse
import http.server
import json
import os

RUNTIME_PREFIX = "/_studio/"
PACK_PREFIX = "/_pack/"


def make_handler(runtime_dir, pack_dir, out_dir):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            # Base directory is the output dir; _studio/_pack are remapped in translate_path.
            super().__init__(*args, directory=out_dir, **kwargs)

        def end_headers(self):
            # Never cache the runtime — a stale studio.js keeps running in an open tab otherwise.
            self.send_header("Cache-Control", "no-store, max-age=0")
            super().end_headers()

        def translate_path(self, path):
            clean = path.split("?", 1)[0].split("#", 1)[0]
            if clean.startswith(RUNTIME_PREFIX):
                return self._safe_join(runtime_dir, clean[len(RUNTIME_PREFIX):])
            if clean.startswith(PACK_PREFIX):
                return self._safe_join(pack_dir, clean[len(PACK_PREFIX):])
            return super().translate_path(path)

        @staticmethod
        def _safe_join(root, rel):
            dest = os.path.abspath(os.path.join(root, rel.lstrip("/")))
            # Prevent path traversal outside the mounted root.
            if dest != root and not dest.startswith(root + os.sep):
                return root
            return dest

        def _from_this_page(self):
            # The request files wake an agent that acts on them, so only the studio page this server
            # serves may write them: no CORS grant, a loopback Host (DNS rebinding), a same-origin Origin.
            host = (self.headers.get("Host") or "").lower()
            if host.rsplit(":", 1)[0] not in ("127.0.0.1", "localhost"):
                return False
            origin = self.headers.get("Origin")
            return origin is None or origin.lower() == "http://" + host

        def do_GET(self):
            clean = self.path.split("?")[0]
            # A missing interaction sidecar is normal — serve {} so the studio's load fetch is quiet.
            if clean.endswith(".interactions.json"):
                dest = self.translate_path(self.path)
                if not os.path.exists(dest):
                    return self._json(200, {})
            return super().do_GET()

        def do_POST(self):
            if not self._from_this_page():
                return self._json(403, {"ok": False, "error": "foreign origin"})
            route = self.path.rstrip("/")
            if route == "/__comments": return self._append("comments.jsonl")
            if route == "/__capture": return self._append("capture-requests.jsonl")
            if route == "/__figma": return self._figma_request()
            if route == "/__interactions": return self._save_sidecar(".interactions.json", "interactions")
            self.send_response(404); self.end_headers()

        def _read_body(self):
            length = int(self.headers.get("Content-Length", 0))
            return self.rfile.read(length).decode("utf-8")

        def _json(self, code, obj):
            self.send_response(code)
            self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps(obj).encode("utf-8"))

        def _figma_request(self):
            """One Export → Figma request, as one JSON line. The steps to follow (figma-export.json) and the
            pack metadata (_ds_manifest.json `pack`) come from the pack itself, never from the body: the agent
            reads this line and runs that procedure, and a screen's copy of the pack block can be stale."""
            try:
                with open(os.path.join(pack_dir, "figma-export.json"), encoding="utf-8") as f:
                    procedure = json.load(f).get("procedure")
            except (OSError, json.JSONDecodeError, AttributeError):
                procedure = None
            if not isinstance(procedure, str) or not procedure:
                return self._json(404, {"ok": False, "error": "this pack has no Figma export"})
            try:
                body = json.loads(self._read_body())
            except json.JSONDecodeError:
                body = None
            if not isinstance(body, dict):
                return self._json(400, {"ok": False, "error": "bad payload"})
            line = {k: body[k] for k in ("url", "candidateId", "candidateLabel") if isinstance(body.get(k), str)}
            line["procedure"] = procedure
            try:
                with open(os.path.join(pack_dir, "_ds_manifest.json"), encoding="utf-8") as f:
                    pack_meta = json.load(f).get("pack")
            except (OSError, json.JSONDecodeError, AttributeError):
                pack_meta = None
            if isinstance(pack_meta, dict):
                line["pack"] = pack_meta
            return self._append("figma-requests.jsonl", json.dumps(line, ensure_ascii=False))

        def _append(self, filename, raw=None):
            if raw is None:
                raw = self._read_body()
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, filename), "a", encoding="utf-8") as f:
                f.write(raw.strip() + "\n")
            self._json(200, {"ok": True})
            print(f"[studio] appended -> {os.path.join(out_dir, filename)}", flush=True)

        def _dest_under_out(self, rel, suffix):
            dest = os.path.abspath(os.path.join(out_dir, (rel or "").lstrip("/")))
            if not dest.endswith(suffix) or (dest != out_dir and not dest.startswith(out_dir + os.sep)):
                return None
            return dest

        def _save_sidecar(self, suffix, field):
            raw = self._read_body()
            try:
                payload = json.loads(raw)
                value = payload.get(field, {} if suffix.endswith(".json") else "")
            except (json.JSONDecodeError, AttributeError):
                return self._json(400, {"ok": False, "error": "bad payload"})
            dest = self._dest_under_out(payload.get("file"), suffix)
            if not dest:
                return self._json(400, {"ok": False, "error": "bad path"})
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w") as f:
                json.dump(value, f, indent=2) if suffix.endswith(".json") else f.write(value)
            self._json(200, {"ok": True})
            print(f"[studio] saved -> {dest}", flush=True)

    return Handler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--runtime", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--port", type=int, default=8917)
    a = ap.parse_args()
    pack = os.path.abspath(a.pack); out = os.path.abspath(a.out); runtime = os.path.abspath(a.runtime)
    os.makedirs(out, exist_ok=True)
    print(f"[studio] runtime={runtime}")
    print(f"[studio] pack={pack}")
    print(f"[studio] out={out}  http://localhost:{a.port}/")
    http.server.HTTPServer(("127.0.0.1", a.port), make_handler(runtime, pack, out)).serve_forever()


if __name__ == "__main__":
    main()
