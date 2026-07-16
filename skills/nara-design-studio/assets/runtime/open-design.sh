#!/usr/bin/env bash
#
# Open a finalized handoff design by Jira ID (or any filename fragment).
# Finds the matching <outDir>/handoff/<JIRA-ID>-<slug>-<DATE>.html, makes sure serve.py is
# running (--pack <packDir> --out <outDir>), and opens it in the browser — the live prototype
# with the real DS components.
#
# Usage:  open-design.sh <JIRA-ID | fragment> <outDir> [packDir] [port]
#   <outDir>   output directory (holds handoff/, comments.jsonl, capture-requests.jsonl)
#   [packDir]  DS pack directory served at /_pack/ (default: this skill's bundled starter-pack —
#              pass your project's real pack dir here once nara-design-pack-builder has one)
#   [port]     default 8917
#
#   e.g.  open-design.sh JIRA-293 ./out
#         open-design.sh pending-approval ./out /path/to/my-ds-pack 8080
set -euo pipefail

RUNTIME_DIR="$(cd "$(dirname "$0")" && pwd)"                      # assets/runtime
DEFAULT_PACK="$(cd "$RUNTIME_DIR/../starter-pack" && pwd)"        # assets/starter-pack (bundled default)

QUERY="${1:-}"
OUT_DIR="${2:-}"
PACK_DIR="${3:-$DEFAULT_PACK}"
PORT="${4:-8917}"

if [ -z "$QUERY" ] || [ -z "$OUT_DIR" ]; then
  echo "usage: open-design.sh <JIRA-ID | fragment> <outDir> [packDir] [port]"
  exit 1
fi

HANDOFF="$OUT_DIR/handoff"

list_available() {
  echo "available handoff designs:"
  ls "$HANDOFF"/*.html 2>/dev/null | sed 's#.*/##; s/^/  /' || echo "  (none — save one to $HANDOFF/ first)"
}

# Match, newest first — filenames end with -YYYY-MM-DD.html, so reverse sort = latest revision.
matches="$(ls "$HANDOFF"/*.html 2>/dev/null | grep -i -- "$QUERY" | sort -r || true)"
if [ -z "$matches" ]; then
  echo "no handoff design matching '$QUERY'."
  list_available
  exit 1
fi

count="$(printf '%s\n' "$matches" | grep -c . )"
file="$(printf '%s\n' "$matches" | head -1)"
file="$(basename "$file")"
[ "$count" -gt 1 ] && echo "[open-design] $count matches for '$QUERY' — opening newest: $file"

# Ensure serve.py is up on $PORT (mounts runtime + pack + out so the DS bundle resolves).
if ! curl -s -o /dev/null "http://localhost:$PORT/" 2>/dev/null; then
  echo "[open-design] starting serve.py on $PORT (pack=$PACK_DIR, out=$OUT_DIR)…"
  nohup python3 "$RUNTIME_DIR/serve.py" --pack "$PACK_DIR" --out "$OUT_DIR" --runtime "$RUNTIME_DIR" --port "$PORT" \
    >/tmp/nara-design-studio-serve.log 2>&1 &
  sleep 1.5
fi

URL="http://localhost:$PORT/handoff/$file"
echo "[open-design] $URL"
if command -v open >/dev/null 2>&1; then open "$URL"
elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL"
else echo "[open-design] open it manually: $URL"; fi
