#!/usr/bin/env bash
# nara-memory-audit Tier 1: score a memory file 0-4 by age/ref_validity/code_drift/skill_ref_broken
# Usage: audit.sh [--log] <memory_file>
# Output: one line JSON
#
# Required: jq, git, stat, date, grep
# Optional env: THRESHOLD_AGE_DAYS (default 90), CLAUDE_PROJECT_DIR (default cwd)
#
# Signal 4 (skill_ref_broken) resolves nara-kit skill references against
# $CLAUDE_PROJECT_DIR/skills/ — run from the repo the memory is ABOUT
# (e.g. nara-kit root) so skills/ and git resolve. The memory dir itself
# lives elsewhere (~/.claude/projects/<slug>/memory/) and is passed as $1.

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
has_frontmatter_key() {
  awk -v field="$1" '
    /^---[[:space:]]*$/ {c++; next}
    c==1 && $0 ~ "^[[:space:]]*"field":" {found=1; exit}
    c>=2 {exit}
    END {exit(found?0:1)}
  ' "$target"
}

# Emit each item of a multi-line YAML list frontmatter field, one per line.
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

# --- Signal 1: age ---
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

# --- Signal 2: ref_validity ---
ref_paths_raw=$(parse_frontmatter_field "ref_paths")
declare -a paths=()
ref_paths_declared=0
if has_frontmatter_key "ref_paths"; then
  ref_paths_declared=1
  if [[ -n "${ref_paths_raw// /}" ]]; then
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
    while IFS= read -r p; do
      [[ -n "$p" ]] && paths+=("$p")
    done < <(extract_frontmatter_list "ref_paths")
  fi
fi
# Grep-fallback only when ref_paths is absent (not when explicitly empty).
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

# --- Signal 3: code_drift ---
drift_commits=0
if git -C "$PROJECT_DIR" rev-parse --git-dir &>/dev/null && [[ $total -gt 0 ]]; then
  if [[ "$age_source" == "verified_at" ]]; then
    since_arg="$verified_at"
  else
    since_arg=$(date -r "$base_epoch" +%Y-%m-%d)
  fi
  for p in "${paths[@]}"; do
    if [[ -e "$PROJECT_DIR/$p" ]]; then
      count=$(git -C "$PROJECT_DIR" log --since="$since_arg" --pretty=format: --name-only -- "$p" 2>/dev/null | grep -c . || true)
      drift_commits=$(( drift_commits + count ))
    fi
  done
fi
drift_hit=$(( drift_commits > 0 ? 1 : 0 ))

# --- Signal 4: skill_ref_broken ---
# High-precision only: explicit nara-kit skill claims that don't resolve to a
# live skills/<name>/ directory. Two forms — (A) `skills/<name>/` path tokens,
# (B) `/nara-<name>` slash-command invocations. Bare backticked skill names
# without a skills/ prefix or /nara- invocation are intentionally NOT caught
# here (would be noisy); Tier 2 semantic review handles those.
declare -a skill_refs=()
# Form A: skills/<name>/ directory path claims
while IFS= read -r tok; do
  n="${tok#skills/}"; n="${n%/}"
  [[ -n "$n" ]] && skill_refs+=("skills/$n")
done < <(grep -oE 'skills/[a-zA-Z0-9_-]+/' "$target" 2>/dev/null | sort -u || true)
# Form B: /nara-<name> slash-command invocations (not part of a longer path)
while IFS= read -r tok; do
  n="${tok##*/}"
  [[ "$n" == "nara-kit" ]] && continue
  [[ -n "$n" ]] && skill_refs+=("skills/$n")
done < <(grep -oE '(^|[^A-Za-z0-9/])/nara-[a-zA-Z0-9_-]+' "$target" 2>/dev/null | grep -oE '/nara-[a-zA-Z0-9_-]+' | sort -u || true)

declare -a broken_refs=()
if [[ ${#skill_refs[@]} -gt 0 ]]; then
  while IFS= read -r sref; do
    [[ -z "$sref" ]] && continue
    [[ -d "$PROJECT_DIR/$sref" ]] || broken_refs+=("$sref")
  done < <(printf '%s\n' "${skill_refs[@]}" | sort -u)
fi
skill_ref_broken_hit=$(( ${#broken_refs[@]} > 0 ? 1 : 0 ))

# --- Score ---
score=$(( age_hit + validity_hit + drift_hit + skill_ref_broken_hit ))
if   [[ $score -eq 0 ]]; then label="healthy"
elif [[ $score -eq 1 ]]; then label="watch"
elif [[ $score -eq 2 ]]; then label="suspect"
else                          label="danger"
fi

signals_arr=()
[[ $age_hit              -eq 1 ]] && signals_arr+=("age_days")
[[ $validity_hit         -eq 1 ]] && signals_arr+=("ref_validity")
[[ $drift_hit            -eq 1 ]] && signals_arr+=("code_drift")
[[ $skill_ref_broken_hit -eq 1 ]] && signals_arr+=("skill_ref_broken")

signals_json=$(printf '%s\n' "${signals_arr[@]:-}" | jq -R . | jq -s 'map(select(length > 0))')
broken_json=$(printf '%s\n' "${broken_refs[@]:-}" | jq -R . | jq -s 'map(select(length > 0))')

result=$(jq -nc \
  --arg file "$target" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson score "$score" \
  --argjson signals "$signals_json" \
  --argjson age_days "$age_days" \
  --argjson validity_pct "$validity_pct" \
  --argjson drift_commits "$drift_commits" \
  --argjson broken "$broken_json" \
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
      skill_refs_broken: $broken
    },
    label: $label
  }')

echo "$result"

if [[ $LOG_MODE -eq 1 ]]; then
  log_path="$(dirname "$target")/.audit-log.jsonl"
  echo "$result" >> "$log_path"
fi
