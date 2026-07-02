#!/usr/bin/env bash
# memory-audit: score a memory file 0-4 by age/ref_validity/code_drift/conflict
# Usage: audit.sh <memory_file>
# Output: one line JSON
#
# Required: jq, git, stat, date
# Optional env: THRESHOLD_AGE_DAYS (default 90), CLAUDE_PROJECT_DIR (default cwd)

set -euo pipefail

THRESHOLD_AGE_DAYS="${THRESHOLD_AGE_DAYS:-90}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

LOG_MODE=0
if [[ "${1:-}" == "--log" ]]; then
  LOG_MODE=1
  shift
fi
target="${1:?memory file path required}"
[[ -f "$target" ]] || { echo "{\"error\":\"file not found: $target\"}"; exit 1; }

# Read a scalar frontmatter field's value. Indentation-tolerant so it also
# reads keys nested under a `metadata:` block (canonical schema), not just
# top-level keys. Returns the trailing value (empty when the field heads a
# multi-line YAML list).
parse_frontmatter_field() {
  awk -v field="$1" '
    /^---[[:space:]]*$/ {c++; next}
    c==1 && $0 ~ "^[[:space:]]*"field":" {
      line=$0
      sub("^[[:space:]]*"field":[[:space:]]*", "", line)
      print line
      exit
    }
    c>=2 {exit}
  ' "$target"
}

# Exit 0 if the frontmatter declares the given key at any indentation.
# Distinguishes "key absent" from "key present but empty" (multi-line list).
has_frontmatter_key() {
  awk -v field="$1" '
    /^---[[:space:]]*$/ {c++; next}
    c==1 && $0 ~ "^[[:space:]]*"field":" {found=1; exit}
    c>=2 {exit}
    END {exit(found?0:1)}
  ' "$target"
}

# Emit each item of a multi-line YAML list frontmatter field, one per line.
# Handles the canonical form where `ref_paths:` heads an indented `- item` list.
extract_frontmatter_list() {
  awk -v field="$1" '
    /^---[[:space:]]*$/ {c++; if(c>=2) exit; next}
    c!=1 {next}
    inlist==1 {
      if ($0 ~ /^[[:space:]]+-[[:space:]]*/) {
        item=$0
        sub(/^[[:space:]]+-[[:space:]]*/, "", item)
        print item
        next
      }
      inlist=0
    }
    $0 ~ "^[[:space:]]*"field":[[:space:]]*$" {inlist=1}
  ' "$target" | tr -d '[]"'"'"' '
}

# Signal 1: age
verified_at=$(parse_frontmatter_field "verified_at")
if [[ -n "$verified_at" ]] && date -j -f "%Y-%m-%d" "$verified_at" +%s &>/dev/null; then
  base_epoch=$(date -j -f "%Y-%m-%d" "$verified_at" +%s)
  age_source="verified_at"
else
  base_epoch=$(stat -f %m "$target")
  age_source="mtime"
fi
now_epoch=$(date +%s)
age_days=$(( (now_epoch - base_epoch) / 86400 ))
age_hit=$(( age_days >= THRESHOLD_AGE_DAYS ? 1 : 0 ))

# Signal 2: ref_validity
ref_paths_raw=$(parse_frontmatter_field "ref_paths")
declare -a paths=()
ref_paths_declared=0
if has_frontmatter_key "ref_paths"; then
  ref_paths_declared=1
  if [[ -n "${ref_paths_raw// /}" ]]; then
    # Inline array or scalar on the same line: `ref_paths: [a, b]` / `ref_paths: []`
    cleaned="${ref_paths_raw//[\[\]\"\']/}"
    if [[ -n "${cleaned// /}" ]]; then
      IFS=',' read -ra arr <<< "$cleaned"
      for p in "${arr[@]+"${arr[@]}"}"; do
        p="${p#"${p%%[![:space:]]*}"}"
        p="${p%"${p##*[![:space:]]}"}"
        [[ -n "$p" ]] && paths+=("$p")
      done
    fi
  else
    # Key heads a multi-line YAML list (canonical nested schema)
    while IFS= read -r p; do
      [[ -n "$p" ]] && paths+=("$p")
    done < <(extract_frontmatter_list "ref_paths")
  fi
fi
# Only grep-fallback when ref_paths field is absent (not when explicitly empty).
# Optional leading '/' so absolute paths are captured intact (not slash-stripped).
if [[ $ref_paths_declared -eq 0 ]]; then
  while IFS= read -r p; do
    [[ -n "$p" ]] && paths+=("$p")
  done < <(grep -oE '/?[a-zA-Z_][a-zA-Z0-9_/.-]*/[a-zA-Z0-9_./-]+\.(md|ts|tsx|py|json|yaml|yml|sh|html)' "$target" | sort -u)
fi

valid=0
total=${#paths[@]}
if [[ $total -gt 0 ]]; then
  for p in "${paths[@]}"; do
    if [[ -e "$PROJECT_DIR/$p" ]] || [[ -e "$p" ]]; then
      valid=$((valid + 1))
    fi
  done
fi
if [[ $total -eq 0 ]]; then
  validity_pct=100
else
  validity_pct=$(( valid * 100 / total ))
fi
validity_hit=$(( validity_pct < 100 ? 1 : 0 ))

# Signal 3: code_drift
drift_commits=0
if git -C "$PROJECT_DIR" rev-parse --git-dir &>/dev/null && [[ $total -gt 0 ]]; then
  if [[ "$age_source" == "verified_at" ]]; then
    since_arg="$verified_at"
  else
    since_arg=$(date -r "$base_epoch" +%Y-%m-%d)
  fi
  if [[ $total -gt 0 ]]; then
    for p in "${paths[@]}"; do
      if [[ -e "$PROJECT_DIR/$p" ]]; then
        count=$(git -C "$PROJECT_DIR" log --since="$since_arg" --pretty=format: --name-only -- "$p" 2>/dev/null | grep -c . || true)
        drift_commits=$(( drift_commits + count ))
      fi
    done
  fi
fi
drift_hit=$(( drift_commits > 0 ? 1 : 0 ))

# Signal 4: conflict
target_base=$(basename "$target" .md)
target_dir=$(dirname "$target")
target_mtime=$(stat -f %m "$target")
conflict_hit=0
for other in "$target_dir"/*.md; do
  [[ "$other" == "$target" ]] && continue
  [[ "$(basename "$other")" == "MEMORY.md" ]] && continue
  other_mtime=$(stat -f %m "$other")
  [[ $other_mtime -le $target_mtime ]] && continue
  if grep -qE "(supersedes|replaces|deprecates):[[:space:]]*${target_base}\\b" "$other"; then
    conflict_hit=1
    break
  fi
done

score=$(( age_hit + validity_hit + drift_hit + conflict_hit ))
if   [[ $score -eq 0 ]]; then label="healthy"
elif [[ $score -eq 1 ]]; then label="watch"
elif [[ $score -eq 2 ]]; then label="suspect"
else                          label="danger"
fi

signals_arr=()
[[ $age_hit      -eq 1 ]] && signals_arr+=("age_days")
[[ $validity_hit -eq 1 ]] && signals_arr+=("ref_validity")
[[ $drift_hit    -eq 1 ]] && signals_arr+=("code_drift")
[[ $conflict_hit -eq 1 ]] && signals_arr+=("conflict")

signals_json=$(printf '%s\n' "${signals_arr[@]:-}" | jq -R . | jq -s 'map(select(length > 0))')

result=$(jq -nc \
  --arg file "$target" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson score "$score" \
  --argjson signals "$signals_json" \
  --argjson age_days "$age_days" \
  --argjson validity_pct "$validity_pct" \
  --argjson drift_commits "$drift_commits" \
  --argjson conflict "$conflict_hit" \
  --arg label "$label" \
  '{
    ts: $ts,
    file: $file,
    score: $score,
    signals: $signals,
    details: {
      age_days: $age_days,
      validity_pct: $validity_pct,
      drift_commits: $drift_commits,
      conflict: ($conflict == 1)
    },
    label: $label
  }')

echo "$result"

if [[ $LOG_MODE -eq 1 ]]; then
  log_path="$(dirname "$target")/.audit-log.jsonl"
  echo "$result" >> "$log_path"
fi
