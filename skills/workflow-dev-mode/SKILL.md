---
name: workflow-dev-mode
description: >-
  Run implementation-first workflow enforcing structured gates from SoT localization through gap analysis, TDD, verification, and branch finish.
  USE FOR: "dev mode", "구현 워크플로우", "implementation workflow", "개발 모드", "feature implementation".
  DO NOT USE FOR: documentation-only artifacts (→ workflow-doc-mode), design exploration without stable requirements (→ ooo interview or superpowers:brainstorming), simple one-file edits (→ direct edit).
---

# Workflow Dev Mode

Implementation-first workflow (router classifies `dev`).

## Use when

bugfix / feature / refactor / impl delivery, 코드·설정·테스트 변경, design stable.

## Decision rules

1. Confirm implementation workflow.
2. Classify scope (모호 시 상향): `small` (1-2 files, single concern) / `medium` (3-10 files, single domain) / `large` (10+ files, multi-domain).
3. Walk gates: SoT -> discovery -> gap -> plan -> pre-execution -> TDD -> verify.

## Execution

- External req -> `prep` (SoT fetch)
- Readiness 4/4 -> `superpowers:brainstorming` -> `gap`; 2-3/4 -> `ooo interview` -> `/prep`; 0-1/4 -> `ooo interview` 필수
- `backlog/` + Level 1 -> `/backlog decompose`. 없으면 `gap` full
- plan per subtask -> Pre-execution gate -> execute
- Execute: `superpowers:SDD` default, `ooo run`/`auto` fallback
- Subtask 완료 -> `/backlog done` (auto-verify)
- 완료 -> `ooo evaluate` -> `code-review` -> `reflect` -> `adr` -> branch finish

## Gates

- Pre-execution: plan + AskUserQuestion 승인 ([상세](references/pre-execution-gate.md))
- Component Pick: 카탈로그 5단계 ([상세](references/component-pick-procedure.md))

AskUserQuestion은 Pre-execution gate에만. 라우팅/분기는 평문.

**Load** [references/dev-workflow-details.md](references/dev-workflow-details.md) for routing table, output contract, examples, hallucination guards.
