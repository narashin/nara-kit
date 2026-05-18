#!/usr/bin/env bash
# memory-archive: move flagged memory to archive/, remove from MEMORY.md index
# Usage: archive.sh <memory_file>
# Output: JSON receipt {action, from, to, index_updated}
#
# Idempotent: re-running on already-archived path is a no-op.

set -euo pipefail

target="${1:?memory file path required}"
memory_dir=$(dirname "$target")
base=$(basename "$target")
archive_dir="$memory_dir/archive"

# Case 1: file exists at source — normal archive flow below.
# Case 2: file missing at source BUT already in archive — return noop (idempotent on original path).
# Case 3: file missing everywhere — hard error.
if [[ ! -f "$target" ]]; then
  candidate="$archive_dir/$base"
  if [[ -f "$candidate" ]]; then
    jq -nc --arg from "$target" --arg to "$candidate" \
      '{action: "noop", from: $from, to: $to, index_updated: false, reason: "already in archive"}'
    exit 0
  fi
  echo "{\"error\":\"file not found: $target\"}"
  exit 1
fi

# Already inside archive/ dir — also idempotent (check BEFORE mkdir to avoid nested archive/archive)
if [[ "$memory_dir" == */archive ]]; then
  jq -nc --arg file "$target" '{action: "noop", from: $file, to: $file, index_updated: false, reason: "already in archive"}'
  exit 0
fi

mkdir -p "$archive_dir"

dest="$archive_dir/$base"
# Suffix with timestamp if collision
if [[ -e "$dest" ]]; then
  ts=$(date +%Y%m%d-%H%M%S)
  dest="$archive_dir/${base%.md}.${ts}.md"
fi

mv "$target" "$dest"

# Remove matching line from MEMORY.md index — match only list-item link rows
# Pattern: leading `- [label](basename.md)` (allow leading spaces). Strict to avoid
# false hits on prose mentions of the basename.
index_path="$memory_dir/MEMORY.md"
index_updated=false
if [[ -f "$index_path" ]]; then
  base_link=$(printf '%s' "$base" | sed 's/[][\/.^$*]/\\&/g')
  pattern="^[[:space:]]*-[[:space:]]\\[[^]]+\\]\\(${base_link}\\)"
  if grep -qE "$pattern" "$index_path"; then
    grep -vE "$pattern" "$index_path" > "$index_path.tmp"
    mv "$index_path.tmp" "$index_path"
    index_updated=true
  fi
fi

jq -nc \
  --arg from "$target" \
  --arg to "$dest" \
  --argjson index_updated "$index_updated" \
  '{action: "archived", from: $from, to: $to, index_updated: $index_updated}'
