# nara-kit

Claude Code plugin — 37 opinionated workflow skills by shinnara.

## Structure

```
skills/<name>/SKILL.md          # Skill definition (YAML frontmatter + markdown body)
skills/<name>/references/       # Supporting templates, examples, phase docs
hooks/hooks.json                # Plugin-provided hooks (runs in all projects that install nara-kit)
evals/<name>/eval.yaml          # Waza evaluation config
evals/<name>/tasks/*.yaml       # Test scenarios
evals/<name>/fixtures/          # Test fixtures (sample files, mock diffs)
```

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

- All skills work standalone. External plugins (superpowers, codex) are optional enhancements with manual fallbacks
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

Two orchestrated modes — `workflow-orchestrator` routes requests:

- **Dev mode** (`workflow-dev-mode`): 6-step core spine `gap → plan → execute → verify → code-review → reflect` (entry: prep/ac-draft; conditional satellites: brainstorm/adr/impl-notes)
- **Doc mode** (`workflow-doc-mode`): clarify → prep → spec → publish → reflect

See [skills/README.md](skills/README.md) for the skill catalog + mermaid diagrams.

## Hooks

Plugin-provided hooks in `hooks/hooks.json` — run in every project that installs nara-kit.

| Event | Purpose |
|-------|---------|
| SessionStart | Silently audit auto-memories via `memory-audit`; surface `systemMessage` when any memory scores ≥2 (flag count) |

Hooks use prompt-based evaluation (semantic, not mechanical). Always `approve` — never block.

## When Adding a New Skill

1. Create `skills/<name>/SKILL.md` with proper frontmatter
2. Create `evals/<name>/eval.yaml` + `tasks/` + `fixtures/`
3. Update `skills/README.md` catalog table — keep skill count accurate (root `README.md` has no per-skill table; the catalog + mermaids live in `skills/README.md`)
4. If skill participates in workflow, update `workflow-dev-mode` or `workflow-doc-mode` references
5. New skill inherits output contract automatically — do not add per-skill output-contract reference (CLAUDE.md handles it)

## When Modifying a Skill

1. Run `waza check skills/<name>` before and after — verify no regression on tokens, links, advisories
2. If changing `description` field, verify routing doesn't break (test with `workflow-orchestrator` eval)
3. For substantive behavior changes, use `/nara-kit:skill-forge <name>` — EPT subagent loop with iterative fixes
4. Check cross-references — other skills may link to this one via `references/`

## Release / Redeploy

Changes to skills, hooks, or any plugin file are **not live** until the plugin is republished and reinstalled. Local edits affect only this repo, not other projects that consume nara-kit.

**Trigger this flow whenever any of these change:**
- `skills/**/*` — SKILL.md, references, assets (NOT `skills/README.md`, which is docs — see skip list)
- `hooks/hooks.json`
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- `commands/**` (if added later)

**Steps:**

1. **Version bump (semver):**
   - Patch (`0.1.1 → 0.1.2`): bug fix, doc fix, single skill tweak
   - Minor (`0.1.x → 0.2.0`): new skill, new hook, breaking skill rename
   - Major (`0.x.y → 1.0.0`): incompatible workflow restructure
   - Bump BOTH `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` to the same version
2. **Commit + push** to `origin/main`. Tag the release: `git tag v<version> && git push --tags`
3. **Marketplace refresh** (consumer side): `/plugin marketplace update nara-kit`
4. **Plugin update**: `/plugin update nara-kit` (or reinstall if first time)
5. **Restart Claude Code** — hooks are loaded at SessionStart only; without restart new/changed hooks do not activate

**Automation:** `claude-mem:version-bump` handles steps 1-2 (bumps all manifests, tags, optionally publishes GitHub release). Prefer it over manual bumps.

**Skip release when:** changes touch only `evals/**`, `README.md`, `skills/README.md`, `CLAUDE.md`, or development tooling — these are docs, not shipped skill behavior.

**Verify after release:**
- `ls ~/.claude/plugins/cache/nara-kit/nara-kit/` should show the new version directory
- `ls ~/.claude/plugins/cache/nara-kit/nara-kit/<new-version>/skills/` should list the new/changed skill
- Run a quick smoke test of the changed skill in a fresh Claude Code session
