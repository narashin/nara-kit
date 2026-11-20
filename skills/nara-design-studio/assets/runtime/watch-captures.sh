#!/usr/bin/env bash
#
# Block until the studio POSTs a NEW "Export → PNG" capture request, print it, exit.
#
# The coding agent runs this in the BACKGROUND (like watch-comments.sh). When the user hits
# Export → PNG in the browser, serve.py appends a line to <outDir>/capture-requests.jsonl; this
# script detects the growth, prints the new line(s), and exits — waking the agent to capture THAT
# one candidate with its browser MCP (playwright / chrome-devtools): navigate to the url, select
# the candidate tab (data-id), add `document.body.classList.add('capturing')` (hides the studio
# chrome AND expands the inner scroll container so the whole screen — including the interaction
# legend at the bottom — is captured, not clipped), dispatch a resize so hotspots re-anchor,
# screenshot full-page, then remove the class. Save to the user's ~/Downloads as
# <name>-<candidateId>.png (same place the Layout contract / PDF land, so users don't hunt in the repo).
# Re-launch this for the next request, right after waking and before the work: it counts lines from
# its own start, so a request that lands while the agent is busy is otherwise never printed.
#
# Export → Figma uses the same loop with its own file: pass figma-requests.jsonl as the third
# argument. serve.py adds "procedure" (the pack's Figma steps) and "pack" (its manifest block) to each line.
#
# Each line is JSON: {"url": "...", "candidateId": "A", "candidateLabel": "..."} — one candidate.
#
# Usage:  watch-captures.sh [outDir] [timeout-seconds] [request-file]
#   defaults: outDir=./out, timeout=600s, request-file=capture-requests.jsonl
#   watches:  <outDir>/<request-file>
set -euo pipefail

OUT_DIR="${1:-./out}"
FILE="$OUT_DIR/${3:-capture-requests.jsonl}"
TIMEOUT="${2:-600}"

mkdir -p "$(dirname "$FILE")"
touch "$FILE"
before="$(wc -l < "$FILE" | tr -d ' ')"

waited=0
while :; do
  now="$(wc -l < "$FILE" | tr -d ' ')"
  if [ "$now" -gt "$before" ]; then
    tail -n "+$((before + 1))" "$FILE"
    exit 0
  fi
  if [ "$waited" -ge "$TIMEOUT" ]; then
    echo "__WATCH_TIMEOUT__ no requests in $(basename "$FILE") in ${TIMEOUT}s"
    exit 0
  fi
  sleep 1
  waited=$((waited + 1))
done
