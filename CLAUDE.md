# nara-kit

Claude Code plugin — 26 opinionated workflow skills by @shinnara.

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

- All skills work standalone. External plugins (superpowers, ouroboros, codex) are optional enhancements with manual fallbacks
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

- **Dev mode** (`workflow-dev-mode`): prep → gap → plan → execute → verify → review → reflect
- **Doc mode** (`workflow-doc-mode`): clarify → prep → spec → publish → reflect

See README.md mermaid diagrams for full flow.

## Hooks

Plugin-provided hooks in `hooks/hooks.json` — run in every project that installs nara-kit.

| Event | Purpose |
|-------|---------|
| Stop | Remind `/reflect` (substantial work) and `/adr` (architectural decisions) before session end |

Hooks use prompt-based evaluation (semantic, not mechanical). Always `approve` stop — never block.

## When Adding a New Skill

1. Create `skills/<name>/SKILL.md` with proper frontmatter
2. Create `evals/<name>/eval.yaml` + `tasks/` + `fixtures/`
3. Update README.md skill table — keep skill count accurate
4. If skill participates in workflow, update `workflow-dev-mode` or `workflow-doc-mode` references
5. New skill inherits output contract automatically — do not add per-skill output-contract reference (CLAUDE.md handles it)

## When Modifying a Skill

1. Run `waza check skills/<name>` before and after — verify no regression on tokens, links, advisories
2. If changing `description` field, verify routing doesn't break (test with `workflow-orchestrator` eval)
3. For substantive behavior changes, use `/nara-kit:skill-forge <name>` — EPT subagent loop with iterative fixes
4. Check cross-references — other skills may link to this one via `references/`
