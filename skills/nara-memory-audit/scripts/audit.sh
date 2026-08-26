#!/usr/bin/env bash
# nara-memory-audit Tier 1: score a memory file 0-4 by age/ref_validity/code_drift/skill_ref_broken
# Usage: audit.sh [--log] <memory_file>
# Output: one line JSON
#
# Required: jq, git, stat, date, grep
# Optional env: THRESHOLD_AGE_DAYS (default 90), CLAUDE_PROJECT_DIR (default cwd),
#               NARA_SKILLS_DIRS (colon-separated skill roots; overrides autodetect)
#
# Signal 4 resolves skill references per FORM, because the two forms make
# different claims, and reports each under its own identifier shape:
#   Form A  skills/<name>/   a repo-relative PATH claim, reported as
#                            `skills/<name>`. The audited repo answers it when it
#                            has a skills/ tree; otherwise it falls back to
#                            existence-anywhere (see the Form A loop below).
#   Form B  /nara-<name>     an INSTALLED-SKILL claim, reported as `/<name>`.
#                            Any discoverable root answers it.
# A Form A claim is never cleared by an agent root: the pre-`nara-` migration
# names (code-review, commit, gap, ...) collide with generically-named skills
# installed there, and clearing on that collision would hide the migration drift
# class this signal exists to catch. The strongest verdict such a match earns is
# UNKNOWN.
#
# An unresolvable check is never scored as a failure: skill_ref_unknown scores 0.
# But "cannot confirm the path" is not the same as "cannot see the skill" — a
# skill absent from every root is broken regardless of which repo asks.
#
# Run from the repo the memory is ABOUT so git history resolves. The memory dir
# itself lives elsewhere (<agent-config>/projects/<slug>/memory/) and is $1.

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
# Items are emitted RAW — quote stripping is unquote_entry's job, because a
# character class applied to the whole line also eats characters that are part
# of the value (dynamic-route filenames carry their own brackets).
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
  ' "$target"
}

# Trim surrounding whitespace, then strip ONE matched pair of surrounding
# quotes. Everything inside the value survives: `app/[locale]/page.tsx` keeps
# its brackets, and a filename with a space keeps the space. Stripping a
# character class from the whole string instead would query a path that was
# never declared, and the natural remedy for that false miss is to delete the
# anchor — which destroys real information to silence a parser bug.
unquote_entry() {
  local s="$1"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  if [[ ${#s} -ge 2 ]]; then
    if   [[ "${s:0:1}" == '"' && "${s: -1}" == '"' ]]; then s="${s:1:${#s}-2}"
    elif [[ "${s:0:1}" == "'" && "${s: -1}" == "'" ]]; then s="${s:1:${#s}-2}"
    fi
  fi
  printf '%s' "$s"
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
    # Inline flow sequence. Strip only the ONE outer [ ] delimiter pair, and
    # only as a pair — a value may legitimately end in ] without opening one.
    cleaned="$ref_paths_raw"
    cleaned="${cleaned#"${cleaned%%[![:space:]]*}"}"
    cleaned="${cleaned%"${cleaned##*[![:space:]]}"}"
    if [[ "${cleaned:0:1}" == "[" && "${cleaned: -1}" == "]" ]]; then
      cleaned="${cleaned:1:${#cleaned}-2}"
    fi
    if [[ -n "${cleaned//[[:space:]]/}" ]]; then
      IFS=',' read -ra arr <<< "$cleaned"
      for p in "${arr[@]+"${arr[@]}"}"; do
        p="$(unquote_entry "$p")"
        [[ -n "$p" ]] && paths+=("$p")
      done
    fi
  else
    while IFS= read -r p; do
      p="$(unquote_entry "$p")"
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
      # ':(literal)' — git parses a bare pathspec as wildmatch, so a dynamic-route
      # anchor like app/[locale]/page.tsx would glob `[locale]` as a character
      # class and attribute unrelated siblings' commits (app/l/, app/a/, ...) to
      # this anchor. Only reachable since ref_paths stopped stripping brackets.
      count=$(git -C "$PROJECT_DIR" log --since="$since_arg" --pretty=format: --name-only -- ":(literal)$p" 2>/dev/null | grep -c . || true)
      drift_commits=$(( drift_commits + count ))
    fi
  done
fi
drift_hit=$(( drift_commits > 0 ? 1 : 0 ))

# --- Signal 4: skill_ref_broken / skill_ref_unknown ---
# High-precision only: explicit nara-kit skill claims that don't resolve to a
# live <root>/<name>/ directory. Two forms — (A) `skills/<name>/` path tokens,
# (B) `/nara-<name>` slash-command invocations. Bare backticked skill names
# without a skills/ prefix or /nara- invocation are intentionally NOT caught
# here (would be noisy); Tier 2 semantic review handles those.
declare -a form_a_names=()
declare -a form_b_names=()
# Form A: skills/<name>/ directory path claims (repo-relative)
while IFS= read -r tok; do
  n="${tok#skills/}"; n="${n%/}"
  [[ -n "$n" ]] && form_a_names+=("$n")
done < <(grep -oE 'skills/[a-zA-Z0-9_-]+/' "$target" 2>/dev/null | sort -u || true)
# Form B: /nara-<name> slash-command invocations (not part of a longer path)
while IFS= read -r tok; do
  n="${tok##*/}"
  [[ "$n" == "nara-kit" ]] && continue
  [[ -n "$n" ]] && form_b_names+=("$n")
done < <(grep -oE '(^|[^A-Za-z0-9/])/nara-[a-zA-Z0-9_-]+' "$target" 2>/dev/null | grep -oE '/nara-[a-zA-Z0-9_-]+' | sort -u || true)

# Candidate skill roots. NARA_SKILLS_DIRS (colon-separated) replaces the whole
# autodetect list; otherwise probe the audited repo plus each agent's skill dir.
# Runtime-neutral: Claude Code and Codex roots are both probed, neither required.
declare -a skill_roots=()
if [[ -n "${NARA_SKILLS_DIRS:-}" ]]; then
  IFS=':' read -ra skill_roots <<< "$NARA_SKILLS_DIRS"
else
  skill_roots=(
    "$PROJECT_DIR/skills"
    "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
    "$HOME/.codex/skills"
    "$HOME/.agents/skills"
  )
fi
# Only a root that exists can answer the question.
declare -a live_roots=()
for r in "${skill_roots[@]+"${skill_roots[@]}"}"; do
  [[ -n "$r" && -d "$r" ]] && live_roots+=("$r")
done
# The audited repo's own tree, when it has one, is Form A's authority.
repo_root_live=0
[[ -d "$PROJECT_DIR/skills" ]] && repo_root_live=1

# resolves_in <name> <root>... -> 0 when any root holds the skill dir
resolves_in() {
  local name="$1"; shift
  local root
  for root in "$@"; do
    [[ -d "$root/$name" ]] && return 0
  done
  return 1
}

declare -a broken_refs=()
declare -a unknown_refs=()

# Form B — an installed-skill claim. Any root can answer it.
for n in "${form_b_names[@]+"${form_b_names[@]}"}"; do
  if [[ ${#live_roots[@]} -eq 0 ]]; then
    unknown_refs+=("/$n")
  elif ! resolves_in "$n" "${live_roots[@]}"; then
    broken_refs+=("/$n")
  fi
done

# Form A — a repo-relative path claim, so the audited repo answers it when it has
# a skills/ tree. When it does NOT (the normal case: memories audited from the
# consuming app repo), fall back to "does this skill exist ANYWHERE":
#   - nowhere        -> broken. Checkable and real: a removed skill is drift no
#                       matter which repo you ask from. Downgrading this to
#                       unknown silenced live drift (removed skills read healthy).
#   - some other root -> unknown. The skill exists, so there is no evidence of
#                       drift, but this repo cannot confirm the *path*. Crucially
#                       NOT resolved-clean: a bare legacy name (code-review,
#                       commit, gap) can match an unrelated third-party skill
#                       installed under an agent root, and clearing on that would
#                       hide the `nara-` migration drift class.
for n in "${form_a_names[@]+"${form_a_names[@]}"}"; do
  if [[ $repo_root_live -eq 1 ]]; then
    resolves_in "$n" "$PROJECT_DIR/skills" || broken_refs+=("skills/$n")
  elif [[ ${#live_roots[@]} -eq 0 ]]; then
    unknown_refs+=("skills/$n")
  elif resolves_in "$n" "${live_roots[@]}"; then
    unknown_refs+=("skills/$n")
  else
    broken_refs+=("skills/$n")
  fi
done

# Dedupe. Form A and Form B use distinct identifier shapes (`skills/<name>` vs
# `/<name>`) so a verdict is always attributable to the claim that produced it,
# and one ref can never land in both lists. sort -u imposes lexicographic order.
if [[ ${#broken_refs[@]} -gt 0 ]]; then
  IFS=$'\n' read -r -d '' -a broken_refs < <(printf '%s\n' "${broken_refs[@]}" | sort -u && printf '\0')
fi
if [[ ${#unknown_refs[@]} -gt 0 ]]; then
  IFS=$'\n' read -r -d '' -a unknown_refs < <(printf '%s\n' "${unknown_refs[@]}" | sort -u && printf '\0')
fi

skill_ref_broken_hit=$(( ${#broken_refs[@]} > 0 ? 1 : 0 ))
# Unknown is a coverage gap, not a defect — it contributes 0 to the score.
skill_ref_unknown_hit=$(( ${#unknown_refs[@]} > 0 ? 1 : 0 ))

# --- Score ---
score=$(( age_hit + validity_hit + drift_hit + skill_ref_broken_hit ))
if   [[ $score -eq 0 ]]; then label="healthy"
elif [[ $score -eq 1 ]]; then label="watch"
elif [[ $score -eq 2 ]]; then label="suspect"
else                          label="danger"
fi

signals_arr=()
[[ $age_hit               -eq 1 ]] && signals_arr+=("age_days")
[[ $validity_hit          -eq 1 ]] && signals_arr+=("ref_validity")
[[ $drift_hit             -eq 1 ]] && signals_arr+=("code_drift")
[[ $skill_ref_broken_hit  -eq 1 ]] && signals_arr+=("skill_ref_broken")
[[ $skill_ref_unknown_hit -eq 1 ]] && signals_arr+=("skill_ref_unknown")

signals_json=$(printf '%s\n' "${signals_arr[@]:-}" | jq -R . | jq -s 'map(select(length > 0))')
broken_json=$(printf '%s\n' "${broken_refs[@]:-}" | jq -R . | jq -s 'map(select(length > 0))')
unknown_json=$(printf '%s\n' "${unknown_refs[@]:-}" | jq -R . | jq -s 'map(select(length > 0))')

result=$(jq -nc \
  --arg file "$target" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson score "$score" \
  --argjson signals "$signals_json" \
  --argjson age_days "$age_days" \
  --argjson validity_pct "$validity_pct" \
  --argjson drift_commits "$drift_commits" \
  --argjson broken "$broken_json" \
  --argjson unknown "$unknown_json" \
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
      skill_refs_broken: $broken,
      skill_refs_unknown: $unknown
    },
    label: $label
  }')

echo "$result"

if [[ $LOG_MODE -eq 1 ]]; then
  log_path="$(dirname "$target")/.audit-log.jsonl"
  echo "$result" >> "$log_path"
fi
