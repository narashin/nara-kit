# nara-kit

Agent Skills repo — 49 opinionated workflow skills by shinnara. Installed via `npx skills add narashin/nara-kit` into Claude Code and Codex.

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
- Body: steps, modes, rules. Reference files via relative links: `[label](references/file.md)`
- Keep body actionable — Claude executes this, not humans

## Conventions

- All skills work standalone. External plugins (codex) are optional enhancements with manual fallbacks
- Code comments and debug logs in English
- User-facing text (PR body, commit message, docs) follows project language (usually Korean)
- No `any` type in any TypeScript

## Output Contract

All nara-kit skills follow the shared output contract: [references/output-contract.md](references/output-contract.md).
- Response = receipt (3-6 lines), not full artifact
- 4 elements: Outcome / Evidence / Artifact Paths / Next Action
- Status labels: `recorded only` / `applied` / `pending escalation` / `skipped`
- MCP side effects must be declared explicitly
- Escalation uses `→ ESCALATE:` prefix
- Errors use `❌ 실패:` block

Skills inherit this contract automatically — do not duplicate the reference in individual SKILL.md files.

## Eval Structure

```yaml
# evals/<name>/eval.yaml
name: <name>-eval
skill: <name>
graders:
  - type: code    # Assertion-based
  - type: text    # Regex/pattern matching
tasks:
  - "tasks/*.yaml"
```

Run: `waza eval <skill-name>` (requires `.waza.yaml` config at root)

## Workflow Architecture

**There is no workflow skill.** Skills are invoked directly (`/nara-<name>`); `nara-now` reads the session state and names the next command. The four meta-skills that used to own the flow (`workflow-orchestrator`, `workflow-dev-mode`, `workflow-doc-mode`, `workflow-viz`) were removed on 2026-08-14 after measurement showed **1 invocation in 60 days combined** (three of them zero) against `nara-now` at 74 — packaging a flow as a skill means nobody calls it.

Recommended order, not an executed pipeline:

- **개발**: (prep | ac-draft) → plan → implement → verify → code-review → reflect. Verify is 2-track — code AC via `nara-gap`, `browser-visible: yes` AC via `nara-browser-verify` (see `docs/adr/0001-verify-browser-ac-at-runtime.md`). Conditional: grill (large/greenfield), gap up front (brownfield handover), adr (structural decision).
- **기획**: (prep | ac-draft) → grill → spec → claim-audit → publish-spec → reflect
- The Implementation Notes Gate contract now lives in `nara-implement` (`references/implementation-notes.md`) — it moved with the retirement, it was not dropped.

See [skills/README.md](skills/README.md) for the skill catalog + mermaid diagrams.

## When Adding a New Skill

1. Create `skills/nara-<name>/SKILL.md` with proper frontmatter — `nara-` prefix mandatory, `name:` field must equal the directory name
2. Create `skills/nara-<name>/README.md` — thin human guide (Claude does NOT read it at runtime): purpose + invocation (`/nara-<name>`, `$nara-<name>`) + USE FOR / DO NOT USE FOR + backlinks to `../README.md` and `SKILL.md`. Derive from SKILL.md frontmatter to avoid drift. Every skill folder has one — `skills/*/README.md` is tracked (not gitignored). Setup-heavy skills (config/MCP) may add a rich hand-written guide instead (see `nara-slack-to-jira/README.md`)
3. Create `evals/<name>/eval.yaml` + `tasks/` + `fixtures/`
4. Update `skills/README.md` catalog table — keep skill count accurate (root `README.md` has no per-skill table; the catalog + mermaids live in `skills/README.md`)
5. If the skill sits in a flow, update `skills/README.md`'s recommended order and the relevant handoff lines
6. New skill inherits output contract automatically — do not add per-skill output-contract reference (CLAUDE.md handles it)

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

**Sibling-skill links:** a skill may reference another skill's file with a relative path (`../nara-<other>/references/<file>.md`) instead of duplicating it — the owner skill keeps the knowledge (see `docs/adr/0002-link-sibling-skill-references.md`). This assumes the default `--skill '*'` bulk install, so every such reference MUST state what happens when the file is absent (skip and proceed, or return `Unverifiable`). `waza check` reports these as `link escapes skill directory` **whether or not the target exists** — it is not a breakage detector. Before a release, run:

```bash
grep -rn "](\.\./nara-[^)]*)" --include="*.md" skills/ | while IFS=: read -r f _ line; do d=$(dirname "$f"); echo "$line" | grep -oE "\]\(\.\./nara-[^)]+\)" | tr -d "]()" | while read -r rel; do [ -e "$d/$rel" ] || echo "BROKEN $f -> $rel"; done; done
```

No output = all sibling links resolve. Any `BROKEN` line blocks the release.

**What ships:** only `skills/<name>/` directories. `README.md`, `skills/README.md`, `CLAUDE.md`, `CHANGELOG.md`, `references/`, and `evals/` (gitignored) never reach consumers — pushes touching only those need no consumer action.

**Renaming a skill is breaking:** consumers keep the old copy under the old name; they must remove it and reinstall.

**Verify after release (consumer side):**
- `ls ~/.claude/skills | grep -c '^nara-'` → 48 (+ `naranizer` = 49)
- Run a quick smoke test of the changed skill in a fresh session

Note: `claude-mem:version-bump` no longer applies — there are no manifests to bump.
