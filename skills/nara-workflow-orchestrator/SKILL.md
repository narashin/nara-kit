---
name: nara-workflow-orchestrator
description: >-
  Classify natural-language workflow requests into doc or dev mode and route to the correct downstream workflow skill.
  USE FOR: "워크플로우", "workflow", "어떤 모드", "doc냐 dev냐", "start work", "이 작업 어떻게 진행".
  DO NOT USE FOR: direct implementation tasks, standalone documentation edits, simple bug fixes.
---

# Workflow Orchestrator

Classify natural-language workflow requests, then route to `nara-workflow-doc-mode` or `nara-workflow-dev-mode`.

## Decision rules

1. Classify request into `doc` or `dev`.
2. Check if source-of-truth localization is needed before downstream work.
3. If ambiguous, ask one focused question. Otherwise route in same turn.

> Scope(small/medium/large) 분류는 여기서 하지 않는다 — `nara-workflow-dev-mode`가 자체 기준으로 산출·소비. orchestrator는 mode(doc/dev)로만 라우팅.

### Mode

- `doc`: output is spec, RFC, design, proposal, or planning artifact
- `dev`: output changes code, config, behavior, tests, or execution
- mixed: start `doc` until design and acceptance criteria are stable

### Routing

- documentation-first -> `nara-workflow-doc-mode`
- implementation-first -> `nara-workflow-dev-mode`
- mixed with unstable design -> `nara-workflow-doc-mode`
- mixed with stable design -> `nara-workflow-dev-mode`

### Terminal outcomes (route may refuse)

Not every request routes to a workflow. Name the outcome instead of forcing a fit:

- `need-sot` -> recommend `/nara-prep` first (external SoT not yet localized; doc/dev can't start on unstable requirements)
- `decision` -> owner/product judgment or `nara-grill` needed before routing (a blocking decision, not implementation)
- **no-force-fit** — 맞는 nara-kit 스킬/모드가 없으면 직접 실행을 추천하고 억지로 doc/dev 워크플로에 끼워넣지 않는다

## Execution

Active router. Route in same turn when unambiguous. Stop to ask only when mode choice materially changes work.

**Load** [references/routing-details.md](references/routing-details.md) for output contract, examples, stop conditions, and hallucination guards.
