---
name: workflow-orchestrator
description: >-
  Classify natural-language workflow requests into doc or dev mode and route to the correct downstream workflow skill.
  USE FOR: "now", "워크플로우", "workflow", "어떤 모드", "start work".
  DO NOT USE FOR: direct implementation tasks, standalone documentation edits, simple bug fixes.
---

# Workflow Orchestrator

Classify natural-language workflow requests, then route to `workflow-doc-mode` or `workflow-dev-mode`.

## Decision rules

1. Classify request into `doc` or `dev`.
2. Classify scope: `small`, `medium`, or `large` (choose higher when ambiguous).
3. Check if source-of-truth localization is needed before downstream work.
4. If ambiguous, ask one focused question. Otherwise route in same turn.

### Mode

- `doc`: output is spec, RFC, design, proposal, or planning artifact
- `dev`: output changes code, config, behavior, tests, or execution
- mixed: start `doc` until design and acceptance criteria are stable

### Routing

- documentation-first -> `workflow-doc-mode`
- implementation-first -> `workflow-dev-mode`
- mixed with unstable design -> `workflow-doc-mode`
- mixed with stable design -> `workflow-dev-mode`

### Terminal outcomes (route may refuse)

Not every request routes to a workflow. Name the outcome instead of forcing a fit:

- `need-sot` -> recommend `/prep` first (external SoT not yet localized; doc/dev can't start on unstable requirements)
- `decision` -> owner/product judgment or `superpowers:brainstorming` needed before routing (a blocking decision, not implementation)
- **no-force-fit** — 맞는 nara-kit 스킬/모드가 없으면 직접 실행을 추천하고 억지로 doc/dev 워크플로에 끼워넣지 않는다

## Execution

Active router. Route in same turn when unambiguous. Stop to ask only when mode choice materially changes work.

**Load** [references/routing-details.md](references/routing-details.md) for output contract, examples, stop conditions, and hallucination guards.
