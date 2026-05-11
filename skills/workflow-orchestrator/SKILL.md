---
name: workflow-orchestrator
description: Use when user wants end-to-end workflow routing for software work, from intake through design, planning, TDD, verification, and finish. Best for natural-language requests that should trigger a structured process instead of immediate coding.
version: 0.1.0
---

# Workflow Orchestrator Skill

## Purpose

Classify natural-language workflow requests, then route them to focused doc or dev workflow skills.

<prompt-contract>
Input arrives as natural-language software work request.
Output starts with `### Workflow Intake`, then `### Gate Status`, then `### Next Action` before any routed skill/tool invocation.
Router handles classification and handoff only. Detailed workflow body lives in downstream mode skills.
</prompt-contract>

## Use when

- user asks to "handle this properly", "follow workflow", "take this from requirements to implementation", or similar end-to-end requests
- user says things like "이거 제대로 진행해줘", "설계부터 검증까지 밟아줘", "바로 코딩 말고 절차대로 해줘"
- request needs workflow routing instead of direct ad hoc execution

## Do not use when

- user asks for tiny one-off answer with no workflow expectation
- user explicitly asks for a single isolated action only
- user already chose and invoked a narrower workflow skill for exact next step
- user only wants direct explanation, lookup, or one-shot edit with no workflow routing

## Decision rules

<thinking-sequence>
1. Classify request into `doc` or `dev`.
2. Classify scope into `small`, `medium`, or `large` conservatively.
3. Check whether source-of-truth localization must happen before downstream work.
4. Check whether request is ambiguous enough to require one focused question.
5. Route to `workflow-doc-mode` or `workflow-dev-mode` in same turn when unambiguous.
</thinking-sequence>

### Mode
- `doc`: requested output is spec, RFC, design, proposal, architecture note, or planning artifact
- `dev`: requested output changes code, config, behavior, tests, or system execution
- if request mixes both, start in `doc` until design and acceptance criteria are stable

### Scope
- `small`: bounded change, low integration risk
- `medium`: multiple files or clear integration risk
- `large`: multiple subsystems, high uncertainty, or phased delivery required
- if scope is ambiguous, choose the higher scope conservatively and say why

### Routing table
- documentation-first request -> `workflow-doc-mode`
- implementation-first request -> `workflow-dev-mode`
- mixed request with unstable design -> `workflow-doc-mode`
- mixed request with stable design and explicit implementation ask -> `workflow-dev-mode`

## Output contract

Before routing onward, produce:

### Workflow Intake
- Mode
- Scope
- Reasoning bullets

### Gate Status
- source-of-truth localization status
- mode-specific workflow selection status
- ambiguity status
- handoff readiness status

### Next Action
- exact skill/command to invoke
- why now

## Execution behavior

This skill is an active router.

- If request is documentation-first, invoke `workflow-doc-mode`.
- If request is implementation-first, invoke `workflow-dev-mode`.
- If request is mixed but design is not stable, invoke `workflow-doc-mode` first.
- If request is mixed and implementation-ready, invoke `workflow-dev-mode`.
- Only stop to ask when routing path is genuinely ambiguous.

## Hallucination guards

- If mode is unclear, ask instead of guessing.
- If artifact or implementation intent is unclear, ask one focused question.
- If current environment does not confirm skill or command availability, say `[UNVERIFIED: skill or command availability not confirmed]`.
- If current repo state conflicts with remembered workflow context, trust current repo state and update recommendation.

## Stop conditions

- stop and ask when success criteria are unclear
- stop and ask when `doc` and `dev` are both plausible and choice materially changes work
- stop and ask when required external input or credential is missing
- continue without asking only when route is unambiguous

## Examples

### Example 1
User: `Take this API rate-limit bug from analysis to fix.`
Route: classify `dev` -> `workflow-dev-mode`.

### Example 2
User: `I need a design doc for replacing session storage.`
Route: classify `doc` -> `workflow-doc-mode`.

### Example 3
User: `Plan multi-tenant rollout, then implement it.`
Route: classify mixed request -> start with `workflow-doc-mode`, then hand off to `workflow-dev-mode` after design stabilizes.
