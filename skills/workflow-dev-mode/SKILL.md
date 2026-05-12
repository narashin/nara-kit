---
name: workflow-dev-mode
description: >-
  Run implementation-first workflow enforcing structured gates from SoT localization through gap analysis, TDD, verification, and branch finish.
  USE FOR: "dev mode", "구현 워크플로우", "implementation workflow", "개발 모드", "feature implementation".
  DO NOT USE FOR: documentation-only artifacts, design exploration without stable requirements, simple one-file edits.
---

# Workflow Dev Mode

Run implementation-first workflow after router classifies request as `dev`.

## Use when

- request changes code, config, tests, behavior, or runtime execution
- user asks for bugfix, feature, refactor, or implementation delivery
- design intent is stable enough for implementation workflow

## Do not use when

- user only needs a design artifact, RFC, or planning document
- requirements are too ambiguous for implementation — use doc workflow first

## Decision rules

1. Confirm request belongs to implementation workflow.
2. Classify scope (choose higher when ambiguous):
   - `small`: 1-2 files, single concern, low integration risk
   - `medium`: 3-10 files, single domain, clear integration points
   - `large`: 10+ files, multi-domain, cross-service, or phased delivery
3. Walk gates in order: SoT localization -> discovery -> gap -> plan -> TDD -> verify.
4. Choose next skill/tool and invoke in same turn when unambiguous.

## Core gates

SoT localization -> discovery -> integration review -> gap analysis -> written plan -> TDD -> verification -> evaluate + review -> finish

## Execution

- External requirements exist -> `prep` first (router는 SoT fetch 안 함 — 유저 컨텍스트만으로 판단, fetch는 prep이 담당)
- `prep` Readiness 결과로 분기:
  - READY (4/4) -> `superpowers:brainstorming` -> `gap`
  - PARTIAL (2-3/4) -> `ooo interview` -> `/prep` 재실행
  - INSUFFICIENT (0-1/4) -> `ooo interview` 필수 -> `/prep` 재실행
- Gap to current code matters -> `gap`
- Implementation next -> require written plan before code
- Execution -> `superpowers:subagent-driven-development` (default), `ooo run` / `ooo auto` as fallback
- Completion -> `ooo evaluate` -> `code-review` -> `reflect` -> `adr` if relevant -> branch finish

**Load** [references/dev-workflow-details.md](references/dev-workflow-details.md) for routing table, output contract, examples, and hallucination guards.
