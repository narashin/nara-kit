# nara-memory-audit — Tier 1 scoring + Tier 2 verify

Two-tier audit. Tier 1 is a cheap bash prefilter (~0 tokens); only flagged files reach the expensive Tier 2 semantic pass. `bounded + cheap-first` — see memory `feedback-memory-event-driven-sweep`.

## Tier 1 — mechanical signals (bash, no LLM)

`scripts/audit.sh [--log] <memory_file>` emits one-line JSON `{file, score, signals[], details, label}`. Each signal = +1.

### 1. `age_days >= 90`
Days since `verified_at` (falls back to file mtime). Override with `THRESHOLD_AGE_DAYS=N`.
Rationale: long enough to outlast a sprint, short enough that environments drift noticeably.

### 2. `ref_validity < 100%`
Fraction of declared `ref_paths` that still exist on disk (resolved against `$CLAUDE_PROJECT_DIR`). Directory refs (`skills/x/`) and file refs both checked via `-e`.
- `ref_paths` present + empty (`[]`) → 100% (nothing to disprove).
- `ref_paths` absent → grep-fallback extracts path-like tokens with a file extension from the body.
- Symbol-level refs (function/class names) not checked — too noisy without a language server.

### 3. `code_drift > 0`
Commits touching any referenced file after the memory's `verified_at` (git `--since`). A referenced file that changed after verification is a staleness signal, not proof — Tier 2 adjudicates.

### 4. `skill_ref_broken` (nara-kit-specific)
Explicit nara-kit **skill claims** that do not resolve to a live `skills/<name>/` directory. This is the single highest-signal check for this repo — 8/10 of the 2026-07-16 drifts were unprefixed skill names after the `nara-` migration.

High-precision, two forms only:
- **Form A** — `skills/<name>/` path tokens (e.g. `skills/jira-triage/` when the live dir is `skills/nara-jira-triage/`).
- **Form B** — `/nara-<name>` slash-command invocations (expected dir `skills/nara-<name>/`); `nara-kit` (the repo) is excluded.

**Deliberately NOT caught (documented limitation):** bare backticked skill names with no `skills/` prefix and no `/nara-` invocation (e.g. a body that says `` `trending-digest` `` instead of `` `nara-trending-digest` ``). Matching bare kebab-case words against a skill list is noisy (false positives on `nara-kit`, external skills like `brainstorming`). These are left to Tier 2 — but only if the file is flagged by another signal. A file that scores 0 on signals 1-3 and carries only a bare-name drift will be missed by Tier 1. Accept this; do not add a noisy signal to chase it.

### Score → label → routing

| Score | Label | Routing |
|-------|-------|---------|
| 0 | healthy | keep; not reported beyond count |
| 1 | watch | listed in report; NO Tier 2 |
| 2 | suspect | → Tier 2 verify → human decides |
| 3-4 | danger | → Tier 2 verify → archive/rewrite candidate |

## Tier 2 — semantic verify (subagent, flagged files only)

Batch flagged files (~5-8 per subagent) and run in parallel. Each subagent, per file:

1. Extract concrete verifiable claims — names of skills, files, flags, functions, commit hashes, counts, paths.
2. Verify against the live repo (`ls`/`grep`/`git`/read): skill dir existence, commit existence + message match, count accuracy, referenced-symbol existence.
3. Classify external-system claims (other repos, Multica/Jira/Confluence runtime, talks) as `UNVERIFIABLE [requires <source>]` — never guess.
4. Detect intra-memory **contradiction**: does a newer memory assert something this one denies? (The mechanical tier cannot see this; the subagent can.)
5. Return per file: `verdict ∈ {FRESH, STALE, CONTRADICTION, UNVERIFIABLE}` + evidence + a minimal fix. A pure behavioral principle with no code anchor → `FRESH` (nothing to rot).

### Subagent prompt template

> You are auditing durable memory files for staleness. For each assigned file: read it, extract verifiable claims, verify against the live repo at `<PROJECT_DIR>` using ls/grep/git/read. Skill existence: check `skills/<name>/SKILL.md`. Commit claims: `git show --stat <hash>`. External-system claims → `[UNVERIFIED: requires <source>]`, do NOT guess. A principle with no code anchor → FRESH. Return per file: `filename | verdict (FRESH/STALE/CONTRADICTION/UNVERIFIABLE) | evidence | minimal fix`. Read-only — do not modify anything.

## Apply (after human approval only)

- **anchor fix** → `Edit` the file. Slim the rot-prone anchor rather than patch-in-place where possible (see memory `feedback-memory-storage-discipline`): if the drift is a repo-derivable fact that should not have been stored, remove it, don't just correct it.
- **danger / refuted claim** → move the file to `memory/archive/` and delete its line from `MEMORY.md`. **Move, never delete** — reversible (inherited from the removed `memory-archive` skill).
- re-sync the `MEMORY.md` index (pointer count must equal file count).

Nothing is modified before explicit approval.

## Frontmatter contract

```yaml
---
name: <slug>
description: <one-line>
metadata:
  type: user | feedback | project | reference
  verified_at: <YYYY-MM-DD>     # ISO; falls back to file mtime
  ref_paths: [<repo-relative path>, ...]   # or []
---
```

`ref_paths` are repo-relative (resolved from `$CLAUDE_PROJECT_DIR`). Absolute paths, worktree paths, and invented paths are contract violations — they defeat signals 2 and 3.

## Troubleshooting

- Requires `jq`, `git`. Run `audit.sh` from the repo the memories are ABOUT (so `skills/` + git history resolve). The memory dir path is the argument.
- `verified_at` must be `YYYY-MM-DD`. Missing → mtime fallback (less reliable; mtime resets on any touch).
