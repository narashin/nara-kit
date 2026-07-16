#!/usr/bin/env bash
#
# Block until the studio POSTs a NEW batch of "Send to Agent" comments, print it, exit.
#
# The coding agent runs this in the BACKGROUND. When the user hits "Send to Agent" in the
# browser, serve.py appends a line to <outDir>/comments.jsonl; this script detects the growth,
# prints the new line(s), and exits — which wakes Claude Code to apply them automatically
# (no "apply my comments" message needed). Claude then re-launches it for the next round.
#
# Usage:  watch-comments.sh [outDir] [timeout-seconds]
#   defaults: outDir=./out, timeout=600s
#   watches:  <outDir>/comments.jsonl
set -euo pipefail

OUT_DIR="${1:-./out}"
FILE="$OUT_DIR/comments.jsonl"
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
    echo "__WATCH_TIMEOUT__ no new comments in ${TIMEOUT}s"
    exit 0
  fi
  sleep 1
  waited=$((waited + 1))
done
