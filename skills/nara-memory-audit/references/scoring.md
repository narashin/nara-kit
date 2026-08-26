# nara-memory-audit — Tier 1 scoring + Tier 2 verify

Two-tier audit. Tier 1 is a cheap bash prefilter (~0 tokens); only flagged files reach the expensive Tier 2 semantic pass. `bounded + cheap-first` — see memory `feedback-memory-event-driven-sweep`.

## Tier 1 — mechanical signals (bash, no LLM)

`scripts/audit.sh [--log] <memory_file>` emits one-line JSON `{file, score, signals[], details, label}`.

Four signals score +1 each: `age_days`, `ref_validity`, `code_drift`, `skill_ref_broken`. `skill_ref_unknown` also appears in `signals[]` but scores **0** — it records a check the run could not perform, not a defect. So `signals` may be longer than `score`; derive the score from the field, never by counting the array.

### 1. `age_days >= 90`
Days since `verified_at` (falls back to file mtime). Override with `THRESHOLD_AGE_DAYS=N`.
Rationale: long enough to outlast a sprint, short enough that environments drift noticeably.

### 2. `ref_validity < 100%`
Fraction of declared `ref_paths` that still exist on disk. Each entry is tried under `$CLAUDE_PROJECT_DIR` and then as given — the second attempt is what lets an absolute anchor resolve, but it is unconditional, so a **relative** entry can also resolve against the caller's cwd if that happens to be a different repo. Directory refs (`skills/x/`) and file refs both checked via `-e`.
- `ref_paths` present + empty (`[]`) → 100% (nothing to disprove).
- `ref_paths` absent → grep-fallback extracts path-like tokens (must contain a `/` and end in a known extension) from the whole file, frontmatter included. The token pattern excludes `[` and `]`, so a bracketed anchor is invisible to the fallback and yields the vacuous `total=0` → 100%. Declare `ref_paths` explicitly for such files.
- Symbol-level refs (function/class names) not checked — too noisy without a language server.

**Entries are read, not scrubbed.** Per entry: trim surrounding whitespace, then strip at most one matched pair of surrounding quotes; for the inline flow form, strip at most one outer `[ ]` pair, and only as a pair. Nothing else is removed, because characters that look like YAML syntax are routinely part of a real filename — `app/[locale]/page.tsx` (the dynamic-route convention of several mainstream frameworks) and any path under `Mobile Documents` are both legitimate. Deleting a character class from the whole value instead queries a path that was never declared, so a present file reports missing forever. The remedy a reader is then nudged toward — dropping the anchor from `ref_paths` — destroys real information to silence a parser bug, and disarms signals 2 and 3 permanently. Fix the reader, never the anchor.

### 3. `code_drift > 0`
Commits touching any referenced file after the memory's `verified_at` (git `--since`). A referenced file that changed after verification is a staleness signal, not proof — Tier 2 adjudicates.

### 4. `skill_ref_broken` / `skill_ref_unknown` (nara-kit-specific)
Explicit nara-kit **skill claims** that do not resolve to a live skill directory. Historically the highest-yield check for this repo: unprefixed skill names left behind by the `nara-` migration. `[UNVERIFIED: the earlier "8 of 10 drifts" figure cited no source and the underlying drift set is not recorded in this repo — treat the ranking as a rule of thumb, not a measurement.]`

High-precision, two forms only. They make different claims, so each resolves differently and is **reported under its own identifier shape** — a verdict is always attributable to the claim that produced it, and one reference can never land in both the broken and unknown lists:

| Form | Shape in the memory | Claim | Reported as |
|---|---|---|---|
| A | `skills/<name>/` path token | a repo-relative **path** exists | `skills/<name>` |
| B | `/nara-<name>` invocation | the **skill** is installed | `/<name>` |

Form A example: `skills/jira-triage/` when the live dir is `skills/nara-jira-triage/`. Form B excludes `nara-kit` (the repo, not a skill).

Roots are probed in order — `$NARA_SKILLS_DIRS` (colon-separated, replaces the whole probe list), else `$CLAUDE_PROJECT_DIR/skills`, `${CLAUDE_CONFIG_DIR:-~/.claude}/skills`, `~/.codex/skills`, `~/.agents/skills`. Runtime-neutral: neither agent's directory is required to exist. Every declared root is probed, not just the first.

`NARA_SKILLS_DIRS` governs the **probe list only**. Form A's authority test is a direct look at `$CLAUDE_PROJECT_DIR/skills`, which the override does not redirect — so an audited repo that happens to contain any directory named `skills/` (its own unrelated one) is treated as the authority, and toolkit path claims are reported `skill_ref_broken` against it. The remedy is `CLAUDE_PROJECT_DIR`, not `NARA_SKILLS_DIRS`. `[UNVERIFIED: not observed in practice — the collision needs a consuming repo whose own skills/ directory shares the name.]`

**Form B** resolves against any root. Absent from all of them → `skill_ref_broken`. No root discoverable at all → `skill_ref_unknown`.

**Form A** is answered by the audited repo when it has a `skills/` tree — that tree is authoritative, and a name it lacks is broken even if an agent root happens to have one. When the repo has **no** `skills/` tree (the normal case: memories audited from the consuming application repo), it falls back to existence-anywhere:

| Repo tree | Skill found in another root | Verdict |
|---|---|---|
| present | — | repo decides: found → clean, absent → `skill_ref_broken` |
| absent | nowhere | `skill_ref_broken` |
| absent | yes | `skill_ref_unknown` |

**Why "absent everywhere" is broken, not unknown.** A skill removed from the toolkit is absent from every root, so the claim is refutable from any repo — no `skills/` tree needed. Downgrading it to unknown made removed skills read `healthy` in exactly the prescribed scenario, silencing live drift. Measured on this repo's own 48 memory files audited from a consuming repo: three references to skills deleted in 0.21.0 contributed 0 to the score under the downgrade and contribute 1 with the fallback, moving their files from `watch` to `suspect` and so into Tier 2 where they belong.

**Why a match under an agent root only earns `unknown`.** Clearing on it would defeat the signal. The pre-`nara-` migration names (`code-review`, `commit`, `gap`, `jira-triage`) collide with generically-named third-party skills installed under those roots — `code-review` really does exist under a Codex skills dir — so a stale repo path would resolve against an unrelated skill and the migration drift class, the whole reason this signal exists, would go unflagged. `unknown` says the honest thing: the skill exists, so there is no evidence of drift, but this repo cannot confirm the path.

**A Form B mention never settles a Form A claim.** Tempting (same skill name, one is resolvable) and wrong: it re-opens the widening above through the back door, so adding `/nara-x` to a file would erase the verdict on an unchanged, still-false `skills/nara-x/` claim.

**`skill_ref_unknown` scores 0.** A check the run cannot perform is not a defect. Report it as coverage the run did not have.

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

> You are auditing durable memory files for staleness. For each assigned file: read it, extract verifiable claims, verify against the live repo at `<PROJECT_DIR>` using ls/grep/git/read. Read-only — do not modify anything.
>
> **Skill claims** — mirror Tier 1's two forms, or you will contradict it.
> A `skills/<name>/` **path** claim is answered by `<PROJECT_DIR>/skills/` when that directory exists: present → FRESH, absent → STALE, and a same-named skill under an agent root does **not** rescue it (bare pre-`nara-` names collide with unrelated third-party skills). If `<PROJECT_DIR>/skills/` does not exist, check the agent roots (`$NARA_SKILLS_DIRS` if set, else `${CLAUDE_CONFIG_DIR:-~/.claude}/skills`, `~/.codex/skills`, `~/.agents/skills`): found anywhere → `UNVERIFIABLE` (the skill exists, but you cannot confirm the path from here), found nowhere → STALE.
> A `/nara-<name>` **invocation** claim is answered by any of those roots: found → FRESH, absent from all → STALE, no root readable → `UNVERIFIABLE`.
> Existence means the directory holds a `SKILL.md`. Tier 1 only tests that the directory exists, so a gutted install is the one case where you may legitimately be stricter than the score you were handed — say so in the evidence.
>
> Commit claims: `git show --stat <hash>`. External-system claims → `[UNVERIFIED: requires <source>]`, do NOT guess. A principle with no code anchor → FRESH. Return per file: `filename | verdict (FRESH/STALE/CONTRADICTION/UNVERIFIABLE) | evidence | minimal fix`.

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

Prefer repo-relative `ref_paths` (resolved from `$CLAUDE_PROJECT_DIR`) — those are what signal 3 can read git history for. Worktree paths and invented paths are contract violations. An absolute path is the honest form for an anchor that genuinely lives outside any repo (an external notes vault, a machine-local config): it still answers signal 2, but signal 3 stays blind to it. Do not "fix" such a path by deleting it.

## Troubleshooting

- Requires `jq`, `git`. Run `audit.sh` from the repo the memories are ABOUT (so `skills/` + git history resolve). The memory dir path is the argument.
- `verified_at` must be `YYYY-MM-DD`. Missing → mtime fallback (less reliable; mtime resets on any touch).
