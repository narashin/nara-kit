# nara-kit

Agent Skills repo — 59 opinionated workflow skills by shinnara. Installed via `npx skills add narashin/nara-kit` into Claude Code and Codex.

## Structure

```
skills/<name>/SKILL.md          # Skill definition (YAML frontmatter + markdown body)
skills/<name>/references/       # Supporting templates, examples, phase docs
evals/<name>/eval.yaml          # Waza evaluation config
evals/<name>/tasks/*.yaml       # Test scenarios
evals/<name>/fixtures/          # Test fixtures (sample files, mock diffs)
```

Naming: every skill is prefixed `nara-` (dir name == frontmatter `name`). Sole exception: `naranizer` (already nara-branded). Invocation: `/nara-<skill>` in Claude Code, `$nara-<skill>` in Codex.

## Skill Anatomy

Every SKILL.md must have YAML frontmatter:

```yaml
---
name: <skill-name>              # Must match directory name
description: >-
  One-line purpose.
  USE FOR: trigger phrases.
  DO NOT USE FOR: anti-patterns (with redirect).
---
```

- `description` drives Claude's skill routing — be precise on USE FOR / DO NOT USE FOR
- **User-only skills.** A skill that writes to a remote system on the user's behalf (Confluence, Jira, a release tag) is invocation-gated on both hosts: `disable-model-invocation: true` in the SKILL.md frontmatter (Claude Code) **and** `skills/<name>/agents/openai.yaml` with `policy.allow_implicit_invocation: false` (Codex ignores the SKILL.md flag). Cost: the description leaves the context, so USE FOR routing stops for that skill and the user types the slash command. Current set: `publish-spec`, `spec-revision`, `slack-to-jira`, `worklog`, `jira-triage`, `release-finalize`. `tools/check-docs.py` fails when only one surface is set. `waza check` reports these six as 8/9 spec compliance (`spec-allowed-fields: disable-model-invocation`) because the field is a Claude Code host extension outside the agentskills.io core list; that one line is expected, not a regression. `npx skills add . --list` still finds all of them
- **Catalog tag.** `metadata: { nara: { scope: multica } }` marks a skill that cannot run without the `multica` CLI. Claude Code ignores `metadata`; only `tools/check-docs.py` reads it
- Body: steps, modes, rules. Reference files via relative links: `[label](references/file.md)`
- Keep body actionable — Claude executes this, not humans

## Conventions

- All skills work standalone. External plugins (codex) are optional enhancements with manual fallbacks
- Code comments and debug logs in English
- User-facing text (PR body, commit message, docs) follows project language (usually Korean)
- No `any` type in any TypeScript

## Output Contract

All nara-kit skills follow the shared output contract: [skills/nara-now/references/output-contract.md](skills/nara-now/references/output-contract.md). It lives inside a skill directory because only `skills/<name>/` ships to consumers; a repo-root file never reached an installed skill. Every SKILL.md carries one pointer line to it right under its H1 (`tools/check-docs.py` fails a skill without it).
- Response = receipt (3-6 lines), not full artifact
- 4 elements: Outcome / Evidence / Artifact Paths / Next Action
- Status labels: `recorded only` / `applied` / `pending escalation` / `skipped`
- MCP side effects must be declared explicitly
- Escalation uses `→ ESCALATE:` prefix
- Errors use `❌ 실패:` block

The pointer line is the only per-skill reference: do not copy the contract's rules into a SKILL.md. A skill whose body deliberately differs (for example nara-rewrite returns the rewrite itself, not a receipt) says so in its body; the pointer line already states that the body wins.

## Eval Structure

```yaml
# evals/<name>/eval.yaml
name: <name>-eval
skill: <name>
graders:
  - type: code                 # eval-level: universally-true properties only
    name: real_run             # provenance gate -- mandatory, see below
    config:
      assertions:
        - "len(output) > 40"
        - "'Mock response for:' not in output"
  - type: text                 # Regex/pattern matching
tasks:
  - "tasks/*.yaml"
```

Eval-level graders run against **every** task including anti-trigger ones, so they may assert only universally-true properties. All behavioural discrimination belongs in each task's `expected.output_contains` / `output_not_contains`.

### What can and cannot be measured here

There is no `waza eval` command — it is `waza run`. But neither engine measures a skill in this repo:

| Path | Status |
|---|---|
| `waza run` with `executor: copilot-sdk` | Needs a Copilot seat (unassigned). Has never run |
| `waza run` with `executor: mock` | Runs, prints scores, **measures nothing** — the mock never invokes the skill |
| `waza check <skill>` | Works. Static only: tokens, links, frontmatter, description quality |
| `waza coverage` | Works. Structural only: does a suite exist, which grader types |
| `waza grade` on a real run's JSON | Works. The only path to a behavioural score |
| `tools/eval-fixture.py generate <skill>` | Works, bills the headless quota. Hermetic `claude -p` (no settings, MCP or tools) with SKILL.md + references appended as system prompt. Real text for grader validation (`validate --right-from gen`), not a skill benchmark: tools are off, so git/gh steps are narrated, never run. Model is the CLI built-in default unless `--model` pins one; only the skill's own `references/*.md` are appended (sibling links are not followed); validate warns when a generation predates a SKILL.md change |

The mock echoes the prompt, the task's own `name`/`description`, and the fixture text verbatim. Grading that measures the eval against itself: `nara-gap` scored 4/8 purely because assertion strings appeared in its own description (`Score` matched `"produces docs/gap.md with a score (0-100)"`, case-insensitively). **Every suite therefore carries the `real_run` provenance gate, which fails all tasks under mock on purpose.** A loud 0/8 beats a quiet tautology that reads like a measurement. Never remove that gate to make a mock run look green.

### Validating that graders discriminate

What is measurable without an engine is the graders. Give them a correct output and an incorrect one; graders that cannot separate those cannot measure a skill either.

```bash
tools/eval-fixture.py validate <skill>      # probe → fill both sides → grade → report
```

The table lives in `evals/<skill>/validation.yaml` (`right:` / `wrong:` keyed by task id). Populate `wrong:` from **behaviour the skill actually produced** — invented failures are trivially discriminated and prove nothing. Expected result: every task passes on `right` and fails on `wrong`. A `wrong`-side pass means the assertion is satisfiable by incorrect output; a `right`-side failure means it is unsatisfiable by correct output. Both are grader defects, not skill findings.

Reference suite: `evals/nara-gap/validation.yaml` — 8/8 discriminate. Run artifacts land in `results/` (gitignored).

## Workflow Architecture

**There is no workflow skill.** Skills are invoked directly (`/nara-<name>`); `nara-now` reads the session state and names the next command. The four meta-skills that used to own the flow (`workflow-orchestrator`, `workflow-dev-mode`, `workflow-doc-mode`, `workflow-viz`) were removed on 2026-08-14 after measurement showed **1 invocation in 60 days combined** (three of them zero) against `nara-now` at 74 — packaging a flow as a skill means nobody calls it.

Recommended order, not an executed pipeline:

- **개발**: (prep | ac-draft) → plan → implement → verify → code-review → reflect. Verify is 2-track — code AC via `nara-gap`, `browser-visible: yes` AC via `nara-browser-verify` (see `docs/adr/0001-verify-browser-ac-at-runtime.md`). What either track cannot judge (gap's `Needs Confirm`, browser-verify's `Unverifiable`) goes to a human through `nara-qa-sheet` — a handoff, not a third verdict. Conditional: grill (large/greenfield), gap up front (brownfield handover), adr (structural decision).
- **기획**: (prep | ac-draft) → grill → spec → claim-audit → publish-spec → reflect
- The Implementation Notes Gate contract now lives in `nara-implement` (`references/implementation-notes.md`) — it moved with the retirement, it was not dropped.

See [skills/README.md](skills/README.md) for the skill catalog + mermaid diagrams.

## When Adding a New Skill

1. Create `skills/nara-<name>/SKILL.md` with proper frontmatter — `nara-` prefix mandatory, `name:` field must equal the directory name
2. Create `skills/nara-<name>/README.md` — thin human guide (Claude does NOT read it at runtime): purpose + invocation (`/nara-<name>`, `$nara-<name>`) + USE FOR / DO NOT USE FOR + backlinks to `../README.md` and `SKILL.md`. Derive from SKILL.md frontmatter to avoid drift. Every skill folder has one — `skills/*/README.md` is tracked (not gitignored). Setup-heavy skills (config/MCP) may add a rich hand-written guide instead (see `nara-slack-to-jira/README.md`)
3. Create `evals/<name>/eval.yaml` + `tasks/` + `fixtures/` — the eval-level `real_run` provenance gate is mandatory (see Eval Structure). Add `validation.yaml` and run `tools/eval-fixture.py validate <name>` once the skill has produced real output to copy from
4. Add one row to the `skills/README.md` catalog under the **intent** group it serves (groups are by what the user wants to do, not by lifecycle stage), add the short name to the matching row of the root `README.md` "Skills by intent" index, and bump the counts. A skill that cannot run without the `multica` CLI goes under **Multica 연동** and carries `metadata: { nara: { scope: multica } }` in its frontmatter. Then run `tools/check-docs.py` — it fails on a missing/duplicate row, a stale count, or a tag/group mismatch
5. If the skill sits in a flow, update `skills/README.md`'s recommended order and the relevant handoff lines
6. Put the output-contract pointer line under the SKILL.md H1, copied from any existing skill (`> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. ...`). Repo-level CLAUDE.md does not reach installed skills, so this line is the only way a consumer's agent sees the contract

## When Modifying a Skill

1. Run `waza check skills/<name>` before and after — verify no regression on tokens, links, advisories
2. If changing `description` field, verify routing still matches the intended triggers — and regenerate `README.md` (purpose/USE FOR/DO NOT lines derive from `description`)
3. For substantive behavior changes, use `/nara-skill-forge <name>` — EPT subagent loop with iterative fixes
4. Check cross-references — other skills may link to this one via `references/`

## Release / Redeploy

nara-kit ships as plain Agent Skills — no version manifest, no marketplace, no restart cycle. The GitHub repo's `main` branch IS the release. Git tags (`vMAJOR.MINOR.PATCH`) are immutable snapshots and, together with `CHANGELOG.md`, are the version source of truth.

**Flow:**

1. Commit on `main` (user commits manually — never auto-commit).
2. Record notable changes under `CHANGELOG.md` `[Unreleased]` (Added/Changed/Removed/Fixed). On release, move `[Unreleased]` under the new `vX.Y.Z` heading and tag the commit. Version bump: skill rename/removal or invocation/artifact-path change = **major**; new skill or additive behavior = **minor**; fix/doc = **patch**.
3. Push to BOTH remotes: `git push origin main && git push github main && git push --tags` (both).
   (`origin` = LINE internal; `github` = github.com/narashin/nara-kit — consumers install from github).
4. Consumer side: `npx skills update` (or re-run `npx skills add narashin/nara-kit --global --agent claude-code --agent codex --skill '*'`).

**Sibling-skill links:** a skill may reference another skill's file with a relative path (`../nara-<other>/references/<file>.md`) instead of duplicating it — the owner skill keeps the knowledge (see `docs/adr/0002-link-sibling-skill-references.md`). This assumes the default `--skill '*'` bulk install, so every such reference MUST state what happens when the file is absent (skip and proceed, or return `Unverifiable`). `waza check` reports these as `link escapes skill directory` **whether or not the target exists** — it is not a breakage detector.

**Catalog check (blocks every release and any commit that adds, removes or regroups a skill):**

```bash
tools/check-docs.py
```

`Pass: ...` = safe. Any other line blocks it. It checks, stdlib only: every skill directory has exactly one `skills/README.md` catalog row and no row lacks a directory; every skill count written in `README.md`, `skills/README.md` and `CLAUDE.md` equals the directory count; `metadata.nara.scope: multica` tags and the **Multica 연동** group agree; every sibling link resolves, both `](../nara-<other>/...)` from a SKILL.md and `](../../nara-<other>/...)` from a `references/` file (this replaced the old grep one-liner, which missed the second form); every skill has `name` == directory, a `description`, and a `README.md`; `disable-model-invocation: true` and `agents/openai.yaml` `allow_implicit_invocation: false` appear together or not at all; every SKILL.md carries the output-contract pointer before its first `##` section and the contract file exists. Its own docstring lists the checks in order. Count drift is its reason to exist: the catalog sat at 51 against 55 directories, and the root README said 55 next to 56, and neither was caught by `waza` or by eye.

**What ships:** only `skills/<name>/` directories. `README.md`, `skills/README.md`, `CLAUDE.md`, `CHANGELOG.md`, `references/`, and `evals/` never reach consumers — pushes touching only those need no consumer action.

**Eval identifier scan (blocks any commit touching `evals/`).** Suites are tracked so skill performance is measurable, but this repo is public. Tasks and fixtures must use placeholders (`PROJ-123`, `OPS-88`, `web-ui`, `api-server`, `git.example.com`, `acme-sre`, `C0123456789`), never real ticket keys, hosts, repo names, Slack channel IDs, or names:

```bash
grep -rInE 'LYRIS|SANDY|linecorp|LINE-SRE|iris-ui|iris-api|C0[0-9A-Z]{8,}|/p1[0-9]{15}' evals --exclude-dir=results \
  | grep -vE 'C0123456789|/p170000000000000'
```

No output = safe to commit. Any hit blocks it. The second `grep -v` whitelists the placeholders themselves, which match the same shapes — extend it when you add a placeholder, never widen the first pattern.

Two traps, both hit in practice:
- **Preserve the distinctions a task asserts.** The jira-triage suites grade FE→BE repo routing, so the two placeholder repo names must stay opposed in `output_contains` / `output_not_contains`.
- **Slack message timestamps are live pointers**, not just channel IDs. They are 16 digits after `p` (`/p1778744277781889`); an off-by-one in the digit count silently leaves them in place.

**Renaming a skill is breaking:** consumers keep the old copy under the old name; they must remove it and reinstall.

**Verify after release (consumer side):**
- `ls ~/.claude/skills | grep -c '^nara-'` → 58 (+ `naranizer` = 59)
- Run a quick smoke test of the changed skill in a fresh session

Note: `claude-mem:version-bump` no longer applies — there are no manifests to bump.
