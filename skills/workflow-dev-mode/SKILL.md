---
name: workflow-dev-mode
description: Use when request is for code, config, tests, bugfixes, or other behavior-changing implementation workflow.
version: 0.1.0
---

# Workflow Dev Mode

## Purpose

Run implementation-first workflow after router classifies request as `dev`.

<prompt-contract>
Input arrives from top-level router after `dev` classification.
Output starts with `### Workflow Intake`, then `### Gate Status`, then `### Next Action` before any routed skill/tool invocation.
Keep TDD and verification gates explicit for behavior-changing work.
</prompt-contract>

## Use when

- requested output changes code, config, tests, behavior, or runtime execution
- user asks for bugfix, feature, refactor, or implementation delivery
- design intent is already stable enough to enter implementation workflow

## Do not use when

- user only needs a design artifact, RFC, or planning document
- requirements are still too ambiguous for implementation and need doc workflow first
- user wants one-shot explanation only

## Required sequence

1. Confirm implementation goal, scope, and acceptance criteria
2. Localize source-of-truth when requirements are external or scattered
3. Run discovery and clarification before code changes when ambiguity remains
4. Perform integration review against existing code and patterns
5. Run gap analysis when current-state vs target-state delta matters
6. Create written implementation plan before execution
7. Enforce TDD for behavior-changing work where practical
8. Run verification before claiming completion
9. Route to evaluation, review, reflect, ADR, and finish only after prior gates pass

## Decision rules

<thinking-sequence>
1. Confirm request belongs to implementation workflow.
2. Classify scope into `small`, `medium`, or `large` conservatively.
3. Check whether source-of-truth localization is required.
4. Check whether discovery, design clarification, or product framing is still open.
5. Check whether current-state vs target-state delta requires `gap`.
6. Check whether written implementation plan already exists.
7. Check whether TDD is mandatory or explicit exception applies.
8. Choose exact next skill/tool and invoke it in same turn when unambiguous.
</thinking-sequence>

### Scope
- `small`: bounded change, low integration risk
- `medium`: multiple files or clear integration risk
- `large`: multiple subsystems, high uncertainty, or phased delivery required
- if scope is ambiguous, choose higher scope conservatively and say why

### Mandatory routing table
- external or scattered requirements -> `prep`
- design ambiguity -> `ooo interview`
- product framing or option comparison -> `ooo pm`
- design snapshot needed -> `ooo seed`
- current-state vs target-state delta matters -> `gap`
- implementation about to start -> written implementation plan artifact
- phased or broader execution -> `superpowers:subagent-driven-development`
- lighter fallback execution intentionally chosen -> `ooo run`
- inline-style fallback explicitly chosen -> `ooo auto`
- before completion claim -> `ooo evaluate`, then `code-review`
- architectural decision happened -> `adr`
- test scenario discovery needed -> `test-discover`
- existing scenarios need review -> `test-verify`
- work fully verified and branch-ready -> branch finish workflow

## Output contract

Before routing onward, produce:

### Workflow Intake
- Mode: `dev`
- Scope
- Reasoning bullets

### Gate Status
- source-of-truth localization status
- discovery status
- integration review status
- gap status
- planning status
- TDD status
- verification status

### Next Action
- exact skill/command to invoke next
- why now

## Execution behavior

- If external requirements exist, invoke `prep` first.
- If design is not settled enough for code changes, invoke `ooo interview` or hand back to `workflow-doc-mode`.
- If product framing matters, invoke `ooo pm`.
- If design must be snapshotted before implementation, invoke `ooo seed`.
- If gap to current code matters, invoke `gap`.
- If implementation is next, require written implementation plan artifact before code-writing work.
- If execution should proceed, invoke `superpowers:subagent-driven-development` by default.
- Use `ooo run` or `ooo auto` only as intentional fallback execution paths.
- If work reaches completion gates, invoke `ooo evaluate`, then `code-review`, then `reflect`, then `adr` when architecturally relevant, then branch finish workflow.

## Hallucination guards

- If acceptance criteria are missing, do not infer them silently.
- If codebase fit is unknown, inspect before endorsing new abstraction.
- If verification cannot be executed, state missing proof explicitly.
- If automated test is not practical, state why TDD exception applies.
- If workflow gate is skipped by user choice, name skipped gate and risk explicitly.
- If current environment does not confirm skill or command availability, say `[UNVERIFIED: skill or command availability not confirmed]`.

## Stop conditions

- stop and ask when success criteria are unclear
- stop and ask when doc and dev paths are both plausible and materially different
- stop and ask when required external input or credential is missing
- continue without asking only when next implementation gate is unambiguous

## Examples

### Example 1
User: `Fix API rate-limit bug from analysis to code fix.`
Route: dev -> medium -> `ooo interview` -> written implementation plan artifact -> TDD -> `superpowers:subagent-driven-development` -> `ooo evaluate`.

### Example 2
User: `Add audit log export API.`
Route: dev -> `gap` -> written implementation plan artifact -> `superpowers:subagent-driven-development` -> verification.

### Example 3
User: `Implement multi-tenant rollout across services.`
Route: dev -> large -> stronger `ooo interview` / `ooo pm` discovery -> phased plan -> `superpowers:subagent-driven-development`.
