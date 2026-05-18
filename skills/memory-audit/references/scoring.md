# memory-audit scoring algorithm

Quantitative 4-signal scoring for memory health. All signals are bash-runnable; no LLM judgment in scoring.

## Signal definitions

### 1. `age_days >= 90`

Days since the memory was last verified or written.

```bash
if has_frontmatter_field verified_at; then
  base=$(parse_iso_date "$verified_at")
else
  base=$(stat -f %m memory/X.md)
fi
age_days=$(( ($(date +%s) - base) / 86400 ))
[[ $age_days -ge 90 ]] && score+=1
```

**Rationale:** 90 days is a calibrated default — long enough to outlast a typical project sprint, short enough that environments drift noticeably. Override at audit invocation with `THRESHOLD_AGE_DAYS=N` if needed.

### 2. `ref_validity < 100%`

Fraction of declared `ref_paths` that still exist on disk.

```bash
if has_frontmatter_field ref_paths; then
  paths=$(parse_yaml_list ref_paths)
else
  # Fallback: extract path-like tokens from body
  paths=$(grep -oE '[a-zA-Z_][a-zA-Z0-9_/.-]*/[a-zA-Z0-9_./-]+\.(md|ts|tsx|py|json|yaml|yml|sh)' memory/X.md | sort -u)
fi

valid=0; total=0
for p in $paths; do
  total=$((total+1))
  [[ -e "$p" ]] && valid=$((valid+1))
done
validity_pct=$(( total > 0 ? valid * 100 / total : 100 ))
[[ $validity_pct -lt 100 ]] && score+=1
```

**Notes:**
- Resolved relative to project root (`$CLAUDE_PROJECT_DIR`), not memory dir.
- Empty `ref_paths` and zero grep hits → assume 100% (cannot disprove).
- Symbol-level refs (function/class names) not checked here — too noisy without language server.

### 3. `code_drift > 0`

Commits touching any referenced file after the memory's `verified_at`.

```bash
since=$(verified_at_or_mtime)
drift=0
for p in $paths; do
  count=$(git log --since="$since" --pretty=format: --name-only -- "$p" 2>/dev/null | grep -c .)
  drift=$((drift + count))
done
[[ $drift -gt 0 ]] && score+=1
```

**Notes:**
- Only files inside the git repo are checked. Out-of-repo paths skip drift check.
- Drift > 0 doesn't mean the memory is wrong — just that the underlying code changed. Combined with age/validity, signals risk.

### 4. `conflict_found`

A newer memory file in the same dir mentions deprecation/supersession of this one.

```bash
conflict=0
for other in memory/*.md; do
  [[ "$other" == "$target" ]] && continue
  [[ $(stat -f %m "$other") -le $(stat -f %m "$target") ]] && continue
  target_name=$(basename "$target" .md)
  if grep -qE "(supersedes|replaces|deprecates):.*${target_name}" "$other"; then
    conflict=1
    break
  fi
done
[[ $conflict -eq 1 ]] && score+=1
```

**Notes:**
- Requires explicit `supersedes: <name>` markers in newer memories. Vague semantic conflicts are NOT detected — too LLM-dependent for a deterministic auditor.
- Adding `supersedes:` to a new memory is a manual discipline.

## Output JSON contract

`scripts/audit.sh <memory_file>` emits one line of JSON:

```json
{
  "file": "memory/feedback_x.md",
  "score": 2,
  "signals": ["age_days", "code_drift"],
  "details": {
    "age_days": 142,
    "validity_pct": 100,
    "drift_commits": 3,
    "conflict": false
  },
  "label": "suspect"
}
```

Labels:

| Score | Label |
|-------|-------|
| 0 | healthy |
| 1 | watch |
| 2 | suspect |
| 3-4 | danger |

## Configuration

Environment variables (optional):
- `THRESHOLD_AGE_DAYS` — override 90-day age cutoff.
- `MEMORY_DIR` — override default `~/.claude/projects/<project>/memory/`.

## Determinism

All 4 signals are deterministic given the same inputs (file mtime, frontmatter, git history, sibling memory contents). Re-running the audit on unchanged state yields the same scores. This is intentional — score drift only happens when reality changes.

## Coverage limitations (known)

Two design trade-offs reduce signal coverage:

### `ref_paths: []` silences 2 of 4 signals

When `ref_paths` is explicitly empty (declared `[]`), both `ref_validity` and `code_drift` checks become unreachable. Net effect: such a memory is effectively audited on `age_days` alone (signal 1) and `conflict_found` (signal 4 — only fires if a *newer* memory deprecates it).

**Mitigation discipline:**
- Declare actual refs whenever the memory makes claims tied to files/symbols (e.g. `ref_paths: [skills/foo/SKILL.md, docs/x.md]`).
- Use `[]` *only* for pure conventions/feedback memories that intentionally have no file ties (rare).
- When a memory's body mentions file paths in prose (not as examples), they belong in `ref_paths`.

### Dishonest timestamping is not detected

`verified_at` is a self-declared field. A user re-stamping it without actually re-checking content will reset the age signal silently. The audit cannot tell apart "actually re-verified today" from "I edited the date." This is a fundamental limit of declarative metadata.

**Mitigation:** rely on `code_drift` for objective freshness — it uses git history, which the user cannot easily fake. Combined with `ref_paths` discipline (above), drift compensates for honest timestamping failures.

## Receipt format clarifications

For consistency:

- **`total`** = count of memory files audited. Excludes `MEMORY.md` (the index) and any file under `archive/`.
- **`flagged: none`** = literal string when no memory has score >= 2. Drop the field entirely is also acceptable.
- **JSON aggregate vs. human receipt** — the receipt template in SKILL.md is the *user-facing* surface. The per-file JSON from `audit.sh` is internal — only surface it on explicit user request (e.g., `--verbose`) or when triaging a specific flagged file.
